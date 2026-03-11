"""
Configuration
=============================
Central configuration file for OCR & Linguistic Integrity pipeline.
All constants, dictionaries, and regex patterns live here.
To add a new product, append to AUTHENTIC_PRODUCTS.
"""

import re

# Expand this list as more brands are onboarded into SabiLens.

AUTHENTIC_PRODUCTS = {
    "axe musk 150ml": {
        "brand": "AXE",
        "manufacturer": "Unilever"
    },
    "closeup complete fresh protection 130g": {
        "brand": "Closeup",
        "manufacturer": "Unilever"
    },
    "dangote sugar 500g": {
        "brand": "Dangote",
        "manufacturer": "Dangote Group"
    },
    "dove gentle exfoliating": {
        "brand": "Dove",
        "manufacturer": "Unilever"
    },
    "dove coconut & jasmine flower scent 250ml": {
        "brand": "Dove",
        "manufacturer": "Unilever"
    },
    "dove pear & aloe vera scent 250ml": {
        "brand": "Dove",
        "manufacturer": "Unilever"
    },
    "familia 2 toilet rolls": {
        "brand": "Familia",
        "manufacturer": "PZ Cussons"
    },
    "golden penny pasta spaghettini 500g": {
        "brand": "Golden Penny",
        "manufacturer": "Flour Mills of Nigeria"
    },
    "golden terra soya oil 5l": {
        "brand": "Golden Terra",
        "manufacturer": "Golden Terra"
    },
    "indomie instant noodles": {
        "brand": "Indomie",
        "manufacturer": "Indofood"
    },
    "kellogg's coco pops 360g": {
        "brand": "Kellogg's",
        "manufacturer": "Kellogg's"
    },
    "kellogg's corn flakes 500g": {
        "brand": "Kellogg's",
        "manufacturer": "Kellogg's"
    },
    "kellogg's go grains 500g": {
        "brand": "Kellogg's",
        "manufacturer": "Kellogg's"
    },
    "lipton yellow label tea 25 tea bags": {
        "brand": "Lipton",
        "manufacturer": "Unilever"
    },
    "pepsodent triple protection": {
        "brand": "Pepsodent",
        "manufacturer": "Unilever"
    },
    "rexona xtra cool 50ml": {
        "brand": "Rexona",
        "manufacturer": "Unilever"
    },
    "sedoso vegetable oil 1l": {
        "brand": "Sedoso",
        "manufacturer": "Sedoso"
    },
    "terra chicken 50 cubes": {
        "brand": "Terra",
        "manufacturer": "Terra"
    },
    "vaseline intensive care 400ml": {
        "brand": "Vaseline",
        "manufacturer": "Unilever"
    },
    "vaseline blue seal 225ml": {
        "brand": "Vaseline",
        "manufacturer": "Unilever"
    }
}

# LOOKALIKE CHARACTER MAP. Counterfeiters commonly swap these characters to fool the eye.
# This maps fake character → real character.

LOOKALIKE_MAP = {
    "0": "o",    # zero → o
    "1": "l",    # one → l
    "3": "e",    # three → e
    "4": "a",    # four → a
    "5": "s",    # five → s
    "8": "b",    # eight → b
    "|": "l",    # pipe → l
    "rn": "m",   # rn → m (very common trick)
    "vv": "w",   # vv → w
}

# ==============================================================
# REGEX PATTERNS
# ==============================================================

# NAFDAC number format: e.g. A7-1234 or B1-56789
NAFDAC_PATTERN = re.compile(r"^[A-Z0-9]{1,3}-\d{3,6}$")

# Batch number: alphanumeric, 6–15 characters
BATCH_PATTERN = re.compile(r"^[A-Z0-9]{6,15}$")

# Expiry date: MM/YYYY or MM-YYYY or MON YYYY
EXPIRY_PATTERN = re.compile(
    r"(\d{2}[\/\-]\d{4}|\d{6}|[A-Z]{3}\.?\s?\d{4})",
    re.IGNORECASE
)
# NAFDAC number in full label text (with surrounding keywords)
NAFDAC_IN_TEXT_PATTERN = re.compile(
    r"(?:NAFDAC|REG(?:ISTRATION)?\.?\s*(?:NO\.?|NUMBER)?)\s*:?\s*([A-Z0-9]{1,2}-\d{3,6})",
    re.IGNORECASE
)

# Batch number in full label text
BATCH_IN_TEXT_PATTERN = re.compile(
    r"(?:BATCH|LOT|BATCH\s*NO\.?)\s*:?\s*([A-Z0-9]{6,15})",
    re.IGNORECASE
)

# Manufacturer name in full label text
MANUFACTURER_IN_TEXT_PATTERN = re.compile(
    r"(?:Manufactured\s+by|Marketed\s+by|Distributed\s+by)\s*:?\s*(.+?)(?:\.|,|\n|$)",
    re.IGNORECASE
)

# ==============================================================
# SCORING THRESHOLDS
# ==============================================================


# OCR confidence: below this (after damage adjustment) = low confidence flag
OCR_CONFIDENCE_THRESHOLD = 0.70

# Anomaly score weights (must sum to 1.0)
WEIGHTS = {
    "brand_anomaly": 0.40,       # 40% — brand name mismatch is the strongest signal
    "nafdac_format": 0.25,       # 25% — invalid NAFDAC format
    "missing_fields": 0.20,      # 20% — missing required label fields
    "low_ocr_confidence": 0.15,  # 15% — low OCR confidence after damage adjustment
}

# ==============================================================
# HYBRID RULE + ML BLENDING CONFIGURATION
# ==============================================================

HYBRID_SCORING = {
    "rule_weight": 0.75,
    "ml_weight": 0.25
}

BRAND_SIMILARITY_THRESHOLD = 75
PRODUCT_SIMILARITY_THRESHOLD = 60


# ==============================================================
# REQUIRED LABEL FIELDS
# Every authentic product label must contain all of these.
# ==============================================================
REQUIRED_FIELDS = [
    "product_name",
    "nafdac_number",
    "batch_number",
    "expiry_date",
    "manufacturer_name",
]