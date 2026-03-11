"""
This file contains the Fusion Engine's Main Entry Point

Single entry point for the entire A4 pipeline.
The FastAPI backend calls run_scan() with the three signal payloads
and GPS/purchase metadata. Everything else is handled internally.

CALL FLOW:
  FastAPI Backend
      │
      ▼
  run_scan()                        <- THIS FILE
      │
      ├── validate_inputs()         <-  gate check before any processing
      │
      ├── visual_adapter.adapt()    <-  normalise VISUAL signal
      ├── ocr_adapter.adapt()       <-  normalise OCR signal (+ invert score)
      ├── reg_adapter.adapt()       <-  normalise REGULATORY signal
      │
      ├── fusion_engine.run_fusion()    <-  weighted scoring + overrides
      ├── decision_classifier.classify() <-  verdict → action + N-ATLAS strings
      │
      ├── evidence_packager.package()   <-  if FAKE or user opts to report
      │
      └── return ScanResult

INTEGRATION CONTRACT:
  Input:  Three raw signal dicts (VISUAL, OCR, reg) + GPS + purchase metadata
  Output: One clean ScanResult dict consumed by the FastAPI response layer

ERROR HANDLING STRATEGY:
  - Validation errors  -> raise ValueError (FastAPI returns 422)
  - Adapter failures    -> logged, signal defaulted to worst-case (0.0 score)
  - Packager failure    -> logged, scan result returned without evidence package
  - Any unhandled error -> logged, returns a FAIL-SAFE result (verdict=FAKE)
    The system fails closed - a crash never returns AUTHENTIC.
"""

import traceback
from datetime import datetime, timezone

from signals.visual_adapter   import adapt as visual_adapt,  validate as visual_validate
from signals.ocr_adapter      import adapt as ocr_adapt,     validate as ocr_validate
from signals.reg_adapter      import adapt as reg_adapt,     validate as reg_validate
from core.fusion_engine       import run_fusion
from core.decision_classifier import classify
from core.evidence_packager   import package
from utils.logger             import setup_logger

logger = setup_logger("A4_FusionEngine")


# Fail-safe signal defaults 
# Used when an upstream signal is missing, invalid, or causes an adapter crash.
# DESIGN RULE: these must ALWAYS produce a FAKE verdict when adapted.
# Never relax these values - their purpose is to guarantee fail-closed behaviour.

_FAILSAFE_VISUAL = {
    "product":           "UNKNOWN",
    "Visual Similarity": 0.0,
    "damage_score":      0.1,        # Not extreme blur - RESCAN_REQUIRED must not fire
    "blur_value":        60.0,       # Sharp image assumption - so score, not rescan, fires
    "confidence":        0.0,        # 0.0 confidence → FAKE verdict
    "verdict":           "Fake",
}

_FAILSAFE_OCR = {
    "source":                   "OCR_FAILSAFE",
    "metadata":                 {},
    "brand_anomaly":            {},
    "structural_validation":    {},
    "rule_score":               {},
    "ml_score":                 1.0,  # Maximum anomaly
    "final_text_anomaly_score": 1.0,  # Maximum anomaly → fusion_score=0.0 after inversion
}

_FAILSAFE_REG = {
    "verified":           False,
    "verification_score": 0.0,
    "status_code":        "NOT_FOUND",  # Triggers HARD_FAKE override in fusion_engine
    "severity":           "CRITICAL",
    "summary":            "Signal unavailable - treated as NOT_FOUND.",
    "detail":             "Regulatory signal could not be retrieved. System fails closed.",
    "expiry_check":       None,
    "alignment":          None,
    "matched_record":     None,
    "all_records":        [],
    "fallback_used":      False,
    "tools_called":       [],
    "reasoning_trace":    [],
}


# Public entry point 

