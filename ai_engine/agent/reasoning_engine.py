"""
agent/reasoning_engine.py
Rule-based ReAct (Reason + Act) engine for NAFDAC product verification.
Each run cycles through Thought → Action → Observe steps until a verdict is reached.THE DECISION TREE
  START
    │
    ├─ NAFDAC number provided?
    │     YES → Action: lookup_nafdac
    │              ├─ Found?  YES → Action: check_expiry
    │              │                   ├─ Expired?  YES → STOP: EXPIRED
    │              │                   └─ Valid?    YES → Action: check_alignment
    │              │                                         ├─ Mismatch? → STOP: SUBCATEGORY_MISMATCH
    │              │                                         └─ Match?    → STOP: VERIFIED
    │              │
    │              └─ Not Found? → Action: semantic_search (fallback)
    │                                 ├─ Candidate found? → re-run with candidate NAFDAC
    │                                 └─ No match?        → STOP: NOT_FOUND
    │
    └─ No NAFDAC (text only) → Action: semantic_search directly

OBSERVATION LOG
  Every Thought/Action/Observe step is appended to self.steps so the caller
  can return a full reasoning trace to D5 (dashboard) and the A4 audit trail.
"""

from dataclasses import dataclass, field
from typing      import Optional


@dataclass
class ReActStep:
    """One Thought-Action-Observe cycle recorded during a verification run."""
    thought:             str   # why this tool was chosen
    action:              str   # name of the tool that was called
    action_input:        dict  # arguments passed to the tool
    observation:         any   # raw return value from the tool
    observation_summary: str   # one-line human-readable summary of the result


@dataclass
class AgentVerdict:
    """Final verdict produced by the ReAct loop, consumed by agent_scorer and routes.py."""
    verified:           bool
    verification_score: float
    status_code:        str
    severity:           str
    summary:            str
    detail:             str
    expiry_check:       Optional[dict]
    alignment:          Optional[dict]
    matched_record:     Optional[dict]
    all_records:        list
    reasoning_trace:    list = field(default_factory=list)  # ordered list of ReActStep
    tools_called:       list = field(default_factory=list)  # tool names in call order
    fallback_used:      bool = False                        # True when semantic search was the entry point


# Verification score constants — same values as regulatory_scorer.py
SCORE_VERIFIED             = 1.0   # all checks passed
SCORE_SUBCATEGORY_MISMATCH = 0.2   # valid number, wrong product type
SCORE_EXPIRED              = 0.1   # registration has lapsed
SCORE_EXPIRING_SOON        = 0.85  # valid but expiry within 60 days
SCORE_NOT_FOUND            = 0.0   # number not in database


