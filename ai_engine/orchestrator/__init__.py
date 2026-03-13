"""
ai_engine/orchestrator/scan_orchestrator.py
Coordinates A1, A2, A3, and A4 for every product label scan in SabiLens.
D1 Backend creates one ScanOrchestrator instance at startup and calls scan() per request.
"""

from ai_engine.agent.verification_agent import NAFDACVerificationAgent
from ai_engine.orchestrator.pipeline    import (
    AgentSignal, PipelineResult,
    SIGNAL_WEIGHTS, MOCK_CONFIDENCE,
    THRESHOLD_AUTHENTIC, THRESHOLD_SUSPICIOUS, CRITICAL_STATUSES,
)


class ScanOrchestrator:
    """
    Runs all four agents in sequence for one product scan and returns a fused verdict.

    Call sequence per scan:
        A2 (OCR) → A3 (NAFDAC verification) → A1 (vision) → A4 (fusion)

    A1 and A2 are mocked at 0.80 confidence until those modules are integrated.
    Pass real confidence values once they are ready — no other code changes needed.

    Usage:
        orchestrator = ScanOrchestrator()                   # once at startup

        result = orchestrator.scan("A8-4114", "corn flakes")
        print(result.final_verdict)  # AUTHENTIC
        print(result.final_score)    # 0.88

        # Once A1 and A2 are integrated:
        result = orchestrator.scan(
            nafdac_no        = "A8-4114",
            scanned_category = "corn flakes",
            a1_confidence    = 0.93,
            a2_confidence    = 0.91,
        )

        # Full plain-text reasoning trace for demos and D5 audit panel:
        print(orchestrator.explain("A8-4114", "corn flakes"))
    """

    def __init__(self):
        self._a3_agent = NAFDACVerificationAgent()  # loads ChromaDB and sentence-transformer once at startup

    def scan(
        self,
        nafdac_no:        str,
        scanned_category: str,
        a1_confidence:    float | None = None,  # real A1 visual confidence; None → mocked at 0.80
        a2_confidence:    float | None = None,  # real A2 OCR confidence;    None → mocked at 0.80
    ) -> PipelineResult:
        """
        Run all agents in pipeline order and return a complete PipelineResult.

        A3 CRITICAL verdicts (NOT_FOUND, SUBCATEGORY_MISMATCH) bypass the
        weighted fusion formula and immediately set the verdict to FAKE.
        """
        a2 = self._run_a2(nafdac_no, a2_confidence)         # step 1 — collect OCR signal
        a3 = self._run_a3(nafdac_no, scanned_category)      # step 2 — regulatory verification
        a1 = self._run_a1(scanned_category, a1_confidence)  # step 3 — collect visual signal
        a4 = self._run_a4(a1, a2, a3)                       # step 4 — fuse all three signals

        return PipelineResult(
            a1             = a1,
            a2             = a2,
            a3             = a3,
            a4             = a4,
            final_verdict  = a4.payload["verdict"],
            final_score    = a4.payload["fused_score"],
            final_severity = a4.payload["severity"],
            summary        = a4.payload["summary"],   # forwarded from A3 — one-line verdict
            detail         = a4.payload["detail"],    # forwarded from A3 — full sentence for D6
            signals_used   = [                        # only include agents that had non-zero weight
                agent_id for agent_id in ["A1", "A2", "A3"]
                if a4.payload["signal_breakdown"][agent_id.lower()]["weight"] > 0
            ],
        )

    # ── Agent runners ──────────────────────────────────────────────────────────
    # Each runner returns one AgentSignal with a standardised confidence and payload.
    # When a module is not yet integrated, mocked=True and confidence=MOCK_CONFIDENCE.

    def _run_a2(self, nafdac_no: str, real_confidence: float | None) -> AgentSignal:
        """Collect the A2 OCR signal. Returns a mock signal until A2 module is integrated."""
        mocked     = real_confidence is None
        confidence = MOCK_CONFIDENCE if mocked else real_confidence
        return AgentSignal(
            agent_id   = "A2",
            available  = True,
            confidence = confidence,
            mocked     = mocked,
            payload    = {
                "ocr_confidence": confidence,
                "raw_nafdac_no" : nafdac_no,  # passed through unchanged to A3
            },
        )

    def _run_a3(self, nafdac_no: str, scanned_category: str) -> AgentSignal:
        """
        Run the A3 NAFDACVerificationAgent ReAct loop and package the result as an AgentSignal.
        This is always a real call — A3 is never mocked.
        """
        verdict = self._a3_agent.verify(nafdac_no, scanned_category)  # runs lookup → expiry → alignment
        return AgentSignal(
            agent_id   = "A3",
            available  = True,
            confidence = verdict.verification_score,  # 0.0 (NOT_FOUND) to 1.0 (VERIFIED)
            mocked     = False,
            payload    = {
                "verification_score": verdict.verification_score,
                "status_code"       : verdict.status_code,   # VERIFIED | EXPIRED | NOT_FOUND | SUBCATEGORY_MISMATCH
                "severity"          : verdict.severity,       # NONE | WARNING | HIGH | CRITICAL
                "verified"          : verdict.verified,
                "summary"           : verdict.summary,
                "detail"            : verdict.detail,
                "matched_record"    : verdict.matched_record,  # full DB record or None
                "expiry_check"      : verdict.expiry_check,    # expiry layer result dict
                "alignment"         : verdict.alignment,       # category match layer result dict
                "reasoning_trace"   : [                        # each step the ReAct engine took
                    {
                        "thought"            : step.thought,
                        "action"             : step.action,
                        "action_input"       : step.action_input,
                        "observation_summary": step.observation_summary,
                    }
                    for step in verdict.reasoning_trace
                ],
                "tools_called" : verdict.tools_called,   # e.g. ["lookup_nafdac", "check_expiry", "check_alignment"]
                "fallback_used": verdict.fallback_used,  # True if semantic search was needed
            },
        )

    def _run_a1(self, scanned_category: str, real_confidence: float | None) -> AgentSignal:
        """Collect the A1 vision signal. Returns a mock signal until A1 module is integrated."""
        mocked     = real_confidence is None
        confidence = MOCK_CONFIDENCE if mocked else real_confidence
        return AgentSignal(
            agent_id   = "A1",
            available  = True,
            confidence = confidence,
            mocked     = mocked,
            payload    = {
                "visual_confidence": confidence,
                "detected_category": scanned_category,  # placeholder until A1 classifies the image
            },
        )

    def _run_a4(self, a1: AgentSignal, a2: AgentSignal, a3: AgentSignal) -> AgentSignal:
        """
        Fuse A1, A2, and A3 signals into a final verdict using weighted scoring.

        If A3 returns a CRITICAL status (NOT_FOUND or SUBCATEGORY_MISMATCH), the
        weighted formula is bypassed entirely and the verdict is forced to FAKE.
        This prevents high A1/A2 confidence from masking a definitive fake signal.
        """
        a3_status = a3.payload["status_code"]

        if a3_status in CRITICAL_STATUSES:
            # Critical override path — A3 has definitive evidence, no formula needed
            fused_score = a3.confidence  # 0.0 for NOT_FOUND, 0.2 for SUBCATEGORY_MISMATCH
            verdict     = "FAKE"
            severity    = "CRITICAL"
            summary     = a3.payload["summary"]
            detail      = a3.payload["detail"]
            breakdown   = {
                "a3": {"score": a3.confidence, "weight": 1.0},  # full weight to A3 on override
                "a1": {"score": a1.confidence, "weight": 0.0},  # zeroed to signal override was applied
                "a2": {"score": a2.confidence, "weight": 0.0},
            }

        else:
            # Normal fusion path — weighted average of all three signals
            weights     = dict(SIGNAL_WEIGHTS)  # copy so we don't mutate the module constant
            scores      = {"A3": a3.confidence, "A1": a1.confidence, "A2": a2.confidence}
            total_w     = sum(weights[k] for k in scores)  # always 1.0, but safe against future changes
            fused_score = round(
                sum((weights[k] / total_w) * scores[k] for k in scores), 4
            )

            if fused_score >= THRESHOLD_AUTHENTIC:
                verdict  = "AUTHENTIC"
                severity = a3.payload.get("severity", "NONE")  # preserve WARNING if near-expiry
            elif fused_score >= THRESHOLD_SUSPICIOUS:
                verdict  = "SUSPICIOUS"
                severity = "WARNING"
            else:
                verdict  = "FAKE"
                severity = "HIGH"

            summary   = a3.payload["summary"]
            detail    = a3.payload["detail"]
            breakdown = {
                "a3": {"score": a3.confidence, "weight": round(weights["A3"] / total_w, 4)},
                "a1": {"score": a1.confidence, "weight": round(weights["A1"] / total_w, 4)},
                "a2": {"score": a2.confidence, "weight": round(weights["A2"] / total_w, 4)},
            }

        return AgentSignal(
            agent_id   = "A4",
            available  = True,
            confidence = fused_score,
            mocked     = False,
            payload    = {
                "verdict"          : verdict,
                "fused_score"      : fused_score,
                "severity"         : severity,
                "summary"          : summary,
                "detail"           : detail,
                "override_applied" : a3_status in CRITICAL_STATUSES,  # True when fusion was bypassed
                "signal_breakdown" : breakdown,   # per-agent score and weight for D5 audit display
                "a1_mocked"        : a1.mocked,   # tells D5 which signals were real vs placeholder
                "a2_mocked"        : a2.mocked,
            },
        )

    # ── Developer utility ──────────────────────────────────────────────────────

    def explain(self, nafdac_no: str, scanned_category: str) -> str:
        """
        Run a full scan and return a formatted plain-text report.
        Shows the A3 reasoning trace and A4 fusion breakdown in one readable block.
        Useful for instructor demos, rag_query.py, and the D5 audit panel.
        """
        result   = self.scan(nafdac_no, scanned_category)
        a3_trace = result.a3.payload.get("reasoning_trace", [])
        bd       = result.a4.payload["signal_breakdown"]

        lines = [
            "",
            "SABILENS SCAN — Orchestrator Report",
            "=" * 60,
            f"NAFDAC      : {nafdac_no}",
            f"Category    : {scanned_category}",
            f"Signals     : A1={'mocked' if result.a1.mocked else 'real'}"
            f"  A2={'mocked' if result.a2.mocked else 'real'}"
            f"  A3=real",
            "",
            "A3 AGENT REASONING",
            "-" * 40,
        ]
        for i, step in enumerate(a3_trace, 1):
            lines += [
                f"  Step {i} | {step['action']}",
                f"    Thought : {step['thought']}",
                f"    Result  : {step['observation_summary']}",
                "",
            ]
        lines += [
            "FUSION RESULT (A4)",
            "-" * 40,
            f"  A3 : score={result.a3.confidence}  weight={bd['a3']['weight']}",
            f"  A1 : score={result.a1.confidence}  weight={bd['a1']['weight']}",
            f"  A2 : score={result.a2.confidence}  weight={bd['a2']['weight']}",
            f"  Override applied : {result.a4.payload['override_applied']}",
            "",
            "FINAL VERDICT",
            "-" * 40,
            f"  Verdict  : {result.final_verdict}",
            f"  Score    : {result.final_score}",
            f"  Severity : {result.final_severity}",
            f"  Summary  : {result.summary}",
            "",
        ]
        return "\n".join(lines)