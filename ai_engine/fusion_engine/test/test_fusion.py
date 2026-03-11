# Mock visual/ocr/reg signals -> validate decisions

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from signals.visual_adapter import adapt as visual_adapt, validate as visual_validate
from signals.ocr_adapter    import adapt as ocr_adapt, validate as ocr_validate
from ai_engine.fusion_engine.signals.reg_adapter    import adapt as reg_adapt, validate as reg_validate

# Mock visual output (authentic product, slight damage) 
mock_visual = {
    "product":          "vaseline blue seal 225ml",
    "Visual Similarity": 0.88,
    "damage_score":     0.10,
    "confidence":       0.792,   # 0.88 * (1 - 0.10)
    "verdict":          "Authentic"
}

# Mock ocr output (clean label, brand found) 
mock_ocr = {
    "source": "OCR_Linguistic",
    "metadata": {
        "product_name": "Vaseline Blue Seal",
        "nafdac_number": "02-0385",
        "batch_number": "BN123456",
        "expiry_date": "2028-12-20",
        "avg_ocr_confidence": 0.91,
        "brand_detected": "Vaseline",
        "brand_similarity": 95.0,
        "brand_anomaly_flag": 0,
    },
    "brand_anomaly": {
        "brand_detected": "Vaseline",
        "closest_match": "Vaseline",
        "similarity_score": 95.0,
        "lookalike_corrections": [],
        "brand_anomaly_flag": 0,
    },
    "structural_validation": {
        "missing_fields": [],
        "missing_fields_count": 0,
        "expiry_format_valid": True,
        "batch_format_valid": True,
        "structural_score": 1.0,
    },
    "rule_score": {
        "rule_score": 0.07,
        "components": {"confidence_component": 0.07},
        "damage_score_applied": 0.10,
        "adjusted_ocr_confidence": 0.91,
    },
    "ml_score": 0.05,
    "final_text_anomaly_score": 0.06,
}

# Mock reg output (verified, category aligned) 
mock_reg = {
    "verified": True,
    "verification_score": 1.0,
    "status_code": "VERIFIED",
    "severity": "NONE",
    "summary": "'Vaseline blueseal pure petroleum jelly' is a valid, registered NAFDAC product.",
    "detvisuall": "Verification passed. Product is registered under Cosmetics.",
    "expiry_check": {"is_valid": True, "is_near_expiry": False, "days_remvisualning": 1015, "severity": "NONE", "message": "Valid."},
    "alignment": {"is_match": True, "scanned_norm": "Cosmetics", "registered_norm": "Cosmetics"},
    "matched_record": {
        "product_name": "Vaseline blueseal pure petroleum jelly original",
        "subcategory": "Cosmetics",
        "expiry_date_iso": "2028-12-20",
        "applicant_name": "UNILEVER NIGERIA PLC",
    },
    "all_records": [],
}

print("=" * 60)
print("ADAPTER VALIDATION & ADAPTATION TEST")
print("=" * 60)

# visual
errors = visual_validate(mock_visual)
print(f"\nvisual validate: {'PASS' if not errors else errors}")
sig1 = visual_adapt(mock_visual)
print(f"   fusion_score:   {sig1['fusion_score']}  (expected ~79.2)")
print(f"   damage_score:   {sig1['damage_score']}")
print(f"   override_flag:  {sig1['override_flag']}")

# ocr
errors = ocr_validate(mock_ocr)
print(f"\nocr validate: {'PASS' if not errors else errors}")
sig2 = ocr_adapt(mock_ocr)
print(f"   fusion_score:   {sig2['fusion_score']}  (expected ~94.0, anomaly=0.06 flipped)")
print(f"   nafdac_number:  {sig2['nafdac_number']}")
print(f"   override_flag:  {sig2['override_flag']}")
print(f"   lookalike_corrections: {sig2['lookalike_corrections']}")

# regulatory
errors = reg_validate(mock_reg)
print(f"\nreg validate: {'PASS' if not errors else errors}")
sig3 = reg_adapt(mock_reg)
print(f"   fusion_score:   {sig3['fusion_score']}  (expected 100.0)")
print(f"   status_code:    {sig3['status_code']}")
print(f"   override_flag:  {sig3['override_flag']}")
print(f"   registered_cat: {sig3['nafdac_registered_category']}")

print("\n" + "=" * 60)
print("WEIGHTED FUSION PREVIEW")
print("=" * 60)
weighted = round(
    sig1['fusion_score'] * 0.30 +
    sig2['fusion_score'] * 0.35 +
    sig3['fusion_score'] * 0.35,
    2
)
print(f"  visual x 0.30 = {sig1['fusion_score'] * 0.30:.2f}")
print(f"  ocr x 0.35 = {sig2['fusion_score'] * 0.35:.2f}")
print(f"  reg x 0.35 = {sig3['fusion_score'] * 0.35:.2f}")
print(f"  ─────────────────────")
print(f"  FINAL SCORE = {weighted}  -> {'AUTHENTIC' if weighted >= 80 else 'SUSPICIOUS' if weighted >= 50 else 'FAKE'}")