class NAFDACReasoningEngine:
    """
    Orchestrates the five verification tools in a rule-based ReAct loop.

    Decision path:
      lookup_nafdac → [not found → semantic_search fallback]
      → check_expiry → check_alignment → [mismatch → browse_category for context]
      → verdict
    """

    def __init__(self, tools: dict):
        """
        Args:
            tools: dict from build_tools() — keys are tool names, values are FunctionTools.
        """
        self.tools = tools
        self.steps: list[ReActStep] = []  # reset per run

    def run(self, nafdac_no: str, scanned_category: str) -> AgentVerdict:
        """Run the full ReAct loop for one scan and return an AgentVerdict."""
        self.steps = []                                   # clear trace from any previous run
        nafdac_no  = nafdac_no.strip()

        records = self._act_lookup_nafdac(nafdac_no)      # step 1: exact NAFDAC lookup

        fallback_used = False
        if not records:                                   # step 2: fallback to semantic search if not found
            fallback_used = True
            records, nafdac_no = self._act_semantic_fallback(nafdac_no, scanned_category)

        if not records:                                   # still nothing — stop here
            return self._verdict_not_found(nafdac_no, fallback_used=fallback_used)

        best         = self._pick_best_record(records, scanned_category)  # prefer category-matching record
        expiry_check = self._act_check_expiry(best)       # step 3: check expiry date

        if not expiry_check["is_valid"]:                  # expired — stop before alignment
            return self._verdict_expired(nafdac_no, best, records, expiry_check, fallback_used)

        alignment = self._act_check_alignment(scanned_category, best)  # step 4: category match

        if not alignment["is_match"]:                     # mismatch — gather context then stop
            self._act_browse_for_context(alignment["scanned_norm"])
            return self._verdict_mismatch(nafdac_no, best, records, expiry_check, alignment, fallback_used)

        return self._verdict_verified(nafdac_no, best, records, expiry_check, alignment, fallback_used)

    # ── Action methods — each records one ReActStep ────────────────────────────

    def _act_lookup_nafdac(self, nafdac_no: str) -> list:
        """Call lookup_nafdac tool and record the step."""
        records = self.tools["lookup_nafdac"].fn(nafdac_no)
        obs_summary = (
            f"Found {len(records)} record(s). Best: '{records[0].get('product_name','?')}' ({records[0].get('subcategory','?')})."
            if records else
            f"'{nafdac_no}' not found in database."
        )
        self.steps.append(ReActStep(
            thought             = f"Look up NAFDAC number '{nafdac_no}' in the registered product database.",
            action              = "lookup_nafdac",
            action_input        = {"nafdac_no": nafdac_no},
            observation         = records,
            observation_summary = obs_summary,
        ))
        return records

    def _act_semantic_fallback(self, nafdac_no: str, scanned_category: str) -> tuple[list, str]:
        """Call semantic_search as fallback and return (records, resolved_nafdac)."""
        search_text = f"{nafdac_no} {scanned_category}".strip()
        candidates  = self.tools["semantic_search"].fn(search_text, 3)  # top 3 candidates

        if candidates:
            top              = candidates[0]
            resolved_nafdac  = top["metadata"].get("nafdac_no_clean", nafdac_no)  # use candidate's NAFDAC
            resolved_name    = top["metadata"].get("product_name", "Unknown")
            self.steps.append(ReActStep(
                thought             = f"Exact lookup failed for '{nafdac_no}'. Trying semantic search with label text.",
                action              = "semantic_search",
                action_input        = {"product_text": search_text},
                observation         = candidates,
                observation_summary = f"Top candidate: '{resolved_name}' (similarity={top['similarity_score']:.2f}). Re-running lookup with '{resolved_nafdac}'.",
            ))
            resolved_records = self.tools["lookup_nafdac"].fn(resolved_nafdac)  # exact lookup with resolved number
            return resolved_records, resolved_nafdac
        else:
            self.steps.append(ReActStep(
                thought             = f"Exact lookup failed for '{nafdac_no}'. Trying semantic search with label text.",
                action              = "semantic_search",
                action_input        = {"product_text": search_text},
                observation         = [],
                observation_summary = "No candidates found above similarity threshold.",
            ))
            return [], nafdac_no

    def _act_check_expiry(self, record: dict) -> dict:
        """Call check_expiry tool and record the step."""
        expiry_iso = record.get("expiry_date_iso", "")    # pull expiry date from matched record
        result     = self.tools["check_expiry"].fn(expiry_iso)
        self.steps.append(ReActStep(
            thought             = f"Record found. Checking whether registration is still valid (expiry: '{expiry_iso}').",
            action              = "check_expiry",
            action_input        = {"expiry_date_iso": expiry_iso},
            observation         = result,
            observation_summary = result["message"],
        ))
        return result

    def _act_check_alignment(self, scanned_category: str, record: dict) -> dict:
        """Call check_alignment tool and record the step."""
        registered = record.get("subcategory", "Unknown")  # official category from DB record
        result     = self.tools["check_alignment"].fn(scanned_category, registered)
        obs_summary = (
            f"Match: '{result['scanned_norm']}' aligns with '{result['registered_norm']}'."
            if result["is_match"] else
            f"MISMATCH: scanned='{result['scanned_norm']}' vs registered='{result['registered_norm']}'."
        )
        self.steps.append(ReActStep(
            thought             = f"Registration valid. Checking whether scanned type '{scanned_category}' matches registered category '{registered}'.",
            action              = "check_alignment",
            action_input        = {"scanned_subcategory": scanned_category, "registered_subcategory": registered},
            observation         = result,
            observation_summary = obs_summary,
        ))
        return result

    def _act_browse_for_context(self, scanned_norm: str) -> list:
        """Browse the scanned category after a mismatch to confirm no better match exists."""
        # resolve via relative package path so the module is found
        from ai_engine.rag_system.retrieval.subcategory_alignment import normalize_subcategory
        canonical = normalize_subcategory(scanned_norm)           # resolve alias to DB canonical name
        results   = self.tools["browse_category"].fn(canonical) if canonical else []
        self.steps.append(ReActStep(
            thought             = f"Mismatch detected. Browsing '{canonical}' products to confirm no legitimate match for this NAFDAC number.",
            action              = "browse_category",
            action_input        = {"subcategory": canonical},
            observation         = results,
            observation_summary = f"Found {len(results)} '{canonical}' product(s). None share this NAFDAC number.",
        ))
        return results

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _pick_best_record(self, records: list, scanned_subcategory: str) -> dict:
        """Return the record whose category best matches the scanned type; fall back to first."""
        if len(records) == 1:
            # only one record available, nothing to compare
            return records[0]

        # resolve via relative package path so the module is found
        from ai_engine.rag_system.retrieval.subcategory_alignment import normalize_subcategory
        scanned_norm = normalize_subcategory(scanned_subcategory)

        for r in records:
            if normalize_subcategory(r.get("subcategory", "")) == scanned_norm:
                return r
        return records[0]  # no category match — default to earliest record

    def _tools_called(self) -> list:
        """Return ordered list of tool names called in this run."""
        return [s.action for s in self.steps]

    # ── Verdict builders ───────────────────────────────────────────────────────

    def _verdict_not_found(self, nafdac_no: str, fallback_used: bool) -> AgentVerdict:
        """Build NOT_FOUND verdict when both lookup and semantic fallback returned nothing."""
        return AgentVerdict(
            verified             = False,
            verification_score   = SCORE_NOT_FOUND,
            status_code          = "NOT_FOUND",
            severity             = "CRITICAL",
            summary              = f"NAFDAC number '{nafdac_no}' not found in the database.",
            detail               = (
                f"The NAFDAC number '{nafdac_no}' does not exist in the registered product database."
                + (" A semantic search was also attempted but found no candidates." if fallback_used else "")
                + " Do not purchase this product."
            ),
            expiry_check         = None,
            alignment            = None,
            matched_record       = None,
            all_records          = [],
            reasoning_trace      = self.steps,
            tools_called         = self._tools_called(),
            fallback_used        = fallback_used,
        )

    def _verdict_expired(self, nafdac_no, best, records, expiry_check, fallback_used) -> AgentVerdict:
        """Build EXPIRED verdict when the registration date has passed."""
        product_name = best.get("product_name", "Unknown")
        applicant    = best.get("applicant_name", "Unknown")
        return AgentVerdict(
            verified             = False,
            verification_score   = SCORE_EXPIRED,
            status_code          = "EXPIRED",
            severity             = "HIGH",
            summary              = f"Registration for '{product_name}' has expired.",
            detail               = f"NAFDAC number '{nafdac_no}' belongs to '{product_name}' by '{applicant}'. {expiry_check['message']} Do not purchase this product.",
            expiry_check         = expiry_check,
            alignment            = None,
            matched_record       = best,
            all_records          = records,
            reasoning_trace      = self.steps,
            tools_called         = self._tools_called(),
            fallback_used        = fallback_used,
        )

    def _verdict_mismatch(self, nafdac_no, best, records, expiry_check, alignment, fallback_used) -> AgentVerdict:
        """Build SUBCATEGORY_MISMATCH verdict when the NAFDAC number belongs to a different product type."""
        product_name   = best.get("product_name", "Unknown")
        applicant      = best.get("applicant_name", "Unknown")
        registered_cat = best.get("subcategory", "Unknown")
        return AgentVerdict(
            verified             = False,
            verification_score   = SCORE_SUBCATEGORY_MISMATCH,
            status_code          = "SUBCATEGORY_MISMATCH",
            severity             = "CRITICAL",
            summary              = f"NAFDAC '{nafdac_no}' registered for '{registered_cat}', not '{alignment['scanned_norm']}'.",
            detail               = (
                f"CRITICAL: NAFDAC number '{nafdac_no}' belongs to '{product_name}' ({registered_cat}) by '{applicant}'. "
                f"The scanned product appears to be '{alignment['scanned_norm']}'. "
                f"This NAFDAC number has been misused on a different product type. Do not buy."
            ),
            expiry_check         = expiry_check,
            alignment            = alignment,
            matched_record       = best,
            all_records          = records,
            reasoning_trace      = self.steps,
            tools_called         = self._tools_called(),
            fallback_used        = fallback_used,
        )

    def _verdict_verified(self, nafdac_no, best, records, expiry_check, alignment, fallback_used) -> AgentVerdict:
        """Build VERIFIED (or VERIFIED_NEAR_EXPIRY) verdict when all checks pass."""
        product_name   = best.get("product_name", "Unknown")
        applicant      = best.get("applicant_name", "Unknown")
        registered_cat = best.get("subcategory", "Unknown")
        near_expiry    = expiry_check.get("is_near_expiry", False)

        score       = SCORE_EXPIRING_SOON if near_expiry else SCORE_VERIFIED   # penalise score slightly if near expiry
        status_code = "VERIFIED_NEAR_EXPIRY" if near_expiry else "VERIFIED"
        severity    = "WARNING" if near_expiry else "NONE"
        expiry_note = f"  Note: {expiry_check['message']}" if near_expiry else ""

        return AgentVerdict(
            verified             = True,
            verification_score   = score,
            status_code          = status_code,
            severity             = severity,
            summary              = f"'{product_name}' is a valid, registered NAFDAC product.",
            detail               = f"Verification passed. '{product_name}' by '{applicant}' is a registered {registered_cat} product (NAFDAC No: {nafdac_no}).{expiry_note}",
            expiry_check         = expiry_check,
            alignment            = alignment,
            matched_record       = best,
            all_records          = records,
            reasoning_trace      = self.steps,
            tools_called         = self._tools_called(),
            fallback_used        = fallback_used,
        )
