"""
tests/test_verification_agent.py
Tests for NAFDACVerificationAgent and NAFDACReasoningEngine.
All tools are mocked — no ChromaDB or embedding model required to run the suite.
"""

import pytest
from unittest.mock import MagicMock, patch
from agent.reasoning_engine import NAFDACReasoningEngine, AgentVerdict
from agent.agent_scorer     import compute_verification_score, _verdict_to_dict


# ── Real data fixtures ────────────────────────────────────────────────────────

CORN_FLAKES_RECORD = {
    "product_name"    : "KELLOGG'S CORN FLAKES",
    "nafdac_no_clean" : "A8-4114",
    "subcategory"     : "Cereals and Cereal Products",
    "applicant_name"  : "KELLOGG TOLARAM NIGERIA LIMTED",
    "expiry_date_iso" : "2029-07-30",
    "country"         : "NIGERIA",
}

LIPTON_RECORD = {
    "product_name"    : "LIPTON YELLOW LABEL TEA",
    "nafdac_no_clean" : "01-0132",
    "subcategory"     : "Beverages",
    "applicant_name"  : "UNILEVER NIGERIA PLC",
    "expiry_date_iso" : "2026-03-28",   # near-expiry in test context
    "country"         : "NIGERIA",
}

VASELINE_RECORD = {
    "product_name"    : "VASELINE BLUESEAL WHITE PETROLEUM JELLY",
    "nafdac_no_clean" : "A2-3016",
    "subcategory"     : "Cosmetics",
    "applicant_name"  : "UNILEVER NIGERIA PLC",
    "expiry_date_iso" : "2030-05-10",
    "country"         : "NIGERIA",
}


# ── Tool mock factory ─────────────────────────────────────────────────────────

def _make_tools(
    lookup_returns=None,
    search_returns=None,
    expiry_returns=None,
    alignment_returns=None,
    browse_returns=None,
):
    """Build a tools dict with mocked .fn() callables."""

    def _tool(fn):
        t = MagicMock()
        t.fn = fn
        return t

    # Defaults
    lookup_returns    = lookup_returns    if lookup_returns    is not None else []
    search_returns    = search_returns    if search_returns    is not None else []
    expiry_returns    = expiry_returns    or {
        "is_valid": True, "is_near_expiry": False,
        "expiry_date": "2029-07-30", "days_remaining": 1000,
        "severity": "NONE", "message": "Valid until 2029-07-30.",
    }
    alignment_returns = alignment_returns or {
        "is_match": True, "scanned_norm": "cereals and cereal products",
        "registered_norm": "cereals and cereal products",
        "mismatch_type": None, "severity": "NONE",
        "message": "Categories align.",
    }
    browse_returns    = browse_returns    if browse_returns is not None else []

    return {
        "lookup_nafdac"  : _tool(MagicMock(return_value=lookup_returns)),
        "semantic_search": _tool(MagicMock(return_value=search_returns)),
        "browse_category": _tool(MagicMock(return_value=browse_returns)),
        "check_expiry"   : _tool(MagicMock(return_value=expiry_returns)),
        "check_alignment": _tool(MagicMock(return_value=alignment_returns)),
    }


# ═══════════════════════════════════════════════════════════════════
# Class 1 — Critical override paths
# ═══════════════════════════════════════════════════════════════════

