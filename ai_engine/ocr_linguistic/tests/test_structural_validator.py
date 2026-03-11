from app.ocr_linguistic.structural_validator import StructuralValidator

def test_structural_validation():

    validator = StructuralValidator(category="cosmetics")

    metadata = {
        "nafdac_number": "NAFDAC-02-0385",
        "expiry_date": "2028-10-09",
        "batch_number": "254141",
        "net_weight_or_volume": "225 ml"
    }

    result = validator.validate(metadata)

    assert result["expiry_format_valid"] is True