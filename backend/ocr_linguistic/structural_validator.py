import re
from .category_rules import CATEGORY_RULES


class StructuralValidator:

    def __init__(self, category: str):
        if category not in CATEGORY_RULES:
            raise ValueError(f"Unsupported category: {category}")

        self.rules = CATEGORY_RULES[category]

    def validate(self, metadata: dict):

        missing_fields = []

        # Required field enforcement
        for field in self.rules["required_fields"]:
            if not metadata.get(field):
                missing_fields.append(field)

        # Expiry format validation
        expiry_valid = True
        expiry_value = metadata.get("expiry_date")

        if expiry_value:
            if not re.search(self.rules["expiry_regex"], expiry_value):
                expiry_valid = False
        else:
            expiry_valid = False

        # Batch format validation
        batch_value = metadata.get("batch_number")
        batch_valid = bool(batch_value)

        if batch_value:
            if not re.search(self.rules["batch_regex"], batch_value):
                batch_valid = False
        else:
            batch_valid = False

        structural_score = 1 - (
            (len(missing_fields) * 0.15)
            + (0.2 if not expiry_valid else 0)
            + (0.2 if not batch_valid else 0)
        )

        structural_score = max(0, min(structural_score, 1))

        return {
            "missing_fields": missing_fields,
            "missing_fields_count": len(missing_fields),
            "expiry_format_valid": expiry_valid,
            "batch_format_valid": batch_valid,
            "structural_score": round(structural_score, 4)
        }