from .ml_model import TextAnomalyClassifier
from pathlib import Path
from .ml_model import TextAnomalyClassifier

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "text_model.pkl"



# Training data
X = [
    # Genuine products (label=0) 
    # Clean scan, all fields present, brand matches perfectly
    {
        "brand_similarity": 100.0, "brand_anomaly_flag": 0,
        "nafdac_valid": 1, "missing_fields_count": 0,
        "structural_score": 1.0, "ocr_confidence": 0.97,
        "damage_score": 0.0, "text_length": 280, "numeric_density": 0.15,
    },
    # Good scan, one minor field missing
    {
        "brand_similarity": 95.0, "brand_anomaly_flag": 0,
        "nafdac_valid": 1, "missing_fields_count": 1,
        "structural_score": 0.9, "ocr_confidence": 0.93,
        "damage_score": 0.0, "text_length": 240, "numeric_density": 0.12,
    },
    # Moderate blur but fields intact
    {
        "brand_similarity": 92.0, "brand_anomaly_flag": 0,
        "nafdac_valid": 1, "missing_fields_count": 1,
        "structural_score": 0.85, "ocr_confidence": 0.88,
        "damage_score": 0.4, "text_length": 210, "numeric_density": 0.10,
    },
    # Near-perfect scan
    {
        "brand_similarity": 98.0, "brand_anomaly_flag": 0,
        "nafdac_valid": 1, "missing_fields_count": 0,
        "structural_score": 1.0, "ocr_confidence": 0.96,
        "damage_score": 0.1, "text_length": 300, "numeric_density": 0.18,
    },
    # Front-only scan (NAFDAC usually on back) - still genuine
    {
        "brand_similarity": 90.0, "brand_anomaly_flag": 0,
        "nafdac_valid": 0, "missing_fields_count": 2,
        "structural_score": 0.7, "ocr_confidence": 0.91,
        "damage_score": 0.1, "text_length": 180, "numeric_density": 0.08,
    },

    # Suspicious / counterfeit products (label=1) 
    # Brand not detected, NAFDAC missing, many fields absent
    {
        "brand_similarity": 66.0, "brand_anomaly_flag": 1,
        "nafdac_valid": 0, "missing_fields_count": 5,
        "structural_score": 0.0, "ocr_confidence": 0.80,
        "damage_score": 0.0, "text_length": 90, "numeric_density": 0.05,
    },
    # Lookalike brand name, invalid NAFDAC format
    {
        "brand_similarity": 72.0, "brand_anomaly_flag": 1,
        "nafdac_valid": 0, "missing_fields_count": 4,
        "structural_score": 0.1, "ocr_confidence": 0.78,
        "damage_score": 0.0, "text_length": 110, "numeric_density": 0.07,
    },
    # Completely fabricated label - very low confidence, missing everything
    {
        "brand_similarity": 40.0, "brand_anomaly_flag": 1,
        "nafdac_valid": 0, "missing_fields_count": 6,
        "structural_score": 0.0, "ocr_confidence": 0.65,
        "damage_score": 0.0, "text_length": 60, "numeric_density": 0.03,
    },
    # Suspicious with moderate blur - harder to read but clearly wrong
    {
        "brand_similarity": 55.0, "brand_anomaly_flag": 1,
        "nafdac_valid": 0, "missing_fields_count": 4,
        "structural_score": 0.1, "ocr_confidence": 0.72,
        "damage_score": 0.4, "text_length": 80, "numeric_density": 0.04,
    },
    # NAFDAC format present but brand is wrong
    {
        "brand_similarity": 60.0, "brand_anomaly_flag": 1,
        "nafdac_valid": 1, "missing_fields_count": 3,
        "structural_score": 0.3, "ocr_confidence": 0.75,
        "damage_score": 0.0, "text_length": 150, "numeric_density": 0.10,
    },
    # Heavy blur, most text unreadable
    {
        "brand_similarity": 30.0, "brand_anomaly_flag": 1,
        "nafdac_valid": 0, "missing_fields_count": 5,
        "structural_score": 0.0, "ocr_confidence": 0.60,
        "damage_score": 0.8, "text_length": 40, "numeric_density": 0.02,
    },
]

y = [0, 0, 0, 0, 0,   # genuine
     1, 1, 1, 1, 1, 1] # suspicious

assert len(X) == len(y), f"X and y length mismatch: {len(X)} vs {len(y)}"

# ── Train and save ────────────────────────────────────────────────────────────
clf = TextAnomalyClassifier()
clf.train(X, y)
clf.save(MODEL_PATH)

print(f"Model trained on {len(X)} samples and saved to: {MODEL_PATH}")
print(f"Feature order: {clf.feature_order}")
