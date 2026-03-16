"""
Signal Weight Configuration

Defines three weight sets. Fusion selects ONE per scan based on
scan quality (blur_value, damage_score) and Regulatory retrieval path.

WEIGHT SELECTION DECISION TREE (handled by fusion_engine._resolve_weights()):

  ┌────────────────────────────────────────────────────────────────────┐
  │ damage_score >= 0.4 (blur_value < 60)                              │
  │   -> SIGNAL_WEIGHTS_DAMAGED                                        │
  │     visual is blur-compromised. regulatory(RAG) takes authority.   |                 │
  │     Applies regardless of retrieval_path.                          │
  ├────────────────────────────────────────────────────────────────────┤
  │ damage_score = 0.1 AND fallback_used = True                        │
  │   -> SIGNAL_WEIGHTS_FALLBACK                                       │
  │     Image is sharp but regulatory(RAG) used semantic search        |
  |     (not exact NAFDAC).                                            │
  │     regulatory(RAG) is uncertain. Visual and OCR lead.             |                 │
  ├────────────────────────────────────────────────────────────────────┤
  │ damage_score = 0.1 AND fallback_used = False                       │
  │   -> SIGNAL_WEIGHTS (base)                                         │
  │     Best case. Sharp image, exact NAFDAC match. Full confidence.   │
  └────────────────────────────────────────────────────────────────────┘

SPECIAL CASE - RESCAN_REQUIRED (no weights used):
  damage_score = 0.8 AND blur_value < 5.0
  Image is too degraded to produce any verdict.
  Scan is rejected. Image is saved for model retraining.
  This is handled in fusion_engine.py before weight selection.

SCALABILITY NOTES:
  - Add new weight sets here as new threat scenarios are identified.
  - All weight sets must pass validate_weights() before deployment.
  - Weight tuning should be driven by evaluation sprint results.
  - Sub-weights (VISUAL_SUB, OCR_SUB, REG_SUB) are reserved for when each
    module exposes component-level scores to Fusion.

WHY THESE VALUES:

  BASE (visual=0.40, ocr=0.35, reg=0.25):
    Vision-first because pixel-level logo comparison is the hardest
    signal for a super-fake counterfeiter to replicate perfectly.
    A3 is reduced from the original 0.40 because super-fakes now
    carry real NAFDAC numbers - reg alone cannot catch them.

  DAMAGED (visual=0.15, ocr=0.30, reg=0.55):
    Blur destroys A1 logo comparison entirely.
    A3 takes over because DB lookup needs only the NAFDAC number
    string - it does not care about image quality at all.

  FALLBACK (visual=0.475, ocr=0.425, reg=0.10):
    Agent could not do exact NAFDAC lookup — used semantic search.
    Regulatory's confidence is low. Visual and OCR are the reliable signals.
    regulatory retains a small weight (0.10) so near-NAFDAC matches still
    contribute without dominating the verdict.
"""
# Mode: "BASE"
# Condition: damage_score=0.1 AND retrieval_path="nafdac_exact"
SIGNAL_WEIGHTS = {
    "visual":      0.40,   # Visual Fingerprinting (logo, layout, color); Forensic (hardest to fake at pixel level)
    "ocr":         0.35,   # OCR confirms NAFDAC number, batch, expiry, brand
    "reg":         0.25,   # Agentic RAG + Categorical Alignment (DB verification supports)
}

# Damaged weights: blurry scan
# Mode: "DAMAGED"
# Condition: damage_score >= 0.4 (blur_value < 60 from DamageDetector)
# Priority: DAMAGED always overrides FALLBACK if both conditions are true.
SIGNAL_WEIGHTS_DAMAGED = {
    "visual": 0.15,   # Penalised Laplacian blur degrades logo comparison severely
    "ocr":    0.30,   # Partial OCR confidence degrades but NAFDAC number may survive
    "reg":    0.55,   # Takes over DB lookup needs number string only, not image quality
}

# Fallback weights - semantic search path
# Mode: "FALLBACK"
# Condition: damage_score=0.1 AND retrieval_path="semantic_fallback" (fallback_used=True)
SIGNAL_WEIGHTS_FALLBACK = {
    "visual": 0.475,  # It leads if image is sharp, forensic vision is fully reliable
    "ocr":    0.425,  # Confirms if OCR is clean, text evidence is trustworthy
    "reg":    0.10,   # Reduced if semantic match is a guess, not a hard DB lookup
}

# Sub-signal weights WITHIN OCR layer
OCR_SUB_WEIGHTS = {
    "nafdac_number":  0.50,   # Core regulatory ID — highest priority
    "batch_number":   0.25,   # Traceability signal
    "expiry_date":    0.15,   # Tamper indicator
    "linguistic":     0.10,   # Label language/grammar coherence
}

# Sub-signal weights WITHIN Visual layer
VISUAL_SUB_WEIGHTS = {
    "logo_match":     0.40,   # Logo pixel similarity vs Master Artwork
    "font_match":     0.30,   # Font weight/spacing forensics
    "color_hex":      0.20,   # Color code deviation from brand standard
    "layout_match":   0.10,   # Structural layout alignment
}

# Sub-signal weights WITHIN REG layer
REG_SUB_WEIGHTS = {
    "db_match":       0.50,   # Product found in NAFDAC Greenbook
    "category_align": 0.35,   # NAFDAC category matches scanned product type
    "recall_flag":    0.15,   # Product on active recall/ban list
}

def validate_weights() -> None:
    """
    Verify all weight sets sum to exactly 1.0.
    Called at fusion startup and in CI. Raises ValueError on failure.
    """
    errors = []
    sets = [
        ("SIGNAL_WEIGHTS",          SIGNAL_WEIGHTS),
        ("SIGNAL_WEIGHTS_DAMAGED",  SIGNAL_WEIGHTS_DAMAGED),
        ("SIGNAL_WEIGHTS_FALLBACK", SIGNAL_WEIGHTS_FALLBACK),
        ("VISUAL_SUB_WEIGHTS",          VISUAL_SUB_WEIGHTS),
        ("OCR_SUB_WEIGHTS",          OCR_SUB_WEIGHTS),
        ("REG_SUB_WEIGHTS",          REG_SUB_WEIGHTS),
    ]
    for name, weights in sets:
        total = round(sum(weights.values()), 10)
        if total != 1.0:
            errors.append(f"{name} sums to {total}; expected 1.0")
        else:
            print(f"{name} OK")

    if errors:
        raise ValueError("Weight validation failed:\n" + "\n".join(errors))
    print("\nAll weight sets validated.")


if __name__ == "__main__":
    validate_weights()