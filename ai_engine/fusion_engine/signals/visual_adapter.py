# Normalizes Visual output -> FusionSignal

"""
This file contains the Fusion Engine's  Visual Signal Adapter

Normalises the output of VisualPipeline.analyze() into a
standard FusionSignal that Fusion engine can consume directly.

Visual OUTPUT CONTRACT (visual_pipeline.py):
  {
      "product":           str,    # Best matched product name from embedding store
      "Visual Similarity": float,  # 0.0–1.0 raw cosine similarity (pre-damage)
      "damage_score":      float,  # 0.1=sharp | 0.4=moderate | 0.8=heavy blur
      "blur_value":        float,  # Raw Laplacian variance — from DamageDetector
      "confidence":        float,  # 0.0–1.0 = similarity * (1 - damage_score)
      "verdict":           str,    # "Authentic" | "Suspicious" | "Fake"
  }

SCORE DIRECTION: confidence 1.0 = authentic - same as fusion engine. No flip needed.
ADAPTER FORMULA: fusion_score = confidence (0.0-1.0, no scale change)


DAMAGE HANDLING:
  damage_score and blur_value are forwarded to fusion_engine.py.
  fusion_engine uses them to:
    1. Select the correct weight set (BASE / DAMAGED / FALLBACK)
    2. Trigger RESCAN_REQUIRED if blur_value < EXTREME_BLUR_CEILING
    3. Store in evidence for NAFDAC reporting and image retraining pipeline

  Fusion does NOT re-apply damage_score to fusion_score.
  Visual's confidence is already damage-adjusted by visual_pipeline.analyze().

HARD OVERRIDE:
  raw_similarity < LOGO_MATCH_FLOOR_THRESHOLD (0.20)
  - override_flag = True
  - fusion_engine floors verdict to SUSPICIOUS

BACKWARD COMPATIBILITY:
  blur_value defaults to 60.0 (sharp) if absent.
  This allows old visual outputs to pass through safely during the
  transition period before damage_detector.py is updated.
  A warning is appended to the validation errors list.

SCALABILITY NOTES:
  - Add new override conditions here as new threat patterns are identified.
  - Do not add scoring logic — scoring belongs in fusion_engine.py.
  - If A1 adds new output fields, extend this adapter and update schema.py.
"""

from datetime import datetime, timezone
from ai_engine.fusion_engine.config.thresholds import LOGO_MATCH_FLOOR_THRESHOLD

def adapt(visual_output: dict) -> dict:
    """
    Normalise VisualPipeline output into a standard Fusion engine signal.

    Args:
        visual_output: Raw dict from VisualPipeline.analyze()

    Returns:
        FusionSignal dict with all fields fusion_engine.run_fusion() needs.
    """
    confidence      = float(visual_output.get("confidence",        0.0))
    raw_similarity  = float(visual_output.get("Visual Similarity", 0.0))
    damage_score    = float(visual_output.get("damage_score",      0.1))
    # Default 60.0 (sharp) preserves backward compat with pre-update visual ouputs
    blur_value      = float(visual_output.get("blur_value",        60.0))
    product_matched = visual_output.get("product",  "UNKNOWN")
    visual_verdict      = visual_output.get("verdict",  "Fake")

    # Fusion score; no flip, no re-apply of damage 
    fusion_score = round(confidence, 4)

    # Hard override: if logo similarity is critically low, escalate to SUSPICIOUS floor
    # Mirrors the override rule in config/thresholds.py → OVERRIDES["logo_match_suspicious_threshold"]
    override_flag   = False
    override_reason = None

    if raw_similarity < LOGO_MATCH_FLOOR_THRESHOLD:
        override_flag   = True
        override_reason = (
            f"Visual: raw logo similarity ({raw_similarity:.3f}) is below the "
            f"{LOGO_MATCH_FLOOR_THRESHOLD} minimum threshold. "
            f"Product fails minimum visual match - verdict floored to SUSPICIOUS."
        )


    return {
        "source":          "VISUAL",
        "fusion_score":    fusion_score, # 0.0-1.0 positive direction
        "raw_confidence":  round(confidence, 4),
        "raw_similarity":  round(raw_similarity, 4),
        "damage_score":    round(damage_score, 4),
        "blur_value":      round(blur_value,   4),
        "product_matched": product_matched,
        "Visual_verdict":      visual_verdict,
        "override_flag":   override_flag,
        "override_reason": override_reason,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
    }


def validate(visual_output: dict) -> list[str]:
    """
    Check that Visual output has all required fields before adaptation.
    Returns a list of missing/invalid field names (empty = valid).
    """
    texts = []
    required = ["confidence", "Visual Similarity", "damage_score", "product", "verdict"]

    for field in required:
        if field not in visual_output:
            texts.append(f"Missing field: '{field}'")

    # blur_value: expected but not blocking (adapter defaults to 60.0)
    if "blur_value" not in visual_output:
        texts.append(
            "WARNING: 'blur_value' missing from A1 output. "
            "Update damage_detector.py and visual_pipeline.py. "
            "Defaulting to 60.0 (sharp) - RESCAN_REQUIRED logic will not fire correctly."
        )

    confidence = visual_output.get("confidence", -1)
    if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
        texts.append(f"'confidence' must be float in [0.0, 1.0], got: {confidence!r}")

    similarity = visual_output.get("Visual Similarity", -1)
    if not isinstance(similarity, (int, float)) or not (0.0 <= float(similarity) <= 1.0):
        texts.append(f"'Visual Similarity' must be float in [0.0, 1.0], got: {similarity!r}")

    verdict = visual_output.get("verdict", "")
    if verdict not in {"Authentic", "Suspicious", "Fake"}:
        texts.append(
            f"'verdict' must be 'Authentic', 'Suspicious', or 'Fake' (Title case), "
            f"got: {verdict!r}"
        )

    return texts