def run_scan(
    visual_output:        dict,
    ocr_output:        dict,
    reg_output:        dict,
    gps_coordinates:  dict = None,
    purchase_channel: str  = "unknown",
    receipt_image:    str  = None,
    storefront_image: str  = None,
    package_evidence: bool = True,
) -> dict:
    """
    Run the complete A4 Fusion Engine pipeline for one product scan.

    Args:
        visual_output:        Raw dict from VisualPipeline.analyze()
        ocr_output:        Raw dict from pipeline.run_pipeline()
        reg_output:        Raw dict from agent_scorer.compute_verification_score()
        gps_coordinates:  GPS lock: {"lat": float, "lng": float, "accuracy": float}
        purchase_channel: Where product was purchased. See evidence_packager options.
        receipt_image:    Optional receipt photo - file path or base64 string.
        storefront_image: Optional storefront photo - file path or base64 string.
        package_evidence: Set False to skip evidence packaging (CI dry-run mode).

    Returns:
        ScanResult dict:
        {
            "status":             "SUCCESS" | "PARTIAL" | "FAILSAFE" | "RESCAN_REQUIRED",
            "scan_id":            str,
            "verdict":            "AUTHENTIC" | "SUSPICIOUS" | "FAKE" | "RESCAN_REQUIRED",
            "action":             "BUY" | "CAUTION" | "DO NOT BUY" | "RESCAN",
            "final_score":        float | None,
            "severity":           str,
            "confidence_label":   str,
            "report_priority":    "AUTO" | "PROMPT" | "NONE",
            "simple_instruction": str,
            "atlas_instruction":  str,
            "atlas_summary":      str,
            "override_applied":   bool,
            "override_summary":   str | None,
            "warnings":           list,
            "breakdown":          dict,
            "weight_mode":        str | None,
            "evidence_package":   dict | None,
            "errors":             list,
            "timestamp":          str,
        }
    """
    errors     = []
    status     = "SUCCESS"
    scan_start = datetime.now(timezone.utc).isoformat()

    logger.info(f"run_scan() started | purchase_channel={purchase_channel}")

    try:
        # Validate and adapt all three signals 
        visual_signal = _safe_adapt("VISUAL", visual_output, _FAILSAFE_VISUAL, visual_validate, visual_adapt, errors)
        ocr_signal = _safe_adapt("OCR", ocr_output, _FAILSAFE_OCR, ocr_validate,    ocr_adapt,    errors)
        reg_signal = _safe_adapt("REG", reg_output, _FAILSAFE_REG, reg_validate,    reg_adapt,    errors)

        if errors:
            status = "PARTIAL"
            logger.warning(f"Signal validation errors ({len(errors)}): {errors}")

        # Run fusion engine 
        logger.info("Running fusion engine...")
        fusion_result = run_fusion(visual_signal, ocr_signal, reg_signal)

        # Handle RESCAN_REQUIRED early exit 
        if fusion_result.get("verdict") == "RESCAN_REQUIRED":
            logger.info(
                f"RESCAN_REQUIRED | "
                f"blur_value={visual_signal.get('blur_value')} | "
                f"damage_score={visual_signal.get('damage_score')}"
            )
            return _rescan_result(fusion_result, scan_start, errors)

        # Run decision classifier 
        logger.info("Running decision classifier...")
        classification = classify(fusion_result)

        scan_id = classification.get("scan_id", "UNKNOWN")
        verdict = classification.get("verdict", "FAKE")

        logger.info(
            f"scan_id={scan_id} | "
            f"verdict={verdict} | "
            f"score={classification.get('final_score')} | "
            f"weight_mode={fusion_result.get('weight_mode')} | "
            f"override={classification.get('override_applied')}"
        )

        # Package evidence if needed 
        evidence_package = None
        report_priority  = classification.get("report_priority", "NONE")
        should_package   = (
            package_evidence and
            report_priority in {"AUTO", "PROMPT"}
        )

        if should_package:
            logger.info(f"Packaging evidence | report_priority={report_priority}")
            try:
                evidence_package = package(
                    classification   = classification,
                    gps_coordinates  = gps_coordinates or {},
                    purchase_channel = purchase_channel,
                    receipt_image    = receipt_image,
                    storefront_image = storefront_image,
                )
                logger.info(
                    f"Evidence packaged | "
                    f"enforcement={evidence_package.get('enforcement_action')} | "
                    f"hash={evidence_package.get('integrity_hash', '')[:16]}..."
                )
            except Exception:
                msg = "Evidence packaging failed"
                errors.append(msg)
                logger.error(f"{msg}:\n{traceback.format_exc()}")
                status = "PARTIAL"

        # Assemble and return ScanResult 
        return {
            "status":             status,
            "scan_id":            scan_id,
            "verdict":            verdict,
            "action":             classification.get("action"),
            "final_score":        classification.get("final_score"),
            "severity":           classification.get("severity"),
            "confidence_label":   classification.get("confidence_label"),
            "report_priority":    report_priority,
            "simple_instruction": classification.get("simple_instruction"),
            "atlas_instruction":  classification.get("atlas_instruction"),
            "atlas_summary":      fusion_result.get("atlas_summary", ""),
            "override_applied":   classification.get("override_applied"),
            "override_summary":   classification.get("override_summary"),
            "warnings":           classification.get("warnings",  []),
            "breakdown":          classification.get("breakdown", {}),
            "weight_mode":        fusion_result.get("weight_mode"),
            "evidence_package":   evidence_package,
            "errors":             errors,
            "timestamp":          scan_start,
        }

    except Exception:
        logger.critical(f"Unhandled exception in run_scan():\n{traceback.format_exc()}")
        return _failsafe_result(scan_start)


