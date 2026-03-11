"""

Coordinates Vision, OCR, Regulatory, and Fusion
for every product label scan in SabiLens.

D1 Backend creates one ScanOrchestrator instance at startup and calls scan() per request.

RESPONSIBILITY OF THIS FILE:
  Collect signals from Visual, OCR, Regulatory and hand them to Fusion.
  That is all.

WHAT THIS FILE DOES NOT DO:
  - Score signals          -> fusion's job (fusion_engine/core/fusion_engine.py)
  - Apply weights          -> fusion's job (fusion_engine/config/weights.py)
  - Apply overrides        -> fusion's job (fusion_engine/signals/rag_adapter.py)
  - Map verdicts           -> fusion's job (fusion_engine/core/decision_classifier.py)
  - Package evidence       -> fusion's job (fusion_engine/core/evidence_packager.py)

CALL SEQUENCE PER SCAN:
  1. _run_ocr()         -> collect ocr signal (mocked until ocr integrated)
  2. _run_regulatory()  -> run regulatory ReAct agent (always real)
  3. _run_vision()      -> collect Visual signal (mocked until Visual integrated)
  4. _run_fusion()      -> hand all three signals to fusion, return ScanResult

INTEGRATION GUIDE (replacing mocks with real modules):
  Visual ready:
    Replace _run_vision() mock with VisualPipeline.analyze(image_path)
    Pass the full analyze() output dict as vision_signal.payload
    The "blur_value" and "damage_score" fields are required by fusion.

  ocr ready:
    Replace _run_ocr() mock with pipeline.run_pipeline(image_path, damage_score)
    Pass the full run_pipeline() output dict as ocr_signal.payload

  No changes needed to _run_regulatory() or _run_fusion() - they are final.

Usage:
    orchestrator = ScanOrchestrator()                        # once at startup

    # Mocked Visual + ocr (current state):
    result = orchestrator.scan(
        nafdac_no        = "A8-4114",
        scanned_category = "corn flakes",
        gps_coordinates  = {"lat": 6.5244, "lng": 3.3792, "accuracy": 8.5},
        purchase_channel = "open_market",
    )
    print(result.final_verdict)    # AUTHENTIC | SUSPICIOUS | FAKE
    print(result.final_score)      # 0.0–1.0
    print(result.action)           # BUY | CAUTION | DO NOT BUY

    # Real Visual + ocr (once integrated):
    result = orchestrator.scan(
        nafdac_no        = "A8-4114",
        scanned_category = "corn flakes",
        gps_coordinates  = {"lat": 6.5244, "lng": 3.3792, "accuracy": 8.5},
        purchase_channel = "open_market",
        Visual_output        = visual_pipeline.analyze(image_path),
        ocr_output        = ocr_pipeline.run_pipeline(image_path, damage_score),
    )

    # Plain-text reasoning trace for demos and D5 audit panel:
    print(orchestrator.explain("A8-4114", "corn flakes"))
"""

from ai_engine.agent.verification_agent import NAFDACVerificationAgent
from ai_engine.orchestrator.pipeline    import (
    AgentSignal, PipelineResult, MOCK_CONFIDENCE,
)
from fusion_engine.main import run_scan


