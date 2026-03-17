"""
SabiLens - A2: Anomaly Scorer
===============================
Handles:
  - Combining all A2 signals into a single text anomaly score
  - Applying A1's damage score to adjust OCR confidence
  - Assigning risk levels (LOW / MEDIUM / HIGH)

This module produces the final output that feeds into the A4 Fusion Engine.
Think of it as A2's verdict layer.
"""

from .config import (
    WEIGHTS,
    OCR_CONFIDENCE_THRESHOLD,
)


def compute_rule_score(metadata: dict, damage_score: float = 0.0) -> dict:

    score = 0.0
    components = {}

    # -----------------------------
    # 1. Brand Anomaly (High Impact)
    # -----------------------------
    if metadata.get("brand_anomaly_flag", 0) == 1:
        score += 0.35
        components["brand_component"] = 0.35
    else:
        components["brand_component"] = 0.0

    # -----------------------------
    # 2. Regulatory Checks
    # -----------------------------
    if not metadata.get("nafdac_number"):
        score += 0.25
        components["nafdac_component"] = 0.25
    else:
        components["nafdac_component"] = 0.0

    if not metadata.get("expiry_format_valid", False):
        score += 0.15

    if not metadata.get("batch_format_valid", False):
        score += 0.10

    # -----------------------------
    # 3. Structural Score
    # -----------------------------
    structural_score = metadata.get("structural_score", 1.0)
    structural_penalty = (1 - structural_score) * 0.25
    score += structural_penalty
    components["structural_component"] = round(structural_penalty, 4)

    # -----------------------------
    # 4. OCR Confidence
    # -----------------------------
    ocr_conf = metadata.get("avg_ocr_confidence", 1.0)

    if ocr_conf < 0.85:
        score += 0.15
        components["confidence_component"] = 0.15
    elif ocr_conf < 0.92:
        score += 0.07
        components["confidence_component"] = 0.07
    else:
        components["confidence_component"] = 0.0

    # -----------------------------
    # 5. External Damage Signal
    # -----------------------------
    score += damage_score * 0.3

    final_score = round(min(score, 1.0), 4)

    return {
        "rule_score": final_score,
        "components": components,
        "damage_score_applied": damage_score,
        "adjusted_ocr_confidence": round(ocr_conf, 4),
    }