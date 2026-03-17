"""
retrieval/subcategory_alignment.py
------------------------------------
Detects mismatches between what a scanned product APPEARS to be and what its
NAFDAC registration number is actually registered for.

THE CORE COUNTERFEIT SCENARIO
  A counterfeit product reuses a valid NAFDAC number from a different product
  type.  For example:
    • A fake "medicine" that prints a NAFDAC number belonging to Indomie noodles.
    • A fake "cooking oil" printed with Vaseline's cosmetics NAFDAC number.

  This module catches those mismatches by comparing:
    scanned_subcategory   — what the product appears to be (from A1/A2 pipeline)
    registered_subcategory— what the NAFDAC number is actually registered for

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL DATA SUBCATEGORIES  (nafdac_database.xlsx, 15 rows)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  'Cereals and Cereal Products'                         — 4 rows
  'Cosmetics'                                           — 5 rows
  'Fats and oils, and Fat Emulsions'                    — 2 rows
  'Salts, Spices, Soups, Sauces, Salads and Seasoning' — 2 rows
  'Beverages'                                           — 1 row
  'Sweeteners'                                          — 1 row

ALIAS MAP DESIGN
  Each canonical subcategory key maps to all the ways a product in that category
  might be described by:
    • The A1 visual classification pipeline
    • The A2 OCR text classifier
    • A human typing into the mobile app
    • Label text fragments

  The reverse lookup dict (_ALIAS_TO_CANONICAL) enables O(1) normalisation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional


# ── Subcategory alias map ──────────────────────────────────────────────────────
# Keys must be EXACT canonical strings as stored in the database.
# Aliases are lowercase for case-insensitive matching.

SUBCATEGORY_ALIASES: dict[str, list[str]] = {

    "Cereals and Cereal Products": [
        "cereal", "cereals", "cereal product", "cereal products",
        "corn flakes", "cornflakes", "coco pops", "oats",
        "noodles", "instant noodles", "pasta", "spaghetti", "spaghettini",
        "macaroni", "semolina", "flour", "wheat",
        "indomie", "golden penny",
        "breakfast cereal",
    ],

    "Cosmetics": [
        "cosmetic", "cosmetics", "personal care",
        "toothpaste", "tooth paste", "dental",
        "deodorant", "roll-on", "antiperspirant", "body spray",
        "lotion", "body lotion", "skin lotion",
        "petroleum jelly", "vaseline", "jelly",
        "closeup", "pepsodent", "rexona",
        "skin care", "skincare", "cream", "moisturiser", "moisturizer",
        "hair care", "shampoo", "conditioner",
        "soap", "body wash",
        "lip balm", "lip care",
    ],

    "Fats and oils, and Fat Emulsions": [
        "fat", "fats", "oil", "oils", "vegetable oil", "cooking oil",
        "soya oil", "palm oil", "palm olein", "sunflower oil", "groundnut oil",
        "fat emulsion", "fat emulsions", "margarine", "shortening",
        "golden terra", "sedoso",
    ],

    "Salts, Spices, Soups, Sauces, Salads and Seasoning": [
        "salt", "spice", "spices", "seasoning", "seasonings",
        "soup", "soups", "sauce", "sauces", "salad", "salads",
        "seasoning cube", "bouillon", "stock cube", "maggi", "knorr",
        "pepper", "tomato paste", "cooking paste", "herbs",
        "curry", "thyme", "ginger", "garlic",
        "peppe terra", "terra",
    ],

    "Beverages": [
        "beverage", "beverages", "drink", "drinks",
        "tea", "coffee", "juice", "soft drink", "carbonated drink",
        "water", "mineral water", "energy drink", "malt",
        "lipton", "yellow label tea",
    ],

    "Sweeteners": [
        "sweetener", "sweeteners", "sugar", "refined sugar",
        "white sugar", "brown sugar", "granulated sugar",
        "honey", "syrup",
        "dangote sugar", "dangote",
    ],

    "Unknown": [
        "unknown", "unclassified", "other", "not specified",
    ],
}

# Build reverse lookup: alias (lowercase) → canonical subcategory
# This gives O(1) lookup in normalize_subcategory().
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for _canonical, _aliases in SUBCATEGORY_ALIASES.items():
    _ALIAS_TO_CANONICAL[_canonical.lower()] = _canonical   # canonical maps to itself
    for _alias in _aliases:
        _ALIAS_TO_CANONICAL[_alias.lower()] = _canonical


def normalize_subcategory(raw: str) -> str:
    """
    Map a raw subcategory string to its canonical NAFDAC subcategory name.

    Performs a case-insensitive lookup against the alias table.
    If no alias matches, returns the input stripped and lowercased.
    This ensures that two truly-unknown categories will still match each
    other, while known aliases always resolve to a stable canonical name.

    Args:
        raw: Raw subcategory string from the database record, OCR output,
             or A1/A2 classifier.

    Returns:
        Canonical subcategory name (e.g. 'Cosmetics') if a match is found,
        otherwise the lowercased raw value.

    Examples:
        >>> normalize_subcategory("Cosmetics")
        'Cosmetics'
        >>> normalize_subcategory("toothpaste")
        'Cosmetics'
        >>> normalize_subcategory("NOODLES")
        'Cereals and Cereal Products'
        >>> normalize_subcategory("dangote sugar")
        'Sweeteners'
        >>> normalize_subcategory("processed meat")  # Not in any alias list
        'processed meat'
    """
    if not raw:
        return "Unknown"

    cleaned = raw.strip().lower()
    return _ALIAS_TO_CANONICAL.get(cleaned, cleaned)


def check_subcategory_alignment(
    scanned_subcategory:    str,
    registered_subcategory: str,
) -> dict:
    """
    Compare what a scanned product appears to be against what its NAFDAC
    registration is for, and return a structured alignment verdict.

    This is the core mismatch detection function.  Called by
    regulatory_scorer.compute_verification_score() after a successful
    NAFDAC number lookup.

    CRITICAL MISMATCH SCENARIO (demo):
        scanned_subcategory    = "cereal"      (looks like Indomie on the box)
        registered_subcategory = "Cosmetics"   (NAFDAC number belongs to Rexona)
        → MISMATCH — counterfeit product reusing Rexona's registration number

    Args:
        scanned_subcategory:    Category identified by the A1/A2 scan pipeline.
                                Raw text is fine — normalize_subcategory() is
                                applied internally.
        registered_subcategory: The subcategory value from the database record
                                returned by retrieve_by_nafdac_no().

    Returns:
        Dict with keys:
          is_match           (bool)       : True if categories align
          scanned_norm       (str)        : Normalised scanned category
          registered_norm    (str)        : Normalised registered category
          mismatch_type      (str | None) : 'SUBCATEGORY_MISMATCH' or None
          severity           (str)        : 'NONE' or 'CRITICAL'
          message            (str)        : Human-readable explanation for
                                           N-ATLAS Yoruba/Hausa/Pidgin translation

    Examples:
        >>> check_subcategory_alignment("toothpaste", "Cosmetics")
        {"is_match": True, "severity": "NONE", ...}

        >>> check_subcategory_alignment("noodles", "Cosmetics")
        {"is_match": False, "severity": "CRITICAL",
         "mismatch_type": "SUBCATEGORY_MISMATCH", ...}
    """
    scanned_norm    = normalize_subcategory(scanned_subcategory)
    registered_norm = normalize_subcategory(registered_subcategory)

    is_match = (scanned_norm == registered_norm)

    if is_match:
        message = (
            f"Product category confirmed: '{registered_norm}'. "
            f"Scanned product matches its registered classification."
        )
    else:
        message = (
            f"CRITICAL MISMATCH — NAFDAC number is registered under "
            f"'{registered_norm}' but the scanned product appears to be "
            f"'{scanned_norm}'. This is a strong indicator that this "
            f"product is counterfeit or has been mislabelled. "
            f"Do not purchase this product."
        )

    return {
        "is_match"       : is_match,
        "scanned_norm"   : scanned_norm,
        "registered_norm": registered_norm,
        "mismatch_type"  : None if is_match else "SUBCATEGORY_MISMATCH",
        "severity"       : "NONE" if is_match else "CRITICAL",
        "message"        : message,
    }


def get_aliases(subcategory: str) -> Optional[list[str]]:
    """
    Return all known aliases for a canonical subcategory name.

    Utility used by tests and the A4 Fusion Engine when it needs all possible
    textual descriptions for a given product category.

    Args:
        subcategory: Canonical subcategory name.

    Returns:
        List of alias strings, or None if the subcategory is not recognised.

    Example:
        >>> get_aliases("Cosmetics")[:4]
        ['cosmetic', 'cosmetics', 'personal care', 'toothpaste']
    """
    return SUBCATEGORY_ALIASES.get(subcategory)