class ScanOrchestrator:
    """
    Collects signals from Visual, ocr, regulatory and hands them to fusion.
    Creates one NAFDACVerificationAgent at startup (loads ChromaDB + model once).
    """

    def __init__(self):
        self._regulatory_agent = NAFDACVerificationAgent()

    def scan(
        self,
        nafdac_no:        str,
        scanned_category: str,
        gps_coordinates:  dict,                # {"lat": float, "lng": float, "accuracy": float}
        purchase_channel: str,                 # "open_market" | "supermarket" | "traffic_vendor" etc.
        visual_output:        dict | None = None,  # real Visual output; None ->mock used
        ocr_output:        dict | None = None,  # real ocr output; None ->mock used
        receipt_image:    str  | None = None,  # optional - for evidence package
        storefront_image: str  | None = None,  # optional - for evidence package
    ) -> PipelineResult:
        """
        Run the full scan pipeline and return a PipelineResult.

        Steps:
          1. Collect ocr signal (real or mocked)
          2. Run regulatory ReAct agent (always real)
          3. Collect vision signal (real or mocked)
          4. Hand all three to fusion run_scan() - fusion owns all scoring and verdict logic
          5. Package fusion's ScanResult into a PipelineResult for D1 Backend

        Args:
            nafdac_no:        NAFDAC number extracted from label (or raw string for regulatory to normalise)
            scanned_category: Product category detected from label or user selection
            gps_coordinates:  GPS lock at point of scan - required for evidence package
            purchase_channel: Where the product was purchased - for NAFDAC enforcement report
            Visual_output:        Full dict from VisualPipeline.analyze(). None until visual integrated.
            ocr_output:        Full dict from pipeline.run_pipeline(). None until ocr integrated.
            receipt_image:    Optional image path/base64 for evidence package
            storefront_image: Optional image path/base64 for evidence package

        Returns:
            PipelineResult with all verdict fields populated from fusion's ScanResult.
        """
        # Collect ocr signal 
        ocr_signal = self._run_ocr(nafdac_no, ocr_output)

        # Run regulatory ReAct agent ─
        regulatory_signal = self._run_regulatory(nafdac_no, scanned_category)

        # Collect vision signal 
        vision_signal = self._run_vision(scanned_category, visual_output)

        # Hand everything to fusion 
        # fusion owns: weights, overrides, damage logic, verdict, evidence packaging.
        # The orchestrator passes raw payloads and context - nothing more.
        fusion_signal = self._run_fusion(
            vision_signal     = vision_signal,
            ocr_signal        = ocr_signal,
            regulatory_signal = regulatory_signal,
            gps_coordinates   = gps_coordinates,
            purchase_channel  = purchase_channel,
            receipt_image     = receipt_image,
            storefront_image  = storefront_image,
        )

        # Unpack fusion's ScanResult into PipelineResult 
        fusion = fusion_signal.payload  # fusion's full ScanResult dict

        return PipelineResult(
            vision_signal      = vision_signal,
            ocr_signal         = ocr_signal,
            regulatory_signal  = regulatory_signal,
            fusion_signal      = fusion_signal,

            # Verdict fields - all from fusion, never computed here ─
            status             = fusion.get("status",             "FAILSAFE"),
            scan_id            = fusion.get("scan_id",            ""),
            final_verdict      = fusion.get("verdict",            "FAKE"),
            final_score        = fusion.get("final_score",        0.0),
            final_severity     = fusion.get("severity",           "CRITICAL"),
            action             = fusion.get("action",             "DO NOT BUY"),
            simple_instruction = fusion.get("simple_instruction", ""),
            atlas_instruction  = fusion.get("atlas_instruction",  ""),
            summary            = fusion.get("atlas_summary",      ""),
            detail             = fusion.get("atlas_detail",       ""),
            report_priority    = fusion.get("report_priority",    "NONE"),
            override_applied   = fusion.get("override_applied",   False),
            override_summary   = fusion.get("override_summary",   ""),
            warnings           = fusion.get("warnings",           []),
            breakdown          = fusion.get("breakdown",          {}),
            evidence_package   = fusion.get("evidence_package",   {}),
            rescan_required    = fusion.get("status") == "RESCAN_REQUIRED",

            # signals_used: agents with non-zero weight in fusion breakdown
            signals_used = [
                agent for agent in ["visual", "ocr", "reg"]
                if fusion.get("breakdown", {}).get(agent, {}).get("weight", 0) > 0
            ],
        )

    # Agent runners 
    # Each runner packages a signal into an AgentSignal envelope.
    # When a module is not yet integrated, mocked=True and a safe mock payload is used.
    # Switching from mock to real requires only changing the payload - nothing else.

    def _run_ocr(self, nafdac_no: str, ocr_output: dict | None) -> AgentSignal:
        """
        Package the OCR signal.
        Uses real ocr_output if provided, otherwise returns a mock signal.

        Mock payload passes the raw nafdac_no through so reg can still attempt
        a real NAFDAC lookup even while ocr is unmocked.
        """
        if ocr_output is not None:
            return AgentSignal(
                agent_id   = "ocr",
                available  = True,
                confidence = 1.0 - ocr_output.get("final_text_anomaly_score", 0.0),
                mocked     = False,
                payload    = ocr_output,
            )

        # Mock: ocr not yet integrated
        return AgentSignal(
            agent_id   = "ocr",
            available  = True,
            confidence = MOCK_CONFIDENCE,
            mocked     = True,
            payload    = {
                "source":                   "OCR_MOCK",
                "final_text_anomaly_score": 1.0 - MOCK_CONFIDENCE,  # 0.20 anomaly ->0.80 confidence
                "ml_score":                 1.0 - MOCK_CONFIDENCE,
                "metadata": {
                    "nafdac_number":      nafdac_no,   # pass raw NAFDAC so reg can still verify
                    "avg_ocr_confidence": MOCK_CONFIDENCE,
                    "brand_detected":     None,
                    "brand_similarity":   0.0,
                    "brand_anomaly_flag": 0,
                },
                "brand_anomaly": {
                    "brand_detected":        None,
                    "similarity_score":      100.0,
                    "lookalike_corrections": [],
                    "brand_anomaly_flag":    0,
                },
                "structural_validation": {
                    "missing_fields":      [],
                    "structural_score":    1.0,
                    "expiry_format_valid": True,
                    "batch_format_valid":  True,
                },
                "rule_score": {
                    "rule_score":           1.0 - MOCK_CONFIDENCE,
                    "damage_score_applied": 0.1,
                    "adjusted_ocr_confidence": MOCK_CONFIDENCE,
                    "components":           {},
                },
            },
        )

    def _run_regulatory(self, nafdac_no: str, scanned_category: str) -> AgentSignal:
        """
        Run the reg NAFDAC ReAct verification agent.
        This is always a real call - regulatory is never mocked.

        The agent runs: lookup_nafdac ->check_expiry ->check_alignment
        and may fall back to semantic_search if the NAFDAC number is not found directly.
        """
        verdict = self._regulatory_agent.verify(nafdac_no, scanned_category)

        return AgentSignal(
            agent_id   = "regulatory",
            available  = True,
            confidence = verdict.verification_score,  # 0.0–1.0, positive direction
            mocked     = False,
            payload    = {
                # Core fields - fusion rag_adapter reads these 
                "verified":           verdict.verified,
                "verification_score": verdict.verification_score,
                "status_code":        verdict.status_code,
                "severity":           verdict.severity,
                "summary":            verdict.summary,
                "detail":             verdict.detail,
                "expiry_check":       verdict.expiry_check,
                "alignment":          verdict.alignment,
                "matched_record":     verdict.matched_record,
                "all_records":        verdict.all_records,

                # ReAct agent fields - fusion uses for dynamic weights + audit
                "fallback_used": verdict.fallback_used,   # True ->semantic search used ->reg weight reduced
                "tools_called":  verdict.tools_called,    # ["lookup_nafdac", "check_expiry", ...]
                "reasoning_trace": [
                    {
                        "thought":             step.thought,
                        "action":              step.action,
                        "action_input":        step.action_input,
                        "observation_summary": step.observation_summary,
                    }
                    for step in verdict.reasoning_trace
                ],
            },
        )

    def _run_vision(self, scanned_category: str, visual_output: dict | None) -> AgentSignal:
        """
        Package the vision signal.
        Uses real visual_output if provided, otherwise returns a mock signal.

        IMPORTANT: Real visual_output must include "blur_value" (raw Laplacian variance)
        in addition to "damage_score". fusion uses blur_value to decide whether to
        reject the scan or shift weights. See damage_detector.py for the change.
        """
        if visual_output is not None:
            return AgentSignal(
                agent_id   = "vision",
                available  = True,
                confidence = visual_output.get("confidence", 0.0),
                mocked     = False,
                payload    = visual_output,   # must contain: product, Visual Similarity,
                                          # damage_score, blur_value, confidence, verdict
            )

        # Mock: visual not yet integrated
        # blur_value=80.0 ->sharp image (no damage weight penalty in fusion)
        return AgentSignal(
            agent_id   = "vision",
            available  = True,
            confidence = MOCK_CONFIDENCE,
            mocked     = True,
            payload    = {
                "product":           "UNKNOWN - visual not yet integrated",
                "Visual Similarity": MOCK_CONFIDENCE,
                "damage_score":      0.1,    # assume sharp image while mocked
                "blur_value":        80.0,   # above 60 threshold ->no damage penalty
                "confidence":        MOCK_CONFIDENCE,
                "verdict":           "Authentic" if MOCK_CONFIDENCE >= 0.75 else "Suspicious",
            },
        )

    def _run_fusion(
        self,
        vision_signal:     AgentSignal,
        ocr_signal:        AgentSignal,
        regulatory_signal: AgentSignal,
        gps_coordinates:   dict,
        purchase_channel:  str,
        receipt_image:     str | None,
        storefront_image:  str | None,
    ) -> AgentSignal:
        """
        Hand all three signals to fusion and return the result as an AgentSignal.

        This method contains NO scoring logic.
        All weighting, override, damage, and verdict logic lives in fusion.

        fusion's run_scan() receives:
          - Raw visual, ocr, reg payloads (adapters normalise them internally)
          - GPS coordinates and purchase channel (for evidence package)
          - Optional receipt and storefront images (for NAFDAC report)

        fusion returns a ScanResult dict. This method wraps it in an AgentSignal
        so PipelineResult can store it uniformly alongside the other signals.
        """
        scan_result = run_scan(
            visual_output        = vision_signal.payload,
            ocr_output        = ocr_signal.payload,
            reg_output        = regulatory_signal.payload,
            gps_coordinates  = gps_coordinates,
            purchase_channel = purchase_channel,
            receipt_image    = receipt_image,
            storefront_image = storefront_image,
        )

        return AgentSignal(
            agent_id   = "fusion",
            available  = True,
            confidence = scan_result.get("final_score", 0.0),
            mocked     = False,
            payload    = scan_result,   # full fusion ScanResult dict
        )

    # Developer utility

    def explain(self, nafdac_no: str, scanned_category: str) -> str:
        """
        Run a full scan with mock visual/ocr and return a formatted plain-text report.
        Shows the reg reasoning trace and fusion fusion breakdown.
        Useful for instructor demos, rag_query.py, and the D5 audit panel.
        """
        result           = self.scan(
            nafdac_no        = nafdac_no,
            scanned_category = scanned_category,
            gps_coordinates  = {"lat": 0.0, "lng": 0.0, "accuracy": 0.0},
            purchase_channel = "unknown",
        )
        regulatory_trace = result.regulatory_signal.payload.get("reasoning_trace", [])
        breakdown        = result.breakdown

        lines = [
            "",
            "SABILENS SCAN - Orchestrator Report",
            "=" * 60,
            f"NAFDAC      : {nafdac_no}",
            f"Category    : {scanned_category}",
            f"Scan ID     : {result.scan_id}",
            f"Status      : {result.status}",
            f"Visual   : {'mocked' if result.vision_signal.mocked else 'real'}",
            f"ocr      : {'mocked' if result.ocr_signal.mocked else 'real'}",
            f"Regulatory: real (always)",
            "",
            "REGULATORY AGENT REASONING",
            "-" * 40,
        ]
        for i, step in enumerate(regulatory_trace, 1):
            lines += [
                f"  Step {i} | {step['action']}",
                f"    Thought : {step['thought']}",
                f"    Result  : {step['observation_summary']}",
                "",
            ]
        lines += [
            "FUSION BREAKDOWN",
            "-" * 40,
        ]
        for signal, data in breakdown.items():
            lines.append(
                f"  {signal:<12} score={data.get('raw_score', 'n/a')}  "
                f"weight={data.get('weight', 'n/a')}  "
                f"weighted={data.get('weighted', 'n/a')}"
            )
        lines += [
            f"  Override applied : {result.override_applied}",
            f"  Override summary : {result.override_summary or 'None'}",
            "",
            "FINAL VERDICT",
            "-" * 40,
            f"  Verdict    : {result.final_verdict}",
            f"  Score      : {result.final_score}",
            f"  Severity   : {result.final_severity}",
            f"  Action     : {result.action}",
            f"  Instruction: {result.simple_instruction}",
            f"  Warnings   : {[w['type'] for w in result.warnings]}",
            "",
        ]
        return "\n".join(lines)