class TestCriticalOverride:
    """Tests for NOT_FOUND and SUBCATEGORY_MISMATCH verdict paths."""

    def test_not_found_when_lookup_empty_and_search_empty(self):
        """NAFDAC number doesn't exist — no semantic fallback hits either."""
        engine  = NAFDACReasoningEngine(_make_tools(lookup_returns=[], search_returns=[]))
        verdict = engine.run("FAKE-9999", "cereal")

        assert verdict.status_code          == "NOT_FOUND"
        assert verdict.verification_score   == 0.0
        assert verdict.severity             == "CRITICAL"
        assert verdict.verified             is False
        assert verdict.matched_record       is None

    def test_not_found_score_is_0(self):
        engine = NAFDACReasoningEngine(_make_tools())
        v = engine.run("FAKE-9999", "cereal")
        assert v.verification_score == 0.0

    def test_subcategory_mismatch_is_critical(self):
        """Valid NAFDAC number but product is the wrong type — strongest fake signal."""
        mismatch_alignment = {
            "is_match": False, "scanned_norm": "cosmetics",
            "registered_norm": "cereals and cereal products",
            "mismatch_type": "different_category",
            "severity": "CRITICAL", "message": "MISMATCH.",
        }
        tools   = _make_tools(
            lookup_returns    = [CORN_FLAKES_RECORD],
            alignment_returns = mismatch_alignment,
        )
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cosmetics")

        assert verdict.status_code        == "SUBCATEGORY_MISMATCH"
        assert verdict.severity           == "CRITICAL"
        assert verdict.verified           is False
        assert verdict.verification_score == 0.2

    def test_mismatch_detail_mentions_both_categories(self):
        mismatch_alignment = {
            "is_match": False, "scanned_norm": "cosmetics",
            "registered_norm": "cereals and cereal products",
            "mismatch_type": "different_category",
            "severity": "CRITICAL", "message": "MISMATCH.",
        }
        tools   = _make_tools(
            lookup_returns    = [CORN_FLAKES_RECORD],
            alignment_returns = mismatch_alignment,
        )
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cosmetics")

        assert "cosmetics" in verdict.detail.lower()
        assert "cereal"    in verdict.detail.lower()

    def test_mismatch_triggers_browse_for_context(self):
        """Agent should call browse_category after detecting a mismatch."""
        mismatch_alignment = {
            "is_match": False, "scanned_norm": "cosmetics",
            "registered_norm": "cereals and cereal products",
            "mismatch_type": "different_category",
            "severity": "CRITICAL", "message": "MISMATCH.",
        }
        tools   = _make_tools(
            lookup_returns    = [CORN_FLAKES_RECORD],
            alignment_returns = mismatch_alignment,
        )
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cosmetics")

        assert "browse_category" in engine._tools_called()


# ═══════════════════════════════════════════════════════════════════
# Class 2 — Expiry paths
# ═══════════════════════════════════════════════════════════════════

class TestExpiryPaths:
    """Tests for EXPIRED and VERIFIED_NEAR_EXPIRY verdict paths."""

    def test_expired_registration_verdict(self):
        expired_expiry = {
            "is_valid": False, "is_near_expiry": False,
            "expiry_date": "2024-01-01", "days_remaining": -400,
            "severity": "EXPIRED",
            "message": "Expired on 2024-01-01 (400 days ago).",
        }
        tools   = _make_tools(
            lookup_returns = [CORN_FLAKES_RECORD],
            expiry_returns = expired_expiry,
        )
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")

        assert verdict.status_code        == "EXPIRED"
        assert verdict.severity           == "HIGH"
        assert verdict.verified           is False
        assert verdict.verification_score == 0.1

    def test_expired_does_not_reach_alignment_check(self):
        """If expired, alignment check should NOT be called — no need."""
        expired_expiry = {
            "is_valid": False, "is_near_expiry": False,
            "expiry_date": "2024-01-01", "days_remaining": -400,
            "severity": "EXPIRED", "message": "Expired.",
        }
        tools   = _make_tools(
            lookup_returns = [CORN_FLAKES_RECORD],
            expiry_returns = expired_expiry,
        )
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cereal")

        assert "check_alignment" not in engine._tools_called()

    def test_near_expiry_still_verified(self):
        """Near-expiry product is VERIFIED with WARNING severity, not EXPIRED."""
        near_expiry = {
            "is_valid": True, "is_near_expiry": True,
            "expiry_date": "2026-03-28", "days_remaining": 18,
            "severity": "WARNING",
            "message": "Expires on 2026-03-28 (in 18 days).",
        }
        tools   = _make_tools(
            lookup_returns = [LIPTON_RECORD],
            expiry_returns = near_expiry,
        )
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("01-0132", "tea")

        assert verdict.status_code        == "VERIFIED_NEAR_EXPIRY"
        assert verdict.severity           == "WARNING"
        assert verdict.verified           is True
        assert verdict.verification_score == 0.85

    def test_near_expiry_score_is_085(self):
        near_expiry = {
            "is_valid": True, "is_near_expiry": True,
            "expiry_date": "2026-03-28", "days_remaining": 18,
            "severity": "WARNING", "message": "Expires soon.",
        }
        tools   = _make_tools(lookup_returns=[LIPTON_RECORD], expiry_returns=near_expiry)
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("01-0132", "tea")
        assert verdict.verification_score == 0.85


# ═══════════════════════════════════════════════════════════════════
# Class 3 — Clean verified path
# ═══════════════════════════════════════════════════════════════════

