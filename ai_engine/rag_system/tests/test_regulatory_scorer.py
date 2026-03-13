"""
tests/test_regulatory_scorer.py
---------------------------------
Unit tests for the regulatory scoring / verification logic.

Tests exercise all four layers of the check sequence using mock database
records that mirror the actual nafdac_database.xlsx data.  No ChromaDB
or embedding model is needed — the scorer is pure Python logic.

Run:
    pytest tests/test_regulatory_scorer.py -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from retrieval.regulatory_scorer import compute_verification_score, _check_expiry


# ── Fixture records mirroring real rows from nafdac_database.xlsx ─────────────

CORN_FLAKES = {
    "nafdac_no"        : "A8-4114",
    "nafdac_no_clean"  : "A8-4114",
    "product_name"     : "KELLOGG'S CORN FLAKES",
    "subcategory"      : "Cereals and Cereal Products",
    "applicant_name"   : "KELLOGG TOLARAM NIGERIA LIMTED",
    "manufacturer"     : "KT LFTZ ENTERPRISE",
    "expiry_date_iso"  : "2029-07-30",
}

LIPTON_TEA = {
    "nafdac_no"        : "01-0132",
    "nafdac_no_clean"  : "01-0132",
    "product_name"     : "LIPTON YELLOW LABEL TEA",
    "subcategory"      : "Beverages",
    "applicant_name"   : "UNILEVER NIGERIA PLC",
    "manufacturer"     : "UNILEVER NIG. PLC",
    "expiry_date_iso"  : "2026-03-28",   # Near expiry (25 days from 2026-03-03)
}

VASELINE = {
    "nafdac_no"        : "02-0385",
    "nafdac_no_clean"  : "02-0385",
    "product_name"     : "Vaseline blueseal pure petroleum jelly original",
    "subcategory"      : "Cosmetics",
    "applicant_name"   : "UNILEVER NIGERIA PLC",
    "manufacturer"     : "UNILEVER NIGERIA PLC",
    "expiry_date_iso"  : "2028-12-20",
}

EXPIRED_RECORD = {
    "nafdac_no"        : "TEST-001",
    "nafdac_no_clean"  : "TEST-001",
    "product_name"     : "Expired Test Product",
    "subcategory"      : "Beverages",
    "applicant_name"   : "Test Company",
    "manufacturer"     : "Test Company",
    "expiry_date_iso"  : "2025-01-01",   # Already expired
}


class TestExpiryCheck:
    """Tests for the _check_expiry helper (internal but critical logic)."""

    def test_valid_far_future(self):
        r = _check_expiry("2029-07-30")
        assert r["is_valid"]       is True
        assert r["is_near_expiry"] is False
        assert r["severity"]       == "NONE"

    def test_near_expiry_within_60_days(self):
        """Lipton Tea expires 2026-03-28 — 25 days from reference 2026-03-03"""
        r = _check_expiry("2026-03-28")
        assert r["is_valid"]       is True
        assert r["is_near_expiry"] is True
        assert r["severity"]       == "WARNING"
        assert r["days_remaining"] == 25

    def test_expired(self):
        r = _check_expiry("2025-01-01")
        assert r["is_valid"]   is False
        assert r["severity"]   == "EXPIRED"
        assert r["days_remaining"] < 0

    def test_no_expiry_date(self):
        r = _check_expiry("")
        assert r["is_valid"]   is True
        assert r["severity"]   == "NONE"

    def test_invalid_date_string(self):
        r = _check_expiry("not-a-date")
        assert r["is_valid"]   is True   # Don't penalise unparseable dates


class TestComputeVerificationScore:
    """Tests for the full four-layer verification score."""

    # ── Layer 1: Not found ────────────────────────────────────────────────────

    def test_not_found_empty_records(self):
        r = compute_verification_score("FAKE-999", "cereal", [])
        assert r["verified"]           is False
        assert r["verification_score"] == 0.0
        assert r["status_code"]        == "NOT_FOUND"
        assert r["severity"]           == "CRITICAL"
        assert r["matched_record"]     is None

    # ── Layer 2: Expired registration ─────────────────────────────────────────

    def test_expired_registration(self):
        r = compute_verification_score("TEST-001", "beverage", [EXPIRED_RECORD])
        assert r["verified"]           is False
        assert r["verification_score"] == 0.1
        assert r["status_code"]        == "EXPIRED"
        assert r["severity"]           == "HIGH"
        assert r["expiry_check"]["is_valid"] is False

    # ── Layer 3: Subcategory mismatch ─────────────────────────────────────────

    def test_mismatch_cosmetic_on_cereal(self):
        """
        DEMO: Kellogg's NAFDAC number stamped on a fake cosmetic product.
        """
        r = compute_verification_score("A8-4114", "cosmetics", [CORN_FLAKES])
        assert r["verified"]           is False
        assert r["verification_score"] == 0.2
        assert r["status_code"]        == "SUBCATEGORY_MISMATCH"
        assert r["severity"]           == "CRITICAL"
        assert r["alignment"]["is_match"] is False

    def test_mismatch_food_on_cosmetic(self):
        """DEMO: Vaseline NAFDAC number on fake cooking oil."""
        r = compute_verification_score("02-0385", "cooking oil", [VASELINE])
        assert r["verified"]           is False
        assert r["verification_score"] == 0.2
        assert r["status_code"]        == "SUBCATEGORY_MISMATCH"

    # ── Layer 4: Verified ─────────────────────────────────────────────────────

    def test_fully_verified_corn_flakes(self):
        """Authentic Kellogg's Corn Flakes scan."""
        r = compute_verification_score("A8-4114", "corn flakes", [CORN_FLAKES])
        assert r["verified"]           is True
        assert r["verification_score"] == 1.0
        assert r["status_code"]        == "VERIFIED"
        assert r["severity"]           == "NONE"
        assert r["matched_record"]["product_name"] == "KELLOGG'S CORN FLAKES"

    def test_verified_near_expiry(self):
        """Lipton Tea is valid but near-expiry — score 0.85, status VERIFIED_NEAR_EXPIRY."""
        r = compute_verification_score("01-0132", "tea", [LIPTON_TEA])
        assert r["verified"]                    is True
        assert r["verification_score"]          == 0.85
        assert r["status_code"]                 == "VERIFIED_NEAR_EXPIRY"
        assert r["severity"]                    == "WARNING"
        assert r["expiry_check"]["is_near_expiry"] is True

    def test_verified_vaseline_cosmetic(self):
        r = compute_verification_score("02-0385", "petroleum jelly", [VASELINE])
        assert r["verified"]           is True
        assert r["verification_score"] == 1.0
        assert r["status_code"]        == "VERIFIED"

    # ── Response structure completeness ───────────────────────────────────────

    def test_all_response_keys_present_verified(self):
        r = compute_verification_score("A8-4114", "cereal", [CORN_FLAKES])
        expected_keys = {
            "verified", "verification_score", "status_code", "severity",
            "summary", "detail", "expiry_check", "alignment",
            "matched_record", "all_records",
        }
        assert expected_keys.issubset(set(r.keys()))

    def test_all_response_keys_present_not_found(self):
        r = compute_verification_score("FAKE-000", "beverage", [])
        expected_keys = {
            "verified", "verification_score", "status_code", "severity",
            "summary", "detail", "matched_record",
        }
        assert expected_keys.issubset(set(r.keys()))
