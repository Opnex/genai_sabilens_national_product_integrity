from app.ocr_linguistic.brand_validator import BrandValidator

validator = BrandValidator()

def test_brand_typo_detection():

    result = validator.validate("P3psodent toothpaste")

    assert result["closest_match"] == "Pepsodent"
    assert result["brand_anomaly_flag"] == 0