# Private helpers 

def _safe_adapt(
    label:       str,
    raw:         dict,
    failsafe:    dict,
    validate_fn,
    adapt_fn,
    errors:      list,
) -> dict:
    """
    Validate and adapt one upstream signal.

    On any validation failure or adapter exception:
      - Appends an error message to the errors list
      - Adapts the failsafe signal and returns it

    This guarantees run_fusion() always receives three structurally valid signals.
    The failsafe signals are calibrated to produce FAKE - never AUTHENTIC.

    Args:
        label:       Signal identifier for error messages ("VISUAL", "OCR", "REG").
        raw:         Raw signal dict from the upstream module.
        failsafe:    Worst-case fallback dict if raw is invalid.
        validate_fn: Adapter's validate() function.
        adapt_fn:    Adapter's adapt() function.
        errors:      Shared list - errors are appended in place.

    Returns:
        Adapted FusionSignal dict (from raw or from failsafe).
    """
    try:
        validation_messages = validate_fn(raw or {})

        # Treat any error (not WARNING-prefixed) as blocking
        blocking = [m for m in validation_messages if not m.startswith("WARNING:")]
        if blocking:
            msg = f"{label} signal invalid: {blocking}"
            errors.append(msg)
            logger.warning(msg + " - using failsafe signal")
            return adapt_fn(failsafe)

        # Log warnings without blocking
        for w in validation_messages:
            if w.startswith("WARNING:"):
                logger.warning(f"{label} adapter: {w}")

        return adapt_fn(raw)

    except Exception:
        msg = f"{label} adapter crashed"
        errors.append(msg)
        logger.error(f"{msg}:\n{traceback.format_exc()}")
        return adapt_fn(failsafe)


def _rescan_result(fusion_result: dict, timestamp: str, errors: list) -> dict:
    """
    Build the ScanResult for a RESCAN_REQUIRED outcome.

    No evidence package is generated. No NAFDAC report is filed.
    The image save flag is embedded in the fusion_result evidence.

    Args:
        fusion_result: The RESCAN_REQUIRED dict from fusion_engine.
        timestamp:     Scan start timestamp string.
        errors:        Any non-fatal errors accumulated so far.

    Returns:
        ScanResult dict with status="RESCAN_REQUIRED".
    """
    rescan_warning = fusion_result.get("warnings", [{}])[0] if fusion_result.get("warnings") else {}

    return {
        "status":             "RESCAN_REQUIRED",
        "scan_id":            "RESCAN",
        "verdict":            "RESCAN_REQUIRED",
        "action":             "RESCAN",
        "final_score":        None,
        "severity":           "NONE",
        "confidence_label":   "NONE",
        "report_priority":    "NONE",
        "simple_instruction": (
            "We could not read this product clearly. "
            "Please hold your phone steady in good lighting and try again."
        ),
        "atlas_instruction":  fusion_result.get("warnings", [{}])[0].get("message", "")
                              if fusion_result.get("warnings") else "",
        "atlas_summary":      "",
        "override_applied":   False,
        "override_summary":   None,
        "warnings":           fusion_result.get("warnings", []),
        "breakdown":          {},
        "weight_mode":        "REJECTED",
        "evidence_package":   None,          # No NAFDAC report for bad scans
        "rescan_evidence":    fusion_result.get("evidence", {}),  # Saved for retraining pipeline
        "errors":             errors,
        "timestamp":          timestamp,
    }


def _failsafe_result(timestamp: str) -> dict:
    """
    Absolute last-resort result when run_scan() itself crashes.

    Called only when an unhandled exception propagates past all try/except blocks.
    The system ALWAYS returns FAKE on catastrophic failure - never AUTHENTIC.
    Designed to be parseable by Backend even when it contains no useful data.

    Args:
        timestamp: Scan start timestamp string.

    Returns:
        Minimal ScanResult dict with status="FAILSAFE" and verdict="FAKE".
    """
    return {
        "status":             "FAILSAFE",
        "scan_id":            "FAILSAFE",
        "verdict":            "FAKE",
        "action":             "DO NOT BUY",
        "final_score":        0.0,
        "severity":           "CRITICAL",
        "confidence_label":   "VERY LOW",
        "report_priority":    "AUTO",
        "simple_instruction": "We could not verify this product. Do not buy it.",
        "atlas_instruction":  "We could not verify this product. Do not buy it.",
        "atlas_summary":      "",
        "override_applied":   False,
        "override_summary":   None,
        "warnings":           [],
        "breakdown":          {},
        "weight_mode":        None,
        "evidence_package":   None,
        "errors":             ["CRITICAL: run_scan() encountered an unhandled exception."],
        "timestamp":          timestamp,
    }