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
  1. _run_ocr()         -> OCR linguistic pipeline
  2. _run_regulatory()  -> NAFDAC ReAct verification agent
  3. _run_vision()      -> Visual similarity + damage pipeline
  4. _run_fusion()      -> Fusion Engine (weights, verdict, evidence)

INTEGRATION STATUS:
  Visual     -> REAL  (VisualPipeline.analyze())
  OCR        -> REAL  (ocr_pipeline.run_pipeline())
  Regulatory -> REAL  (NAFDACVerificationAgent.verify())
  Fusion     -> REAL  (fusion_engine.main.run_scan())

MOCK FALLBACK:
  If any real module raises an exception, _run_*() catches it,
  logs a WARNING, and returns a safe mock signal with mocked=True.
  This keeps the pipeline alive for partial scans (e.g. no camera access).
  fusion receives the mock and adjusts weights / logs it in the evidence package.

SUBCATEGORY MAPPING:
  Regulatory(RAG)'s check_alignment compares scanned_category against the NAFDAC registered
  category string (e.g. "Cereals and Cereal Products"). The orchestrator maps
  product-level descriptions to NAFDAC category strings via NAFDAC_CATEGORY_MAP
  before calling regulatory. If no mapping exists, the raw string is passed through and
  Regulatory(RAG)'s fallback semantic search handles it.

Usage:
    orchestrator = ScanOrchestrator()                        # once at startup; loads ChromaDB + models

    result = orchestrator.scan(
        image_path       = "/path/to/product_label.jpg",
        nafdac_no        = "A8-4114",
        scanned_category = "corn flakes",
        gps_coordinates  = {"lat": 6.5244, "lng": 3.3792, "accuracy": 8.5},
        purchase_channel = "open_market",
    )
    print(result.final_verdict)    # AUTHENTIC | SUSPICIOUS | FAKE
    print(result.final_score)      # 0.0-1.0
    print(result.action)           # BUY | CAUTION | DO NOT BUY
    print(result.simple_instruction) # voice-first instruction

