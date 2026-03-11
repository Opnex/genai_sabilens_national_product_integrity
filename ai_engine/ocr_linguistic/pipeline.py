import logging
import os
from .extractor import extract_text_blocks, build_metadata
from .rule_engine import compute_rule_score
from .feature_engineering import build_feature_vector
from .ml_model import TextAnomalyClassifier
from .config import HYBRID_SCORING
from .metadata_parser import extract_structured_metadata

from .brand_validator import BrandValidator
from .structural_validator import StructuralValidator
from .logger import setup_logger



logger = setup_logger("OCR_Linguistic")

MODEL_PATH = os.getenv("TEXT_MODEL_PATH", "models/text_model.pkl")


# -------------------------
# ML Model Loader
# -------------------------
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = TextAnomalyClassifier()
        _classifier.load(MODEL_PATH)
    return _classifier


# -------------------------
# Main Pipeline
# -------------------------
def run_pipeline(image_path: str, damage_score: float = 0.0) -> dict:

    logger.info(f"Pipeline started | image: {image_path} | damage_score: {damage_score}")

    if not os.path.exists(image_path):
        logger.error(f"Image not found: {image_path}")
        raise FileNotFoundError(image_path)
    
    # ---------------------------------
    # OCR Extraction
    # ---------------------------------
    blocks = extract_text_blocks(image_path)

    if not blocks:
        return _empty_result(damage_score)

    full_text = " ".join([block["text"] for block in blocks])
    logger.info(f"OCR blocks extracted: {len(blocks)}")
    # ---------------------------------
    # Base Metadata (raw OCR stats)
        # ---------------------------------
    metadata = build_metadata(blocks)
    logger.info(f"Base metadata extracted")
    # ---------------------------------
    # Brand Validation
    # ---------------------------------
    brand_validator = BrandValidator()
    brand_result = brand_validator.validate(full_text)

    metadata.update({
        "brand_similarity": brand_result["similarity_score"],
        "brand_anomaly_flag": brand_result["brand_anomaly_flag"],
        "closest_brand_match": brand_result["closest_match"],
        "brand_detected": brand_result["brand_detected"],
    })

    logger.info(f"Brand Validation: {brand_result}")

    # ---------------------------------
    # Regulatory Structured Metadata
    # ---------------------------------
    structured_metadata = extract_structured_metadata(
        full_text,
        brand_result["brand_detected"]
    )

    metadata.update(structured_metadata)

    logger.info(f"Structured Metadata: {structured_metadata}")
    

    # ---------------------------------
    # Structural Validation (Category-Specific)
    # ---------------------------------
    struct_validator = StructuralValidator(category="cosmetics")
    structural_validation = struct_validator.validate(metadata)

    metadata.update(structural_validation)

    logger.info(f"Structural Validation: {structural_validation}")

    # ---------------------------------
    # Rule Engine Scoring
    # ---------------------------------
    rule_score_output = compute_rule_score(
    metadata=metadata,
    damage_score=damage_score
)

    # ---------------------------------
    # Feature Engineering for ML
    # ---------------------------------
    features = build_feature_vector(
        metadata=metadata,
        brand_anomaly={
            "brand_anomaly_flag": brand_result["brand_anomaly_flag"],
            "brand_similarity": brand_result["similarity_score"]
        },
        structural_validation=structural_validation,
        damage_score=damage_score
    )
    logger.info(f"Feature vector built")
    # ---------------------------------
    # ML Model Prediction
    # ---------------------------------
    classifier = get_classifier()

    try:
        ml_score = classifier.predict_proba(features)
    except Exception:
        logger.exception("ML prediction failed")
        ml_score = 0.0
    
    
    # ---------------------------------
    # Hybrid Fusion Scoring
    # ---------------------------------
    final_score = round(
        (HYBRID_SCORING["rule_weight"] * rule_score_output["rule_score"]) +
        (HYBRID_SCORING["ml_weight"] * ml_score),
        4
    )

    logger.info(
        f"Rule Score: {rule_score_output['rule_score']} | "
        f"ML Score: {ml_score} | Final: {final_score}"
    )
    logger.info("Pipeline completed successfully")
    # ---------------------------------
    # Final Output
    # ---------------------------------
    return {
        "source": "OCR_Linguistic",
        "metadata": metadata,
        "brand_anomaly": brand_result,
        "structural_validation": structural_validation,
        "rule_score": rule_score_output,
        "ml_score": round(ml_score, 4),
        "final_text_anomaly_score": final_score,
    }


# -------------------------
# Empty OCR Handling
# -------------------------
def _empty_result(damage_score: float) -> dict:

    rule_score_output = {
    "rule_score": 1.0,
    "components": {"hard_fail": 1.0},
    "damage_score_applied": damage_score,
    "adjusted_ocr_confidence": 0.0,
}

    return {
        "source": "OCR_Linguistic",
        "metadata": {},
        "brand_anomaly": {},
        "structural_validation": {},
        "rule_score": rule_score_output,
        "ml_score": 1.0,
        "final_text_anomaly_score": 1.0,
    }