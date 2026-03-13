
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from signals.visual_adapter import adapt as visual_adapt
from signals.ocr_adapter    import adapt as ocr_adapt
from ai_engine.fusion_engine.signals.reg_adapter    import adapt as reg_adapt
from core.fusion_engine        import run_fusion

def make_signals(visual_conf, visual_sim, ocr_anomaly, ocr_nafdac, reg_score, reg_status, reg_severity, reg_verified, reg_subcat_match=True):
    visual = visual_adapt({
        "product": "vaseline blue seal 225ml",
        "Visual Similarity": visual_sim,
        "damage_score": 0.1,
        "confidence": visual_conf,
        "verdict": "Authentic" if visual_conf >= 0.75 else "Suspicious" if visual_conf >= 0.45 else "Fake"
    })
    ocr = ocr_adapt({
        "source": "OCR_Linguistic",
        "metadata": {"nafdac_number": ocr_nafdac, "avg_ocr_confidence": 0.91,
                     "brand_detected": "Vaseline", "brand_similarity": 95.0, "brand_anomaly_flag": 0},
        "brand_anomaly": {"brand_detected": "Vaseline", "closest_match": "Vaseline",
                          "similarity_score": 95.0, "lookalike_corrections": [], "brand_anomaly_flag": 0},
        "structural_validation": {"missing_fields": [], "structural_score": 1.0,
                                  "expiry_format_valid": True, "batch_format_valid": True},
        "rule_score": {"rule_score": ocr_anomaly, "components": {}, "damage_score_applied": 0.1, "adjusted_ocr_confidence": 0.91},
        "ml_score": ocr_anomaly,
        "final_text_anomaly_score": ocr_anomaly,
    })
    reg = reg_adapt({
        "verified": reg_verified,
        "verification_score": reg_score,
        "status_code": reg_status,
        "severity": reg_severity,
        "summary": f"Test scenario: {reg_status}",
        "detail": f"Detail for {reg_status}",
        "expiry_check": {"is_valid": True, "is_near_expiry": False, "days_remaining": 900, "severity": "NONE", "message": ""},
        "alignment": {"is_match": reg_subcat_match, "scanned_norm": "Cosmetics", "registered_norm": "Cosmetics" if reg_subcat_match else "Cereals"},
        "matched_record": {"product_name": "Vaseline Blue Seal", "subcategory": "Cosmetics", "expiry_date_iso": "2028-12-20", "applicant_name": "Unilever"},
        "all_records": [],
    })
    return visual, ocr, reg

SCENARIOS = [
    ("AUTHENTIC product",
     dict(visual_conf=0.79, visual_sim=0.88, ocr_anomaly=0.06, ocr_nafdac="02-0385",
          reg_score=1.0, reg_status="VERIFIED", reg_severity="NONE", reg_verified=True)),

    ("SUSPICIOUS — no NAFDAC extracted by OCR",
     dict(visual_conf=0.79, visual_sim=0.88, ocr_anomaly=0.06, ocr_nafdac=None,
          reg_score=1.0, reg_status="VERIFIED", reg_severity="NONE", reg_verified=True)),

    ("FAKE - NAFDAC not in database (NOT_FOUND)",
     dict(visual_conf=0.79, visual_sim=0.88, ocr_anomaly=0.06, ocr_nafdac="FAKE-999",
          reg_score=0.0, reg_status="NOT_FOUND", reg_severity="CRITICAL", reg_verified=False)),

    ("FAKE - SUBCATEGORY MISMATCH (classic counterfeit)",
     dict(visual_conf=0.79, visual_sim=0.88, ocr_anomaly=0.06, ocr_nafdac="A8-4114",
          reg_score=0.2, reg_status="SUBCATEGORY_MISMATCH", reg_severity="CRITICAL",
          reg_verified=False, reg_subcat_match=False)),
]

print("=" * 65)
print("FUSION ENGINE — ALL SCENARIOS")
print("=" * 65)

for label, kwargs in SCENARIOS:
    visual, ocr, reg = make_signals(**kwargs)
    result = run_fusion(visual, ocr, reg)

    print(f"\n{label}")
    print(f"  Score:     {result['final_score']}")
    print(f"  Verdict:   {result['verdict']}")
    print(f"  Severity:  {result['severity']}")
    print(f"  Confidence:{result['confidence_label']}")
    print(f"  Override:  {result['override_applied']} -> {result['applied_override']['type'] if result['applied_override'] else 'None'}")
    bd = result['breakdown']
    print(f"  Breakdown: VISUAL={bd['visual']['weighted']} + OCR={bd['ocr']['weighted']} + REG={bd['reg']['weighted']}")

print("\n" + "=" * 65)
