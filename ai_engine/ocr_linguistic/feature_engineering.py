def build_feature_vector(
    metadata: dict,
    brand_anomaly: dict,
    structural_validation: dict,
    damage_score: float
) -> dict:

    raw_text = metadata.get("raw_ocr_text", "")
    tokens = raw_text.split()

    numeric_tokens = [t for t in tokens if any(c.isdigit() for c in t)]

    return {
        "brand_similarity": brand_anomaly.get("similarity_score", 0),
        "brand_anomaly_flag": int(brand_anomaly.get("is_anomaly", False)),
        "nafdac_valid": int(structural_validation.get("nafdac_format_valid", False)),
        "missing_fields_count": len(structural_validation.get("missing_fields", [])),
        "ocr_confidence": metadata.get("avg_ocr_confidence", 0.0),
        "damage_score": damage_score,
        "text_length": len(raw_text),
        "numeric_density": len(numeric_tokens) / max(len(tokens), 1),
    }