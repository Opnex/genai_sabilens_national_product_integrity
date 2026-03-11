"""
ai_engine/orchestrator/scan_orchestrator.py

Executes a regulatory verification scan using the NAFDAC verification agent.

Responsibilities:
    • Instantiates the regulatory verification agent once.
    • Runs the agent verification process for a given NAFDAC number
      and scanned product category.
    • Converts the agent's internal verdict into a structured
      VerificationResult object.
    • Provides a human-readable explanation of the agent reasoning
      trace for debugging, demos, and CLI inspection.
"""

# Import the regulatory verification agent that performs the actual reasoning
from ai_engine.agent.verification_agent import NAFDACVerificationAgent

# Import the structured result container returned to the API layer
from ai_engine.orchestrator.pipeline import VerificationResult


class ScanOrchestrator:
    """
    Coordinates execution of the regulatory verification agent.

    The orchestrator receives a NAFDAC number and scanned product
    category, runs the verification agent, and returns the results
    as a structured VerificationResult.

    A single instance is created at application startup so the
    underlying vector database and embedding model are loaded only once.

    Methods:
        verify()  → Executes a verification scan and returns structured results.
        explain() → Executes a verification scan and returns a formatted
                    reasoning trace for human inspection.
    """

    def __init__(self):
        # Create a single instance of the regulatory verification agent.
        # The agent internally loads the Chroma vector database and
        # embedding model so they remain in memory for future scans.
        self._regulatory_agent = NAFDACVerificationAgent()

    def verify(self, nafdac_no: str, scanned_category: str) -> VerificationResult:
        """
        Executes a regulatory verification scan.

        The method sends the provided NAFDAC number and scanned
        product category to the verification agent, receives the
        agent's verdict, and converts it into a structured
        VerificationResult object used by the API layer.

        Args:
            nafdac_no:
                NAFDAC registration number extracted from OCR or
                provided by the caller.

            scanned_category:
                Product category inferred from OCR or visual analysis.

        Returns:
            VerificationResult containing:
                • verification status
                • verification score
                • severity level
                • summary and detailed explanation
                • matched product record (if found)
                • expiry evaluation
                • category alignment analysis
                • full reasoning trace produced by the agent
                • list of tools invoked during reasoning
                • whether a fallback retrieval strategy was used
        """

        # Run the agent verification process and obtain a verdict object
        verdict = self._regulatory_agent.verify(nafdac_no, scanned_category)

        # Convert the agent verdict into the public VerificationResult structure
        return VerificationResult(

            # Original NAFDAC number provided for the scan
            nafdac_no=nafdac_no,

            # Product category detected from OCR or classification
            scanned_category=scanned_category,

            # Boolean indicating whether the product verification passed
            verified=verdict.verified,

            # Numerical confidence score returned by the verification agent
            verification_score=verdict.verification_score,

            # Status code representing the final verification outcome
            status_code=verdict.status_code,

            # Severity level indicating the seriousness of any detected issue
            severity=verdict.severity,

            # Short human-readable summary of the result
            summary=verdict.summary,

            # Detailed explanation describing the verification reasoning
            detail=verdict.detail,

            # Database record matched to the scanned NAFDAC number
            matched_record=verdict.matched_record,

            # Expiry validation result returned by the regulatory checks
            expiry_check=verdict.expiry_check,

            # Subcategory alignment analysis between scanned and registered product
            alignment=verdict.alignment,

            # Convert the agent reasoning steps into a serialisable structure
            reasoning_trace=[
                {
                    # Internal reasoning step describing the agent's intent
                    "thought": step.thought,

                    # Tool or action executed by the agent
                    "action": step.action,

                    # Input provided to the tool
                    "action_input": step.action_input,

                    # Short summary of the observation returned by the tool
                    "observation_summary": step.observation_summary,
                }
                # Iterate through each reasoning step produced by the agent
                for step in verdict.reasoning_trace
            ],

            # Ordered list of tools invoked by the agent during verification
            tools_called=verdict.tools_called,

            # Boolean indicating whether the fallback retrieval strategy was used
            fallback_used=verdict.fallback_used,
        )

    def explain(self, nafdac_no: str, scanned_category: str) -> str:
        """
        Executes a verification scan and produces a formatted
        plain-text report of the reasoning process.

        The output includes:
            • the scanned NAFDAC number
            • the detected product category
            • the step-by-step reasoning actions taken by the agent
            • the final verification verdict
            • details of the matched database record

        This method is primarily used for debugging, CLI inspection,
        and demonstration output.
        """

        # Run a full verification scan
        result = self.verify(nafdac_no, scanned_category)

        # Build a formatted report header
        lines = [
            "",
            "SABILENS — Regulatory Verification Report",
            "=" * 60,
            f"NAFDAC No   : {nafdac_no}",
            f"Category    : {scanned_category}",
            "",
            "AGENT REASONING",
            "-" * 40,
        ]

        # Iterate through the reasoning steps and add them to the report
        for i, step in enumerate(result.reasoning_trace, 1):
            lines += [
                # Step identifier and action name
                f"  Step {i} | {step['action']}",

                # The agent's internal reasoning statement
                f"    Thought : {step['thought']}",

                # Summary of the result returned by the action
                f"    Result  : {step['observation_summary']}",
                "",
            ]

        # Append the final verification verdict section
        lines += [
            "VERDICT",
            "-" * 40,
            f"  Status   : {result.status_code}",
            f"  Score    : {result.verification_score}",
            f"  Severity : {result.severity}",
            f"  Summary  : {result.summary}",
            f"  Tools    : {' → '.join(result.tools_called)}",
            f"  Fallback : {result.fallback_used}",
            "",
        ]

        # If a database record was matched, include its key details
        if result.matched_record:
            lines += [
                "MATCHED RECORD",
                "-" * 40,
                f"  Product   : {result.matched_record.get('product_name')}",
                f"  Applicant : {result.matched_record.get('applicant_name')}",
                f"  Expiry    : {result.matched_record.get('expiry_date_iso')}",
                f"  Category  : {result.matched_record.get('subcategory')}",
                "",
            ]

        # Combine all lines into a single formatted string
        return "\n".join(lines)