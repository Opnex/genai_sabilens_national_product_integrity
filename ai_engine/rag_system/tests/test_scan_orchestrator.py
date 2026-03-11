"""
ai_engine/tests/test_scan_orchestrator.py
Tests for ScanOrchestrator — your RAG system's internal orchestrator.

Covers:
  - All regulatory verdict paths (VERIFIED, EXPIRED, NOT_FOUND, MISMATCH, NEAR_EXPIRY)
  - VerificationResult shape and field values
  - Reasoning trace passthrough
  - explain() output format

No ChromaDB, no model, no server required — the regulatory agent is mocked.
"""

import pytest
from unittest.mock import MagicMock
from ai_engine.orchestrator.scan_orchestrator import ScanOrchestrator
from ai_engine.orchestrator.pipeline          import VerificationResult


# ── Verdict mock factory ───────────────────────────────────────────────────────

def _make_verdict(
    status      : str   = "VERIFIED",
    score       : float = 1.0,
    severity    : str   = "NONE",
    verified    : bool  = True,
    near_expiry : bool  = False,
    fallback    : bool  = False,
    tools       : list  = None,
):
    """Build a minimal AgentVerdict mock — mirrors what NAFDACVerificationAgent.verify() returns."""
    v = MagicMock()
    v.verified            = verified
    v.verification_score  = score
    v.status_code         = status
    v.severity            = severity
    v.summary             = f"Test summary ({status})"
    v.detail              = f"Test detail ({status})"
    v.matched_record      = {
        "product_name"   : "KELLOGG'S CORN FLAKES",
        "nafdac_no_clean": "A8-4114",
        "subcategory"    : "Cereals and Cereal Products",
        "applicant_name" : "KELLOGG TOLARAM NIGERIA LIMTED",
        "expiry_date_iso": "2029-07-30",
    } if verified else None
    v.expiry_check        = {
        "is_valid"      : True,
        "is_near_expiry": near_expiry,
        "severity"      : "WARNING" if near_expiry else "NONE",
        "message"       : "Expires soon." if near_expiry else "Valid.",
    }
    v.alignment           = {"is_match": True, "severity": "NONE"}
    v.reasoning_trace     = [
        MagicMock(
            thought             = "Look up the NAFDAC number.",
            action              = "lookup_nafdac",
            action_input        = {"nafdac_no": "A8-4114"},
            observation_summary = "Found 1 record.",
        ),
    ]
    v.tools_called        = tools or ["lookup_nafdac", "check_expiry", "check_alignment"]
    v.fallback_used       = fallback
    return v


def _make_orchestrator(verdict_mock) -> ScanOrchestrator:
    """Return a ScanOrchestrator with its regulatory agent replaced by a mock."""
    orc = ScanOrchestrator.__new__(ScanOrchestrator)   # skip __init__ — avoids loading ChromaDB
    orc._regulatory_agent = MagicMock()
    orc._regulatory_agent.verify.return_value = verdict_mock
    return orc


# ═══════════════════════════════════════════════════════════════════
# Class 1 — Verdict paths
# ═══════════════════════════════════════════════════════════════════

class TestVerdictPaths:
    """All six regulatory status codes produce the right VerificationResult."""

    def test_verified(self):
        orc    = _make_orchestrator(_make_verdict("VERIFIED", 1.0, "NONE", verified=True))
        result = orc.verify("A8-4114", "corn flakes")
        assert result.status_code         == "VERIFIED"
        assert result.verified            is True
        assert result.verification_score  == 1.0
        assert result.severity            == "NONE"

    def test_verified_near_expiry(self):
        orc    = _make_orchestrator(_make_verdict("VERIFIED_NEAR_EXPIRY", 0.85, "WARNING", verified=True, near_expiry=True))
        result = orc.verify("01-0132", "tea")
        assert result.status_code         == "VERIFIED_NEAR_EXPIRY"
        assert result.verified            is True
        assert result.verification_score  == 0.85
        assert result.severity            == "WARNING"

    def test_expired(self):
        orc    = _make_orchestrator(_make_verdict("EXPIRED", 0.1, "HIGH", verified=False))
        result = orc.verify("A8-4114", "cereal")
        assert result.status_code         == "EXPIRED"
        assert result.verified            is False
        assert result.verification_score  == 0.1
        assert result.severity            == "HIGH"

    def test_not_found(self):
        orc    = _make_orchestrator(_make_verdict("NOT_FOUND", 0.0, "CRITICAL", verified=False))
        result = orc.verify("FAKE-9999", "cereal")
        assert result.status_code         == "NOT_FOUND"
        assert result.verified            is False
        assert result.verification_score  == 0.0
        assert result.severity            == "CRITICAL"

    def test_subcategory_mismatch(self):
        orc    = _make_orchestrator(_make_verdict("SUBCATEGORY_MISMATCH", 0.2, "CRITICAL", verified=False))
        result = orc.verify("A8-4114", "cosmetics")
        assert result.status_code         == "SUBCATEGORY_MISMATCH"
        assert result.verified            is False
        assert result.verification_score  == 0.2
        assert result.severity            == "CRITICAL"

    def test_agent_error(self):
        orc    = _make_orchestrator(_make_verdict("AGENT_ERROR", 0.0, "CRITICAL", verified=False))
        result = orc.verify("A8-4114", "cereal")
        assert result.status_code         == "AGENT_ERROR"
        assert result.verified            is False
        assert result.verification_score  == 0.0


