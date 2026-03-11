"""
tests/test_subcategory_alignment.py
-------------------------------------
Unit tests for the subcategory alignment / mismatch detection engine.

All test cases reference the 6 real subcategories in nafdac_database.xlsx
and the specific products that belong to each.  The counterfeit scenarios
are designed around the actual demo dataset.

Run:
    pytest tests/test_subcategory_alignment.py -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from retrieval.subcategory_alignment import (
    normalize_subcategory,
    check_subcategory_alignment,
)


class TestNormalizeSubcategory:

    # ── Exact canonical names ─────────────────────────────────────────────────

    def test_cereals_exact(self):
        assert normalize_subcategory("Cereals and Cereal Products") == "Cereals and Cereal Products"

    def test_cosmetics_exact(self):
        assert normalize_subcategory("Cosmetics") == "Cosmetics"

    def test_fats_exact(self):
        assert normalize_subcategory("Fats and oils, and Fat Emulsions") == "Fats and oils, and Fat Emulsions"

    def test_spices_exact(self):
        assert normalize_subcategory("Salts, Spices, Soups, Sauces, Salads and Seasoning") == "Salts, Spices, Soups, Sauces, Salads and Seasoning"

    def test_beverages_exact(self):
        assert normalize_subcategory("Beverages") == "Beverages"

    def test_sweeteners_exact(self):
        assert normalize_subcategory("Sweeteners") == "Sweeteners"

    # ── Alias-based resolution (product-type text from OCR/classifier) ─────────

    def test_noodles_to_cereals(self):
        """'noodles' (Indomie) → Cereals and Cereal Products"""
        assert normalize_subcategory("noodles") == "Cereals and Cereal Products"

    def test_pasta_to_cereals(self):
        """'pasta' (Golden Penny) → Cereals and Cereal Products"""
        assert normalize_subcategory("pasta") == "Cereals and Cereal Products"

    def test_corn_flakes_to_cereals(self):
        assert normalize_subcategory("corn flakes") == "Cereals and Cereal Products"

    def test_toothpaste_to_cosmetics(self):
        assert normalize_subcategory("toothpaste") == "Cosmetics"

    def test_deodorant_to_cosmetics(self):
        assert normalize_subcategory("deodorant") == "Cosmetics"

    def test_vaseline_to_cosmetics(self):
        assert normalize_subcategory("vaseline") == "Cosmetics"

    def test_lotion_to_cosmetics(self):
        assert normalize_subcategory("lotion") == "Cosmetics"

    def test_petroleum_jelly_to_cosmetics(self):
        assert normalize_subcategory("petroleum jelly") == "Cosmetics"

    def test_vegetable_oil_to_fats(self):
        assert normalize_subcategory("vegetable oil") == "Fats and oils, and Fat Emulsions"

    def test_cooking_oil_to_fats(self):
        assert normalize_subcategory("cooking oil") == "Fats and oils, and Fat Emulsions"

    def test_palm_oil_to_fats(self):
        assert normalize_subcategory("palm oil") == "Fats and oils, and Fat Emulsions"

    def test_seasoning_cube_to_spices(self):
        assert normalize_subcategory("seasoning cube") == "Salts, Spices, Soups, Sauces, Salads and Seasoning"

    def test_seasoning_to_spices(self):
        assert normalize_subcategory("seasoning") == "Salts, Spices, Soups, Sauces, Salads and Seasoning"

    def test_spice_to_spices(self):
        assert normalize_subcategory("spice") == "Salts, Spices, Soups, Sauces, Salads and Seasoning"

    def test_tea_to_beverages(self):
        assert normalize_subcategory("tea") == "Beverages"

    def test_lipton_to_beverages(self):
        assert normalize_subcategory("lipton") == "Beverages"

    def test_sugar_to_sweeteners(self):
        assert normalize_subcategory("sugar") == "Sweeteners"

    def test_dangote_to_sweeteners(self):
        assert normalize_subcategory("dangote") == "Sweeteners"

    # ── Case insensitivity ─────────────────────────────────────────────────────

    def test_uppercase_noodles(self):
        assert normalize_subcategory("NOODLES") == "Cereals and Cereal Products"

    def test_mixed_case_toothpaste(self):
        assert normalize_subcategory("Toothpaste") == "Cosmetics"

    # ── Unknown categories ────────────────────────────────────────────────────

    def test_unrecognised_returns_lowercase(self):
        result = normalize_subcategory("processed meat")
        assert result == "processed meat"

    def test_empty_returns_unknown(self):
        assert normalize_subcategory("") == "Unknown"


class TestCheckSubcategoryAlignment:

    # ── Matching scenarios ─────────────────────────────────────────────────────

    def test_corn_flakes_match(self):
        """Kellogg's Corn Flakes scanned as 'corn flakes' vs registered 'Cereals…' → MATCH"""
        r = check_subcategory_alignment("corn flakes", "Cereals and Cereal Products")
        assert r["is_match"] is True
        assert r["severity"] == "NONE"

    def test_indomie_noodles_match(self):
        """Indomie scanned as 'noodles' vs registered 'Cereals…' → MATCH"""
        r = check_subcategory_alignment("noodles", "Cereals and Cereal Products")
        assert r["is_match"] is True

    def test_toothpaste_match(self):
        """Closeup scanned as 'toothpaste' vs registered 'Cosmetics' → MATCH"""
        r = check_subcategory_alignment("toothpaste", "Cosmetics")
        assert r["is_match"] is True
        assert r["severity"] == "NONE"

    def test_vaseline_match(self):
        """Vaseline jelly scanned as 'petroleum jelly' vs registered 'Cosmetics' → MATCH"""
        r = check_subcategory_alignment("petroleum jelly", "Cosmetics")
        assert r["is_match"] is True

    def test_vegetable_oil_match(self):
        r = check_subcategory_alignment("cooking oil", "Fats and oils, and Fat Emulsions")
        assert r["is_match"] is True

    def test_tea_match(self):
        r = check_subcategory_alignment("tea", "Beverages")
        assert r["is_match"] is True

    def test_sugar_match(self):
        r = check_subcategory_alignment("sugar", "Sweeteners")
        assert r["is_match"] is True

    def test_exact_canonical_match(self):
        r = check_subcategory_alignment("Cosmetics", "Cosmetics")
        assert r["is_match"] is True

    # ── MISMATCH scenarios (counterfeit detection) ─────────────────────────────

    def test_cereal_nafdac_on_cosmetic_product(self):
        """
        DEMO SCENARIO 1: Kellogg's NAFDAC number stamped on a fake deodorant.
        scanned='cosmetics', registered='Cereals and Cereal Products' → CRITICAL
        """
        r = check_subcategory_alignment("cosmetics", "Cereals and Cereal Products")
        assert r["is_match"] is False
        assert r["severity"] == "CRITICAL"
        assert r["mismatch_type"] == "SUBCATEGORY_MISMATCH"

    def test_cosmetic_nafdac_on_food_product(self):
        """
        DEMO SCENARIO 2: Vaseline NAFDAC number on a fake cooking oil.
        scanned='cooking oil', registered='Cosmetics' → CRITICAL
        """
        r = check_subcategory_alignment("cooking oil", "Cosmetics")
        assert r["is_match"] is False
        assert r["severity"] == "CRITICAL"

    def test_food_nafdac_on_seasoning(self):
        """
        DEMO SCENARIO 3: Indomie's NAFDAC on a fake seasoning cube.
        scanned='seasoning cube', registered='Cereals and Cereal Products' → CRITICAL
        """
        r = check_subcategory_alignment("seasoning cube", "Cereals and Cereal Products")
        assert r["is_match"] is False
        assert r["severity"] == "CRITICAL"

    def test_mismatch_contains_both_categories_in_message(self):
        r = check_subcategory_alignment("noodles", "Cosmetics")
        assert "Cereals and Cereal Products" in r["message"]
        assert "Cosmetics" in r["message"]

    # ── Result field integrity ─────────────────────────────────────────────────

    def test_normalised_values_in_result(self):
        r = check_subcategory_alignment("TOOTHPASTE", "Cereals and Cereal Products")
        assert r["scanned_norm"]    == "Cosmetics"
        assert r["registered_norm"] == "Cereals and Cereal Products"
        assert r["is_match"]        is False

    def test_match_has_no_mismatch_type(self):
        r = check_subcategory_alignment("sugar", "Sweeteners")
        assert r["mismatch_type"] is None
