from app.ocr_linguistic.metadata_parser import extract_structured_metadata

def test_nafdac_extraction():

    text = "NAFDAC Reg No:02-0385 EXP:091028BN:254141"

    metadata = extract_structured_metadata(text, "vaseline")

    assert metadata["nafdac_number"] == "NAFDAC-02-0385"