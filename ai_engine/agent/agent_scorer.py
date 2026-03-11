"""
agent/agent_scorer.py
Exposes the same compute_verification_score() signature so routes.py needs only one import change.
"""

from ai_engine.agent.verification_agent import NAFDACVerificationAgent
from ai_engine.agent.reasoning_engine   import AgentVerdict

_agent: NAFDACVerificationAgent | None = None  # shared singleton, created lazily on first call


def _get_agent() -> NAFDACVerificationAgent:
    """Return the shared agent instance, creating it on first call."""
    global _agent
    if _agent is None:
        _agent = NAFDACVerificationAgent()  # expensive: loads ChromaDB + model — only runs once
    return _agent


def compute_verification_score(
    nafdac_no:           str,
    scanned_subcategory: str,
    db_records:          list,   # kept for API compatibility with routes.py; agent re-fetches internally
) -> dict:
    """
    Run the verification agent and return a result dict compatible with routes.py.
    Same keys as regulatory_scorer.compute_verification_score(), plus reasoning_trace,
    tools_called, and fallback_used for the D5 audit panel.
    """
    verdict: AgentVerdict = _get_agent().verify(nafdac_no, scanned_subcategory)
    return _verdict_to_dict(verdict)


def _verdict_to_dict(v: AgentVerdict) -> dict:
    """Serialise AgentVerdict to the dict shape routes.py and A4 Fusion expect."""
    return {
        # Core fields — identical to regulatory_scorer output
        "verified"           : v.verified,
        "verification_score" : v.verification_score,
        "status_code"        : v.status_code,
        "severity"           : v.severity,
        "summary"            : v.summary,
        "detail"             : v.detail,
        "expiry_check"       : v.expiry_check,
        "alignment"          : v.alignment,
        "matched_record"     : v.matched_record,
        "all_records"        : v.all_records,
        # Agent-only fields — downstream consumers safely ignore these
        "reasoning_trace"    : [
            {
                "thought"            : s.thought,
                "action"             : s.action,
                "action_input"       : s.action_input,
                "observation_summary": s.observation_summary,
            }
            for s in v.reasoning_trace           # one dict per ReActStep
        ],
        "tools_called"       : v.tools_called,   # e.g. ["lookup_nafdac", "check_expiry", "check_alignment"]
        "fallback_used"      : v.fallback_used,  # True if semantic search was needed
    }
