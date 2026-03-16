# AUTHENTIC ≥80, SUSPICIOUS 50–79, FAKE <50

"""
Fusion Engine - Decision Thresholds

Maps the final weighted fusion score (0-100) to a verdict.
Score thresholds, verdict bands, severity levels, and confidence labels
for the A4 Fusion Engine.

SCORE SCALE: 0.0 - 1.0 (aligned to orchestrator/pipeline.py)

VERDICT BANDS:
  ┌─────────────────────────────────────────────────────┐
  │  >= 0.72  ->  AUTHENTIC         Safe to purchase    │
  │  0.45-0.74 ->  SUSPICIOUS       Proceed with caution│
  │  < 0.45   ->  FAKE              Do not buy. Report. │
  └─────────────────────────────────────────────────────┘

HARD OVERRIDE RULES (bypass score entirely — set in reg_adapter / ocr_adapter):
  Regulatory status in {NOT_FOUND, SUBCATEGORY_MISMATCH, AGENT_ERROR} ->    force FAKE
  OCR nafdac_number = None                                      -> floor SUSPICIOUS
  visual_similarity < 0.20                                      ->floor SUSPICIOUS

DAMAGE IS NOT AN OVERRIDE:
  damage_score and blur_value affect WEIGHTS only — never verdict directly.
  A blurry photo of a real product must never be forced to FAKE.

SCALABILITY NOTES:
  - Threshold values are tuned after each evaluation sprint.
  - Do not hard-code 0.75 or 0.45 anywhere outside this file.
  - All code must call get_verdict(score) — never compare scores inline.
  - RESCAN_REQUIRED is a special non-verdict state handled in fusion_engine.py.
    It is not scored and does not appear in THRESHOLDS.
"""

# Primary Score Thresholds (0.0 - 1.0)
THRESHOLD_AUTHENTIC  = 0.72   # score >= 0.75 -> AUTHENTIC
THRESHOLD_SUSPICIOUS = 0.45   # score 0.45-0.74 -> SUSPICIOUS
                               # score < 0.45   -> FAKE

# Verdict Labels 
VERDICT_AUTHENTIC  = "AUTHENTIC"
VERDICT_SUSPICIOUS = "SUSPICIOUS"
VERDICT_FAKE       = "FAKE"

# Severity Mapping 
SEVERITY_MAP = {
    VERDICT_AUTHENTIC:  "NONE",
    VERDICT_SUSPICIOUS: "MEDIUM",
    VERDICT_FAKE:       "CRITICAL",
}

# Suspicious floor score 
# Applied when a SUSPICIOUS floor override fires (Visual logo too low / OCR no NAFDAC).
# Score is clamped to this value — never lower, never higher than THRESHOLD_AUTHENTIC.
SUSPICIOUS_FLOOR_SCORE = THRESHOLD_SUSPICIOUS   # 0.45

# Confidence labels 
# Human-readable confidence description shown to audit panel and mobile UI.
# Bands are inclusive on both ends. Evaluated top-down, first match wins.
CONFIDENCE_BANDS = [
    (0.90, 1.00, "VERY HIGH"),
    (0.72, 0.89, "HIGH"),
    (0.55, 0.74, "MODERATE"),
    (0.35, 0.54, "LOW"),
    (0.00, 0.34, "VERY LOW"),
]

# Override conditions (informational enforced in the three adapters) 
CRITICAL_REG_STATUSES       = {"NOT_FOUND", "SUBCATEGORY_MISMATCH", "AGENT_ERROR", "EXPIRED"}
LOGO_MATCH_FLOOR_THRESHOLD = 0.20   # visual raw_similarity below this -> SUSPICIOUS floor
EXTREME_BLUR_CEILING       = 5.0    # blur_value below this -> RESCAN_REQUIRED
DAMAGED_SCORE_FLOOR        = 0.40   # damage_score at or above -> DAMAGED weight mode


def get_confidence_label(score: float) -> str: # Return a readable confidence label for a fusion score.
    for low, high, label in CONFIDENCE_BANDS:
        if low <= score <= high:
            return label
    return "VERY LOW"


def get_verdict(score: float) -> str: # Map a fusion score (0.0-1.0) to a verdict label.
    if score >= THRESHOLD_AUTHENTIC:
        return VERDICT_AUTHENTIC
    if score >= THRESHOLD_SUSPICIOUS:
        return VERDICT_SUSPICIOUS
    return VERDICT_FAKE



def get_severity(verdict: str) -> str: # Returns the severity level for a given verdict.
    return SEVERITY_MAP.get(verdict, "CRITICAL")