"""


import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from typing import Optional
from ai_engine.agent.verification_agent import NAFDACVerificationAgent
from ai_engine.fusion_engine.main import run_scan
from ai_engine.orchestrator.pipeline import (
    AgentSignal,
    PipelineResult,
    MOCK_CONFIDENCE,
)

logger = logging.getLogger("ScanOrchestrator")


# NAFDAC Category Map 
# Maps human-readable product descriptions to NAFDAC registered category strings.
# Regulatory's check_alignment tool compares the scanned category against the registered
# category in the NAFDAC database — these must match the database's own strings.
#
# TO ADD A NEW PRODUCT: append a (keyword, nafdac_category) pair.
# Keywords are matched case-insensitively as substrings of the scanned_category.

NAFDAC_CATEGORY_MAP: dict = {
    # Cereals & Grains
    "corn flakes":              "Cereals and Cereal Products",
    "cornflakes":               "Cereals and Cereal Products",
    "coco pops":                "Cereals and Cereal Products",
    "go grains":                "Cereals and Cereal Products",
    "pasta":                    "Cereal Products",
    "spaghetti":                "Cereal Products",
    "noodles":                  "Cereal Products",
    # Oils & Fats
    "vegetable oil":            "Edible Oils and Fats",
    "soya oil":                 "Edible Oils and Fats",
    "cooking oil":              "Edible Oils and Fats",
    # Sweeteners
    "sugar":                    "Food Additives",
    # Preserved foods
    "tomato paste":             "Preserved Fruits and Vegetables",
    "tomato":                   "Preserved Fruits and Vegetables",
    # Condiments & seasonings
    "chicken seasoning":        "Condiments/Spices/Seasonings",
    "seasoning":                "Condiments/Spices/Seasonings",
    "spice":                    "Condiments/Spices/Seasonings",
    # Beverages
    "tea":                      "Non-Alcoholic Beverages",
    "juice":                    "Non-Alcoholic Beverages",
    "water":                    "Non-Alcoholic Beverages",
    # Cosmetics & personal care
    "body spray":               "Cosmetics",
    "antiperspirant":           "Cosmetics",
    "deodorant":                "Cosmetics",
    "toothpaste":               "Cosmetics",
    "toilet roll":              "Cosmetics",
    "tissue":                   "Cosmetics",
    "vaseline":                 "Cosmetics",
    "petroleum jelly":          "Cosmetics",
    "lotion":                   "Cosmetics",
    "cream":                    "Cosmetics",
    "soap":                     "Cosmetics",
    "gel":                      "Cosmetics",
}


def _map_to_nafdac_category(scanned_category: str) -> str:
    """
    Map a product name or description to the NAFDAC registered category string.

    Tries substring matching (case-insensitive) against NAFDAC_CATEGORY_MAP.
    If no match is found, the original string is returned and regulatory's semantic
    search fallback will attempt to resolve it.

    Args:
        scanned_category: Product description from client or OCR extraction.

    Returns:
        NAFDAC registered category string, or scanned_category if unmapped.
    """
    lower = scanned_category.lower().strip()
    for keyword, nafdac_cat in NAFDAC_CATEGORY_MAP.items():
        if keyword in lower:
            logger.debug(
                "Category mapped: '%s' -> '%s' (matched keyword: '%s')",
                scanned_category, nafdac_cat, keyword,
            )
            return nafdac_cat

    logger.warning(
        "No NAFDAC category mapping found for '%s'. "
        "Passing through - regulatory semantic search will attempt resolution.",
        scanned_category,
    )
    return scanned_category



class ScanOrchestrator:
    """
    Collects signals from visual, ocr, regulatory and hands them to fusion.
    Creates one NAFDACVerificationAgent at startup (expensive: loads ChromaDB
    and sentence-transformer model once). Reused across all scans.
    """

    def __init__(self):

        logger.info("Initialising ScanOrchestrator — loading A3 agent...")
        self._regulatory_agent = NAFDACVerificationAgent()
        logger.info("ScanOrchestrator ready.")

    def scan(
        self,
        image_path:       str,
        nafdac_no:        str,
        scanned_category: str,
        gps_coordinates:  dict,
        purchase_channel: str,
        receipt_image:    Optional[str] = None,
        storefront_image: Optional[str] = None,
        damage_score:     float = 0.0,
    ) -> PipelineResult:
        """
        Run the full Visual -> OCR -> Regulatory -> Fusion scan pipeline.

        Args:
            image_path:       Absolute path to the product label image.
            nafdac_no:        NAFDAC number. Can be pre-extracted or empty string
                              (Ocr will attempt extraction; regulatory uses Ocr's result).
            scanned_category: Product type hint (e.g. "corn flakes", "body spray").
                              Mapped to NAFDAC category before regulatory call.
            gps_coordinates:  {"lat": float, "lng": float, "accuracy": float}
            purchase_channel: "open_market" | "supermarket" | "pharmacy" |
                              "traffic_vendor" | "online" | "unknown"
            receipt_image:    Optional path/base64 for NAFDAC evidence package.
            storefront_image: Optional path/base64 for NAFDAC evidence package.
            damage_score:     Scan quality from vision DamageDetector — passed to ocr.

        Returns:
            PipelineResult with all verdict fields from fusion's ScanResult.t.
        """
        logger.info(
            "scan() | nafdac_no=%s | category=%s | channel=%s | image=%s",
            nafdac_no, scanned_category, purchase_channel, image_path,
        )

        # Collect ocr signal 
        ocr_signal = self._run_ocr(image_path, damage_score)

        
        # Use Ocr's extracted NAFDAC number if caller did not pre-extract one
        effective_nafdac = nafdac_no or (
            ocr_signal.payload
            .get("metadata", {})
            .get("nafdac_number") or ""
        )

        # Run regulatory ReAct agent
        nafdac_category   = _map_to_nafdac_category(scanned_category)
        regulatory_signal = self._run_regulatory(effective_nafdac, nafdac_category)

        # Collect vision signal 
        vision_signal = self._run_vision(image_path)

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

        # Assemble PipelineResult; all verdict fields from fusion, never computed here
        fusion = fusion_signal.payload

        return PipelineResult(
            vision_signal      = vision_signal,
            ocr_signal         = ocr_signal,
            regulatory_signal  = regulatory_signal,
            fusion_signal      = fusion_signal,
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
            signals_used       = [
                agent for agent in ["visual", "ocr", "reg"]
                if fusion.get("breakdown", {}).get(agent, {}).get("weight", 0) > 0
            ],
        )

    # Agent runners 
    # Each runner packages a signal into an AgentSignal envelope.
    # When a module is not yet integrated, mocked=True and a safe mock payload is used.
    # Switching from mock to real requires only changing the payload - nothing else.

    def _run_ocr(self, image_path: str, damage_score: float) -> AgentSignal:
        """Run OCR. Falls back to mock on any exception."""
        try:
            from ocr_linguistic.pipeline import run_pipeline as ocr_run_pipeline

            logger.info("OCR | image=%s | damage_score=%s", image_path, damage_score)
            result = ocr_run_pipeline(image_path, damage_score)

            logger.info(
                "OCR complete | nafdac=%s | anomaly_score=%s",
                result.get("metadata", {}).get("nafdac_number"),
                result.get("final_text_anomaly_score"),
            )
            return AgentSignal(
                agent_id   = "ocr",
                available  = True,
                confidence = 1.0 - result.get("final_text_anomaly_score", 0.5),
                mocked     = False,
                payload    = result,
            )

        except Exception:
            logger.warning("OCR failed — using mock signal.", exc_info=True)
            return self._mock_ocr_signal()

    def _run_regulatory(self, nafdac_no: str, nafdac_category: str) -> AgentSignal:
        """
        Run regulatory NAFDAC ReAct agent. Always real — never mocked by design.
        On agent failure, returns AGENT_ERROR payload so Fusion's hard override fires.
        """
        try:
            logger.info(
                "Regulatory | nafdac_no=%s | category=%s",
                nafdac_no, nafdac_category,
            )
            verdict = self._regulatory_agent.verify(nafdac_no, nafdac_category)

            logger.info(
                "Regulatory complete | status=%s | score=%s | fallback=%s",
                verdict.status_code, verdict.verification_score, verdict.fallback_used,
            )
            return AgentSignal(
                agent_id   = "regulatory",
                available  = True,
                confidence = verdict.verification_score,
                mocked     = False,
                payload    = {
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
                    "fallback_used":      verdict.fallback_used,
                    "tools_called":       verdict.tools_called,
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

        except Exception:
            logger.error(
                "Regulatory agent failed - returning AGENT_ERROR failsafe.",
                exc_info=True,
            )
            return AgentSignal(
                agent_id   = "regulatory",
                available  = False,
                confidence = 0.0,
                mocked     = False,
                payload    = {
                    "verified":           False,
                    "verification_score": 0.0,
                    "status_code":        "AGENT_ERROR",
                    "severity":           "CRITICAL",
                    "summary":            "Regulatory agent error - regulatory verification unavailable.",
                    "detail":             "The NAFDAC verification agent encountered an error. System fails closed.",
                    "expiry_check":       None,
                    "alignment":          None,
                    "matched_record":     None,
                    "all_records":        [],
                    "fallback_used":      False,
                    "tools_called":       [],
                    "reasoning_trace":    [],
                },
            )

    def _run_vision(self, image_path: str) -> AgentSignal:
        """
        Run Visual pipeline. Falls back to mock on any exception.
        blur_value and damage_score in the payload drive A4's weight selection.
        """
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'visual'))
            from visual.vision_engine.pipeline.visual_pipeline import VisualPipeline

            logger.info("A1 Vision | image=%s", image_path)
            pipeline = VisualPipeline()
            result   = pipeline.analyze(image_path)

            logger.info(
                "Vision complete | product=%s | similarity=%s | "
                "confidence=%s | verdict=%s",
                result.get("product"),
                result.get("Visual Similarity"),
                result.get("confidence"),
                result.get("verdict"),
            )
            return AgentSignal(
                agent_id   = "vision",
                available  = True,
                confidence = result.get("confidence", 0.0),
                mocked     = False,
                payload    = result,
            )

        except Exception:
            logger.warning("Vision faile, using mock signal.", exc_info=True)
            return self._mock_vision_signal()
        
    
    def _run_fusion(
        self,
        vision_signal:     AgentSignal,
        ocr_signal:        AgentSignal,
        regulatory_signal: AgentSignal,
        gps_coordinates:   dict,
        purchase_channel:  str,
        receipt_image:     Optional[str],
        storefront_image:  Optional[str],
        
    ) -> AgentSignal:

        """
        Hand all three signals to fusion. Contains NO scoring logic.
        All weighting, override, damage, and verdict logic lives in fusion.
        """
        from ai_engine.fusion_engine.main import run_scan


        logger.info("Fusion | starting...")
        scan_result = run_scan(
            visual_output    = vision_signal.payload,
            ocr_output       = ocr_signal.payload,
            reg_output       = regulatory_signal.payload,
            gps_coordinates  = gps_coordinates,
            purchase_channel = purchase_channel,
            receipt_image    = receipt_image,
            storefront_image = storefront_image,
        )

        logger.info(
            "Fusion complete | verdict=%s | score=%s | status=%s | weight_mode=%s",
            scan_result.get("verdict"),
            scan_result.get("final_score"),
            scan_result.get("status"),
            scan_result.get("weight_mode"),
        )
        return AgentSignal(
            agent_id   = "fusion",
            available  = True,
            confidence = scan_result.get("final_score", 0.0),
            mocked     = False,
            payload    = scan_result,
        )

    # Mock fallbacks

    def _mock_ocr_signal(self) -> AgentSignal:
        """Neutral mock OCR signal, does not bias fusion's verdict."""
        return AgentSignal(
            agent_id   = "ocr",
            available  = True,
            confidence = MOCK_CONFIDENCE,
            mocked     = True,
            payload    = {
                "source":                   "OCR_MOCK",
                "final_text_anomaly_score": 1.0 - MOCK_CONFIDENCE,
                "ml_score":                 1.0 - MOCK_CONFIDENCE,
                "metadata": {
                    "nafdac_number":      None,
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
                    "rule_score":              1.0 - MOCK_CONFIDENCE,
                    "damage_score_applied":    0.1,
                    "adjusted_ocr_confidence": MOCK_CONFIDENCE,
                    "components":              {},
                },
            },
        )

    def _mock_vision_signal(self) -> AgentSignal:
        """
        Neutral mock vision signal.
        blur_value=80 -> above damage threshold -> fusion uses BASE weights.
        """
        return AgentSignal(
            agent_id   = "vision",
            available  = True,
            confidence = MOCK_CONFIDENCE,
            mocked     = True,
            payload    = {
                "product":           "UNKNOWN — vison not available",
                "Visual Similarity": MOCK_CONFIDENCE,
                "damage_score":      0.1,
                "blur_value":        80.0,
                "confidence":        MOCK_CONFIDENCE,
                "verdict":           "Authentic" if MOCK_CONFIDENCE >= 0.75 else "Suspicious",
            },
        )   



    # Developer utility

    def explain(self, nafdac_no: str, scanned_category: str) -> str:
        """
        Run a full scan with mock A1/A2 (no image needed) and return a formatted
        plain-text report. Useful for demos and the D5 audit panel.
        """
        result = self.scan(
            image_path       = "EXPLAIN_MODE_NO_IMAGE",
            nafdac_no        = nafdac_no,
            scanned_category = scanned_category,
            gps_coordinates  = {"lat": 0.0, "lng": 0.0, "accuracy": 0.0},
            purchase_channel = "unknown",
        )

        regulatory_trace = result.regulatory_signal.payload.get("reasoning_trace", [])
        breakdown        = result.breakdown

        lines = [
            "",
            "SABILENS SCAN — Orchestrator Report",
            "=" * 60,
            f"NAFDAC      : {nafdac_no}",
            f"Category    : {scanned_category}",
            f"Scan ID     : {result.scan_id}",
            f"Status      : {result.status}",
            f"A1 Vision   : {'mocked' if result.vision_signal.mocked else 'real'}",
            f"A2 OCR      : {'mocked' if result.ocr_signal.mocked else 'real'}",
            f"A3 Reg      : real (always)",
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
            f"  Warnings   : {[w.get('type') for w in result.warnings]}",
            "",
        ]
        return "\n".join(lines)


# Test Runner

if __name__ == "__main__":
    import json
    import os
    import sys
    from ai_engine.visual.vision_engine.damage_detection.damage_detector import DamageDetector

    # Pass the left image or side with visual, ocr and regulatory features
    IMAGE = r"C:\Dev\sabilens\ai_engine\visual\test_images\kelloggs_cornflakes_300g+45g_left.jpg"
    
    # Get damage_score from visual and pass it to OCR
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'visual'))
    damage_score = DamageDetector().damage_score(IMAGE)["damage_score"]

    orchestrator = ScanOrchestrator()

    result = orchestrator.scan(
        image_path       = IMAGE,
        nafdac_no        = "",           # let OCR extract it
        scanned_category = "corn flakes",
        gps_coordinates  = {"lat": 6.5244, "lng": 3.3792, "accuracy": 8.5},
        purchase_channel = "open_market",
        damage_score= damage_score,
    )

    print("\n" + "=" * 60)
    print("SABILENS FULL PIPELINE RESULT")
    print("=" * 60)
    print(f"  Verdict    : {result.final_verdict}")
    print(f"  Score      : {result.final_score}")
    print(f"  Severity   : {result.final_severity}")
    print(f"  Action     : {result.action}")
    print(f"  Instruction: {result.simple_instruction}")
    print(f"  Status     : {result.status}")
    print(f"  Scan ID    : {result.scan_id}")
    print(f"  Visual mocked  : {result.vision_signal.mocked}")
    print(f"  OCR mocked  : {result.ocr_signal.mocked}")
    print(f"  Override   : {result.override_applied}")
    print(f"  Warnings   : {[w.get('type') for w in result.warnings]}")
    print(f"  damage_score passed to ocr: {damage_score}")
    print("\nBREAKDOWN:")
    for signal, data in result.breakdown.items():
        print(f"  {signal:<12} score={data.get('raw_score','n/a')}  weight={data.get('weight','n/a')}  weighted={data.get('weighted','n/a')}")
    print("=" * 60)