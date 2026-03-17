import re
from rapidfuzz import fuzz
from .config import AUTHENTIC_PRODUCTS, LOOKALIKE_MAP, BRAND_SIMILARITY_THRESHOLD


class BrandValidator:
    def __init__(self):
        self.known_brands = list(
            set(product["brand"] for product in AUTHENTIC_PRODUCTS.values())
        )

    def normalize_text(self, text: str):
        """
        Replace lookalike characters with real equivalents.
        Example: Panad0l → Panadol
        """
        normalized = text
        corrections = []

        for fake, real in LOOKALIKE_MAP.items():
            if fake in normalized:
                normalized = normalized.replace(fake, real)
                corrections.append(f"{fake} → {real}")

        return normalized, corrections

    def extract_brand_candidate(self, raw_text: str):
        """
        Try to detect possible brand tokens from raw OCR text.
        """
        tokens = re.findall(r"[A-Za-z0-9']{3,}", raw_text)
        return tokens

    def validate(self, raw_text: str):
        raw_text_lower = raw_text.lower()

        best_match = None
        best_score = 0

        for brand in self.known_brands:
            score = fuzz.partial_ratio(
                brand.lower(),
                raw_text_lower
        )

            if score > best_score:
                best_score = score
                best_match = brand

        # Minimum detection threshold (important!)
        MIN_DETECTION_THRESHOLD = 70

        if best_score < MIN_DETECTION_THRESHOLD:
         return {
            "brand_detected": None,
            "closest_match": None,
            "similarity_score": best_score,
            "lookalike_corrections": [],
            "brand_anomaly_flag": 1
        }

        anomaly_flag = 1 if best_score < BRAND_SIMILARITY_THRESHOLD else 0

        return {
        "brand_detected": best_match,
        "closest_match": best_match,
        "similarity_score": best_score,
        "lookalike_corrections": [],
        "brand_anomaly_flag": anomaly_flag
    }