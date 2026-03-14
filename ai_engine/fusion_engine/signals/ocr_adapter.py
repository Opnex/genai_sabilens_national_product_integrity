# Normalizes OCR output -> FusionSignal

"""
This file contains the Fusion Engine's OCR/Linguistic Signal Adapter

Normalises the output of pipeline.run_pipeline() into a
standard FusionSignal that Fusion engine can consume directly.

OCR OUTPUT CONTRACT (pipeline.py):
{
    "source":                  "OCR_Linguistic",
    "metadata":                dict,   # product_name, nafdac_number, batch_number,
                                       # expiry_date, avg_ocr_confidence, brand_detected, etc.
    "brand_anomaly":           dict,   # brand_detected, similarity_score, brand_anomaly_flag,
                                       # lookalike_corrections
    "structural_validation":   dict,   # missing_fields, structural_score,
                                       # expiry_format_valid, batch_format_valid
    "rule_score":              dict,   # rule_score (0-1, ANOMALY), components, damage_score_applied
    "ml_score":                float,  # 0-1 (ANOMALY score)
    "final_text_anomaly_score": float  # 0-1 (ANOMALY - higher = worse)
}

SCORE DIRECTION: final_text_anomaly_score 1.0 = FAKE (INVERTED vs Fusion engine)
ADAPTER FORMULA: fusion_score = 1 - final_text_anomaly_score

DAMAGE NOTE_:
  OCR applies damage_score internally before producing final_text_anomaly_score.
  The adapter reads damage_score_applied for audit purposes only.
  A4 must NEVER re-apply damage — it would double-penalise the score.

HARD OVERRIDE:
  nafdac_number = None (OCR could not extract NAFDAC from label)
  - override_flag = True
  - fusion_engine floors verdict to SUSPICIOUS

KEY FIELDS FOR DOWNSTREAM:
  lookalike_corrections : evidence_packager counterfeit fingerprint
  missing_fields        : evidence_packager label anomaly report
  brand_anomaly_flag    : evidence_packager detection signals

SCALABILITY NOTES:
  - If OCR adds new anomaly signals, extract them here and add to the return dict.
  - Do not add scoring logic — scoring belongs in fusion_engine.py.
  - The inversion (1 - score) must remain here — fusion_engine expects 1.0 = authentic.
"""

from datetime import datetime, timezone


def adapt(ocr_output: dict) -> dict:
    """
    Normalise OCR pipeline output into a standard Fusion engine signal.

    Args:
        ocr_output: Raw dict from pipeline.run_pipeline()

    Returns:
        FusionSignal dict:
        {
            "source":                str,
            "fusion_score":          float,   # 0.0-1.0 (higher = more authentic)
            "raw_anomaly_score":     float,   # OCR's original 0-1 anomaly score (preserved)
            "rule_score":            float,   # OCR's rule engine component
            "ml_score":              float,   # OCR's ML component
            "nafdac_number":         str | None,
            "brand_detected":        str | None,
            "brand_anomaly_flag":    int,     # 0 or 1
            "brand_similarity":      float,
            "lookalike_corrections": list,    # Evidence for counterfeit fingerprint
            "structural_score":      float,
            "missing_fields":        list,
            "avg_ocr_confidence":    float,
            "damage_already_applied": float,  
            "override_flag":         bool,
            "override_reason":       str | None,
            "timestamp":             str,
        }
    """
    metadata             = ocr_output.get("metadata", {})
    brand_anomaly        = ocr_output.get("brand_anomaly", {})
    structural           = ocr_output.get("structural_validation", {})
    rule_score_obj       = ocr_output.get("rule_score", {})
    raw_anomaly_score    = float(ocr_output.get("final_text_anomaly_score", 1.0))
    ml_score             = float(ocr_output.get("ml_score", 1.0))

    # INVERT: anomaly : authenticity
    fusion_score = round(1.0 - raw_anomaly_score, 4)

    # Extract key fields for override checks and evidence packaging
    nafdac_number        = metadata.get("nafdac_number")
    brand_detected       = metadata.get("brand_detected") or brand_anomaly.get("brand_detected")
    brand_anomaly_flag    = int(brand_anomaly.get("brand_anomaly_flag", 0))
    brand_similarity      = float(brand_anomaly.get("similarity_score", 0.0))
    lookalike_corrections = list(brand_anomaly.get("lookalike_corrections", []))
    structural_score      = float(structural.get("structural_score",   0.0))
    missing_fields        = list(structural.get("missing_fields",      []))
    avg_ocr_confidence    = float(metadata.get("avg_ocr_confidence",   0.0))
    damage_applied        = float(rule_score_obj.get("damage_score_applied", 0.0))
    rule_score            = float(rule_score_obj.get("rule_score",           1.0))


    # Override: NAFDAC number not found by OCR : floor to SUSPICIOUS minimum
    override_flag   = False
    override_reason = None

    if not nafdac_number:
        override_flag   = True
        override_reason = (
            "OCCR could not extract a valid NAFDAC number from the label. "
            "No valid NAFDAC number could be extracted from the label. "
            "This may indicate a damaged label, an unregistered product, or a counterfeit label that omits the NAFDAC number. "
            "Verdict floored to SUSPICIOUS regardless of visual score."
        )

    return {
        "source":                  "OCR",
        "fusion_score":            fusion_score,
        "raw_anomaly_score":       round(raw_anomaly_score, 4),
        "rule_score":             round(rule_score,        4),
        "ml_score":               round(ml_score,          4),
        "avg_ocr_confidence":     round(avg_ocr_confidence,4),
        "damage_already_applied": round(damage_applied,    4),
        "nafdac_number":           nafdac_number,
        "brand_detected":          brand_detected,
        "brand_anomaly_flag":      brand_anomaly_flag,
        "brand_similarity":        round(brand_similarity, 4),
        "lookalike_corrections":   lookalike_corrections,
        "structural_score":        round(structural_score, 4),
        "missing_fields":          missing_fields,
        "override_flag":           override_flag,
        "override_reason":         override_reason,
        "timestamp":               datetime.now(timezone.utc).isoformat(),
    }


def validate(ocr_output: dict) -> list[str]:
    """
    Check that OCR output has all required fields before adaptation.
    Returns a list of missing/invalid field names (empty = valid).
    """
    errors = []
    required_keys = [
        "metadata", "brand_anomaly", "structural_validation",
        "rule_score", "ml_score", "final_text_anomaly_score"
    ]

    for key in required_keys:
        if key not in ocr_output:
            errors.append(f"Missing top-level key: '{key}'")

    score = ocr_output.get("final_text_anomaly_score", -1)
    if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
        errors.append(
            f"'final_text_anomaly_score' must be float in [0.0, 1.0], got: {score!r}"
        )

    return errors