# ═══════════════════════════════════════════════════════════════════
# Class 2 — VerificationResult shape
# ═══════════════════════════════════════════════════════════════════

class TestVerificationResultShape:
    """The VerificationResult returned by verify() has the right structure."""

    def _result(self):
        orc = _make_orchestrator(_make_verdict())
        return orc.verify("A8-4114", "corn flakes")

    def test_returns_verification_result(self):
        assert isinstance(self._result(), VerificationResult)

    def test_nafdac_no_echoed(self):
        assert self._result().nafdac_no == "A8-4114"

    def test_scanned_category_echoed(self):
        assert self._result().scanned_category == "corn flakes"

    def test_summary_is_string(self):
        assert isinstance(self._result().summary, str)

    def test_detail_is_string(self):
        assert isinstance(self._result().detail, str)

    def test_matched_record_present_on_verified(self):
        result = self._result()
        assert result.matched_record is not None
        assert result.matched_record["product_name"] == "KELLOGG'S CORN FLAKES"

    def test_matched_record_none_on_not_found(self):
        orc    = _make_orchestrator(_make_verdict("NOT_FOUND", 0.0, "CRITICAL", verified=False))
        result = orc.verify("FAKE-9999", "cereal")
        assert result.matched_record is None

    def test_expiry_check_present(self):
        assert self._result().expiry_check is not None

    def test_alignment_present(self):
        assert self._result().alignment is not None

    def test_tools_called_is_list(self):
        assert isinstance(self._result().tools_called, list)

    def test_fallback_used_is_bool(self):
        assert isinstance(self._result().fallback_used, bool)


# ═══════════════════════════════════════════════════════════════════
# Class 3 — Reasoning trace
# ═══════════════════════════════════════════════════════════════════

class TestReasoningTrace:
    """The reasoning trace from the agent is passed through correctly."""

    def test_trace_is_list(self):
        orc    = _make_orchestrator(_make_verdict())
        result = orc.verify("A8-4114", "cereal")
        assert isinstance(result.reasoning_trace, list)

    def test_trace_step_has_required_keys(self):
        orc    = _make_orchestrator(_make_verdict())
        result = orc.verify("A8-4114", "cereal")
        step   = result.reasoning_trace[0]
        assert "thought"             in step
        assert "action"              in step
        assert "action_input"        in step
        assert "observation_summary" in step

    def test_trace_step_action_is_correct(self):
        orc    = _make_orchestrator(_make_verdict())
        result = orc.verify("A8-4114", "cereal")
        assert result.reasoning_trace[0]["action"] == "lookup_nafdac"

    def test_tools_called_matches_expected_sequence(self):
        orc    = _make_orchestrator(_make_verdict(tools=["lookup_nafdac", "check_expiry", "check_alignment"]))
        result = orc.verify("A8-4114", "cereal")
        assert result.tools_called == ["lookup_nafdac", "check_expiry", "check_alignment"]

    def test_fallback_used_false_on_clean_scan(self):
        orc    = _make_orchestrator(_make_verdict(fallback=False))
        result = orc.verify("A8-4114", "cereal")
        assert result.fallback_used is False

    def test_fallback_used_true_when_semantic_search_needed(self):
        orc    = _make_orchestrator(_make_verdict(fallback=True, tools=["lookup_nafdac", "semantic_search", "check_expiry", "check_alignment"]))
        result = orc.verify("A8-4114", "cereal")
        assert result.fallback_used is True


# ═══════════════════════════════════════════════════════════════════
# Class 4 — explain()
# ═══════════════════════════════════════════════════════════════════

class TestExplain:
    """explain() produces a readable plain-text report."""

    def _explain(self):
        orc = _make_orchestrator(_make_verdict())
        return orc.explain("A8-4114", "corn flakes")

    def test_returns_string(self):
        assert isinstance(self._explain(), str)

    def test_contains_nafdac_no(self):
        assert "A8-4114" in self._explain()

    def test_contains_scanned_category(self):
        assert "corn flakes" in self._explain()

    def test_contains_status_code(self):
        assert "VERIFIED" in self._explain()

    def test_contains_tool_sequence(self):
        assert "lookup_nafdac" in self._explain()

    def test_contains_matched_product_name(self):
        assert "KELLOGG'S CORN FLAKES" in self._explain()

    def test_explain_on_not_found_has_no_matched_record_section(self):
        orc    = _make_orchestrator(_make_verdict("NOT_FOUND", 0.0, "CRITICAL", verified=False))
        output = orc.explain("FAKE-9999", "cereal")
        assert "MATCHED RECORD" not in output
