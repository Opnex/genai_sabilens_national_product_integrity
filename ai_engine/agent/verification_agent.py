"""
agent/verification_agent.py
Single entry point for all product verification in the SabiLens system.
Instantiate once at startup; call verify() or explain() per request.
"""

from ai_engine.rag_system.retrieval.retriever    import ProductRetriever
from ai_engine.agent.tools            import build_tools
from ai_engine.agent.reasoning_engine import NAFDACReasoningEngine, AgentVerdict


class NAFDACVerificationAgent:
    """
    Loads the retriever and tools once, then runs the ReAct verification loop per scan.

    Usage:
        agent   = NAFDACVerificationAgent()          # once at startup
        verdict = agent.verify("A8-4114", "cereal")  # once per scan request
    """

    def __init__(self):
        self.retriever = ProductRetriever()           # loads ChromaDB + sentence-transformer model
        self.tools     = build_tools(self.retriever)  # wraps retriever methods as LlamaIndex FunctionTools
        self.engine    = NAFDACReasoningEngine(self.tools)  # rule-based ReAct step runner

    def verify(self, nafdac_no: str, scanned_category: str) -> AgentVerdict:
        """
        Run the ReAct loop for one product scan and return a verdict.
        Never raises — exceptions are caught and returned as AGENT_ERROR verdicts.
        """
        try:
            return self.engine.run(
                nafdac_no        = nafdac_no,
                scanned_category = scanned_category,
            )
        except Exception as exc:
            from agent.reasoning_engine import SCORE_NOT_FOUND
            return AgentVerdict(              # fail-safe: bad scan must not crash the API server
                verified             = False,
                verification_score   = SCORE_NOT_FOUND,
                status_code          = "AGENT_ERROR",
                severity             = "CRITICAL",
                summary              = "Agent encountered an unexpected error.",
                detail               = f"Verification failed for NAFDAC '{nafdac_no}': {exc}. Treat this scan as unverified.",
                expiry_check         = None,
                alignment            = None,
                matched_record       = None,
                all_records          = [],
                reasoning_trace      = [],
                tools_called         = [],
                fallback_used        = False,
            )

    def explain(self, nafdac_no: str, scanned_category: str) -> str:
        """
        Run verification and return a formatted plain-text reasoning trace.
        Useful for instructor demos, rag_query.py, and the D5 audit panel.
        """
        verdict = self.verify(nafdac_no, scanned_category)
        lines   = [
            "",
            "NAFDAC VERIFICATION — Agent Reasoning Trace",
            "=" * 60,
            f"Input:         nafdac='{nafdac_no}'  category='{scanned_category}'",
            f"Fallback used: {verdict.fallback_used}",
            "",
        ]
        for i, step in enumerate(verdict.reasoning_trace, 1):
            lines += [
                f"Step {i} | {step.action}",
                f"  Thought : {step.thought}",
                f"  Input   : {step.action_input}",
                f"  Result  : {step.observation_summary}",
                "",
            ]
        lines += [
            "-" * 60,
            f"VERDICT  : {verdict.status_code}",
            f"Score    : {verdict.verification_score}",
            f"Severity : {verdict.severity}",
            f"Summary  : {verdict.summary}",
            f"Tools    : {' -> '.join(verdict.tools_called)}",
            "",
        ]
        return "\n".join(lines)
