import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import run_scan

# Reuse payloads from test_adapters or define inline
VISUAL = {"product": "Milo 400g", "Visual Similarity": 0.91,
      "damage_score": 0.1, "blur_value": 85.0,
      "confidence": 0.819, "verdict": "Authentic"}

OCR = {"source": "OCR_Linguistic", "final_text_anomaly_score": 0.12,
      "ml_score": 0.10,
      "metadata": {"nafdac_number": "A8-4114", "avg_ocr_confidence": 0.91,
                   "brand_detected": "Milo"},
      "brand_anomaly": {"brand_detected": "Milo", "similarity_score": 98.0,
                        "brand_anomaly_flag": 0, "lookalike_corrections": []},
      "structural_validation": {"missing_fields": [], "structural_score": 0.95,
                                "expiry_format_valid": True, "batch_format_valid": True},
      "rule_score": {"rule_score": 0.10, "damage_score_applied": 0.1,
                     "adjusted_ocr_confidence": 0.91}}

REG_VERIFIED = {"verified": True, "verification_score": 1.0,
               "status_code": "VERIFIED", "severity": "NONE",
               "summary": "Verified.", "detail": "All checks passed.",
               "expiry_check": {"is_near_expiry": False, "days_remaining": 180},
               "alignment": {"scanned_norm": "food_supplement"},
               "matched_record": {"product_name": "Milo 400g",
                                  "subcategory": "food_supplement",
                                  "expiry_date_iso": "2026-12-01"},
               "all_records": [], "fallback_used": False,
               "tools_called": ["lookup_nafdac"], "reasoning_trace": []}

REG_NOT_FOUND = {**REG_VERIFIED, "verified": False, "verification_score": 0.0,
                "status_code": "NOT_FOUND", "severity": "CRITICAL",
                "matched_record": None}

GPS = {"lat": 6.5244, "lng": 3.3792, "accuracy": 8.5}


def test_authentic_scan():
    result = run_scan(VISUAL, OCR, REG_VERIFIED, GPS, "open_market",
                      package_evidence=False)
    assert result["verdict"] == "AUTHENTIC", result["verdict"]
    assert result["action"] == "BUY"
    assert result["status"] in ("SUCCESS", "PARTIAL")
    assert result["weight_mode"] == "BASE"
    print(f"authentic | score={result['final_score']} | mode={result['weight_mode']}")

def test_fake_not_found_override():
    result = run_scan(VISUAL, OCR, REG_NOT_FOUND, GPS, "open_market",
                      package_evidence=False)
    assert result["verdict"] == "FAKE", result["verdict"]
    assert result["override_applied"] is True
    assert result["action"] == "DO NOT BUY"
    print(f"fake (NOT_FOUND override) | score={result['final_score']}")

def test_damaged_weights():
    a1_blurry = {**VISUAL, "damage_score": 0.8, "blur_value": 12.0,
                 "confidence": 0.4}
    result = run_scan(a1_blurry, OCR, REG_VERIFIED, GPS, "open_market",
                      package_evidence=False)
    assert result["weight_mode"] == "DAMAGED"
    assert result["verdict"] in ("AUTHENTIC", "SUSPICIOUS", "FAKE")
    print(f"damaged weights | score={result['final_score']} | mode={result['weight_mode']}")

def test_rescan_required():
    a1_extreme = {**VISUAL, "damage_score": 0.8, "blur_value": 2.1}
    result = run_scan(a1_extreme, OCR, REG_VERIFIED, GPS, "open_market",
                      package_evidence=False)
    assert result["status"] == "RESCAN_REQUIRED"
    assert result["verdict"] == "RESCAN_REQUIRED"
    assert result["final_score"] is None
    print("rescan_required | no verdict issued, no NAFDAC report")

def test_fallback_weights():
    REG_fallback = {**REG_VERIFIED, "fallback_used": True,
                   "alignment": {"scanned_norm": "food_supplement",
                                 "similarity_score": 0.78}}
    result = run_scan(VISUAL, OCR, REG_fallback, GPS, "open_market",
                      package_evidence=False)
    assert result["weight_mode"] == "FALLBACK"
    print(f"fallback weights | score={result['final_score']} | mode={result['weight_mode']}")

def test_failsafe_on_bad_input():
    result = run_scan(None, None, None, GPS, "open_market",
                      package_evidence=False)
    assert result["verdict"] == "FAKE"
    assert result["status"] in ("PARTIAL", "FAILSAFE")
    print(f"failsafe | bad inputs never return AUTHENTIC")


if __name__ == "__main__":
    test_authentic_scan()
    test_fake_not_found_override()
    test_damaged_weights()
    test_rescan_required()
    test_fallback_weights()
    test_failsafe_on_bad_input()
    print("\nAll pipeline tests passed.")    