class TestVerifiedPath:
    """Tests for the fully verified clean scan path."""

    def test_clean_scan_is_verified(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "corn flakes")

        assert verdict.status_code        == "VERIFIED"
        assert verdict.verified           is True
        assert verdict.severity           == "NONE"
        assert verdict.verification_score == 1.0

    def test_verified_score_is_1(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")
        assert verdict.verification_score == 1.0

    def test_matched_record_is_populated(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")
        assert verdict.matched_record is not None
        assert verdict.matched_record["product_name"] == "KELLOGG'S CORN FLAKES"

    def test_all_records_is_populated(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")
        assert len(verdict.all_records) == 1

    def test_tool_sequence_for_clean_scan(self):
        """Clean scan must call exactly: lookup → check_expiry → check_alignment."""
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cereal")

        assert engine._tools_called() == [
            "lookup_nafdac", "check_expiry", "check_alignment"
        ]

    def test_verified_detail_mentions_product_and_applicant(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")
        assert "KELLOGG'S CORN FLAKES" in verdict.detail
        assert "KELLOGG TOLARAM" in verdict.detail


# ═══════════════════════════════════════════════════════════════════
# Class 4 — Semantic fallback
# ═══════════════════════════════════════════════════════════════════

class TestSemanticFallback:
    """Tests for the semantic search fallback when NAFDAC lookup returns nothing."""

    def _make_search_result(self, record: dict, score: float = 0.91) -> dict:
        return {
            "metadata"        : record,
            "text"            : "product chunk text",
            "similarity_score": score,
        }

    def test_fallback_used_when_lookup_empty(self):
        """When lookup returns nothing, agent must use semantic search."""
        tools = _make_tools(
            lookup_returns = [],
            search_returns = [self._make_search_result(CORN_FLAKES_RECORD)],
        )
        # Second lookup (after resolving via search) returns the record
        call_count = [0]
        def mock_lookup(nafdac):
            call_count[0] += 1
            if call_count[0] == 1:
                return []    # First call — simulate unreadable NAFDAC
            return [CORN_FLAKES_RECORD]   # Second call — after resolution

        tools["lookup_nafdac"].fn = mock_lookup
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("AAAA-1111", "cereal")

        assert verdict.fallback_used is True
        assert "semantic_search" in verdict.tools_called

    def test_fallback_returns_not_found_when_search_also_empty(self):
        """If both lookup and semantic search fail, result must be NOT_FOUND."""
        tools   = _make_tools(lookup_returns=[], search_returns=[])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("FAKE-9999", "cereal")

        assert verdict.status_code   == "NOT_FOUND"
        assert verdict.fallback_used is True

    def test_not_found_fallback_detail_mentions_search(self):
        """Detail message should note that semantic search was also attempted."""
        tools   = _make_tools(lookup_returns=[], search_returns=[])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("FAKE-9999", "cereal")
        assert "semantic" in verdict.detail.lower()

    def test_fallback_not_used_when_lookup_succeeds(self):
        """If lookup finds the product, semantic search should NOT be called."""
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")

        assert verdict.fallback_used is False
        assert "semantic_search" not in verdict.tools_called


# ═══════════════════════════════════════════════════════════════════
# Class 5 — Reasoning trace
# ═══════════════════════════════════════════════════════════════════

class TestReasoningTrace:
    """Tests for step count, tool sequence, and trace contents."""

    def test_trace_has_3_steps_for_clean_scan(self):
        """Clean scan: lookup → check_expiry → check_alignment = 3 steps."""
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cereal")
        assert len(engine.steps) == 3

    def test_trace_has_2_steps_for_expired(self):
        """Expired scan: lookup → check_expiry = 2 steps (stops before alignment)."""
        expired = {
            "is_valid": False, "is_near_expiry": False,
            "expiry_date": "2024-01-01", "days_remaining": -400,
            "severity": "EXPIRED", "message": "Expired.",
        }
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD], expiry_returns=expired)
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cereal")
        assert len(engine.steps) == 2

    def test_trace_has_4_steps_for_mismatch(self):
        """Mismatch scan: lookup → expiry → alignment → browse_category = 4 steps."""
        mismatch = {
            "is_match": False, "scanned_norm": "cosmetics",
            "registered_norm": "cereals and cereal products",
            "mismatch_type": "different_category",
            "severity": "CRITICAL", "message": "MISMATCH.",
        }
        tools   = _make_tools(
            lookup_returns    = [CORN_FLAKES_RECORD],
            alignment_returns = mismatch,
        )
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cosmetics")
        assert len(engine.steps) == 4

    def test_each_step_has_thought_and_action(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cereal")
        for step in engine.steps:
            assert step.thought, f"Step '{step.action}' missing thought"
            assert step.action
            assert step.observation_summary

    def test_first_step_is_always_lookup(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        engine.run("A8-4114", "cereal")
        assert engine.steps[0].action == "lookup_nafdac"

    def test_trace_resets_between_runs(self):
        """The engine must reset its trace for each new scan."""
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)

        engine.run("A8-4114", "cereal")
        steps_first = len(engine.steps)

        engine.run("A8-4114", "cereal")
        steps_second = len(engine.steps)

        assert steps_first == steps_second   # Same path → same count

    def test_verdict_reasoning_trace_matches_engine_steps(self):
        tools   = _make_tools(lookup_returns=[CORN_FLAKES_RECORD])
        engine  = NAFDACReasoningEngine(tools)
        verdict = engine.run("A8-4114", "cereal")
        assert len(verdict.reasoning_trace) == len(engine.steps)


# ═══════════════════════════════════════════════════════════════════
# Class 6 — agent_scorer.py drop-in interface
# ═══════════════════════════════════════════════════════════════════

class TestAgentScorerInterface:
    """Verifies compute_verification_score() returns the same keys as regulatory_scorer."""

    REQUIRED_KEYS = {
        "verified", "verification_score", "status_code", "severity",
        "summary", "detail", "expiry_check", "alignment",
        "matched_record", "all_records",
    }

    AGENT_ONLY_KEYS = {"reasoning_trace", "tools_called", "fallback_used"}

    def _mock_agent_and_call(self, verdict: AgentVerdict) -> dict:
        """Patch the agent singleton and call compute_verification_score."""
        import agent.agent_scorer as scorer_module
        mock_agent = MagicMock()
        mock_agent.verify.return_value = verdict
        scorer_module._agent = mock_agent
        result = scorer_module.compute_verification_score("A8-4114", "cereal", [])
        scorer_module._agent = None   # Reset after test
        return result

    def _make_verdict(self, status: str, score: float, severity: str) -> AgentVerdict:
        return AgentVerdict(
            verified             = score == 1.0,
            verification_score   = score,
            status_code          = status,
            severity             = severity,
            summary              = "Test summary",
            detail               = "Test detail",
            expiry_check         = None,
            alignment            = None,
            matched_record       = None,
            all_records          = [],
            reasoning_trace      = [],
            tools_called         = [],
            fallback_used        = False,
        )

    def test_all_required_keys_present(self):
        verdict = self._make_verdict("VERIFIED", 1.0, "NONE")
        result  = self._mock_agent_and_call(verdict)
        for key in self.REQUIRED_KEYS:
            assert key in result, f"Missing required key: '{key}'"

    def test_agent_only_keys_present(self):
        verdict = self._make_verdict("VERIFIED", 1.0, "NONE")
        result  = self._mock_agent_and_call(verdict)
        for key in self.AGENT_ONLY_KEYS:
            assert key in result, f"Missing agent key: '{key}'"

    def test_verified_verdict_shape(self):
        verdict = self._make_verdict("VERIFIED", 1.0, "NONE")
        result  = self._mock_agent_and_call(verdict)
        assert result["verified"]           is True
        assert result["verification_score"] == 1.0
        assert result["status_code"]        == "VERIFIED"
        assert result["severity"]           == "NONE"

    def test_not_found_verdict_shape(self):
        verdict = self._make_verdict("NOT_FOUND", 0.0, "CRITICAL")
        result  = self._mock_agent_and_call(verdict)
        assert result["verified"]           is False
        assert result["verification_score"] == 0.0
        assert result["severity"]           == "CRITICAL"

    def test_mismatch_verdict_shape(self):
        verdict = self._make_verdict("SUBCATEGORY_MISMATCH", 0.2, "CRITICAL")
        result  = self._mock_agent_and_call(verdict)
        assert result["verification_score"] == 0.2
        assert result["status_code"]        == "SUBCATEGORY_MISMATCH"

    def test_reasoning_trace_is_list(self):
        verdict = self._make_verdict("VERIFIED", 1.0, "NONE")
        result  = self._mock_agent_and_call(verdict)
        assert isinstance(result["reasoning_trace"], list)

    def test_tools_called_is_list(self):
        verdict = self._make_verdict("VERIFIED", 1.0, "NONE")
        result  = self._mock_agent_and_call(verdict)
        assert isinstance(result["tools_called"], list)

    def test_fallback_used_is_bool(self):
        verdict = self._make_verdict("VERIFIED", 1.0, "NONE")
        result  = self._mock_agent_and_call(verdict)
        assert isinstance(result["fallback_used"], bool)
