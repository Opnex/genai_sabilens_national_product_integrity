"""
tests/test_nafdac_normalizer.py
--------------------------------
Unit tests for NAFDAC number normalisation logic.

Every test case is derived from actual data in nafdac_database.xlsx or
from known NAFDAC number formats observed across the broader NAFDAC
Greenbook dataset.  No hypothetical inputs.

Run:
    pytest tests/test_nafdac_normalizer.py -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.nafdac_normalizer import normalize_nafdac_no, is_valid_nafdac_no


class TestNormalizeNafdacNo:

    # ── Standard forms already in canonical form ──────────────────────────────

    def test_standard_alpha_short(self):
        """'A8-4114' → 'A8-4114'  (Kellogg's Corn Flakes)"""
        assert normalize_nafdac_no("A8-4114") == "A8-4114"

    def test_standard_alpha_long_serial(self):
        """'A8-100798' → 'A8-100798'  (Dangote Sugar — long serial)"""
        assert normalize_nafdac_no("A8-100798") == "A8-100798"

    def test_standard_numeric_prefix(self):
        """'01-0132' → '01-0132'  (Lipton Tea — numeric prefix)"""
        assert normalize_nafdac_no("01-0132") == "01-0132"

    def test_standard_a2_prefix(self):
        """'A2-5334' → 'A2-5334'  (Closeup Toothpaste)"""
        assert normalize_nafdac_no("A2-5334") == "A2-5334"

    def test_standard_letter_suffix(self):
        """'A8-8893L' → 'A8-8893L'  (Sedoso Vegetable Oil — letter suffix kept)"""
        assert normalize_nafdac_no("A8-8893L") == "A8-8893L"

    def test_lowercase_uppercased(self):
        """'a8-4114' → 'A8-4114'  (OCR may output lowercase)"""
        assert normalize_nafdac_no("a8-4114") == "A8-4114"

    def test_leading_trailing_ascii_whitespace(self):
        """'  A8-4114  ' → 'A8-4114'  (accidental spaces)"""
        assert normalize_nafdac_no("  A8-4114  ") == "A8-4114"

    # ── Non-breaking space prefix (real data rows 2 and 9) ───────────────────

    def test_nbsp_prefix_01_series(self):
        """'\\xa001-0132' → '01-0132'  (Lipton Tea, actual row 2)"""
        assert normalize_nafdac_no("\xa001-0132") == "01-0132"

    def test_nbsp_prefix_02_series(self):
        """'\\xa002-8608' → '02-8608'  (Pepsodent, actual row 9)"""
        assert normalize_nafdac_no("\xa002-8608") == "02-8608"

    def test_nbsp_embedded_in_middle(self):
        """'A8\xa0-4114' → 'A8-4114'  (NBSP anywhere in string)"""
        assert normalize_nafdac_no("A8\xa0-4114") == "A8-4114"

    # ── Spaced-dash variants (observed across broader NAFDAC data) ─────────────

    def test_spaces_around_dash_alpha(self):
        """'A4 - 5180' → 'A4-5180'"""
        assert normalize_nafdac_no("A4 - 5180") == "A4-5180"

    def test_spaces_around_dash_numeric(self):
        """'04 - 1508' → '04-1508'"""
        assert normalize_nafdac_no("04 - 1508") == "04-1508"

    def test_space_after_dash_only(self):
        """'04- 9502' → '04-9502'  (trailing space after dash)"""
        assert normalize_nafdac_no("04- 9502") == "04-9502"

    # ── En-dash / em-dash variants ─────────────────────────────────────────────

    def test_en_dash(self):
        """'04\u20132045' → '04-2045'  (en-dash U+2013)"""
        assert normalize_nafdac_no("04\u20132045") == "04-2045"

    def test_en_dash_with_spaces(self):
        """'04 \u2013 1486' → '04-1486'"""
        assert normalize_nafdac_no("04 \u2013 1486") == "04-1486"

    # ── Legacy slash format (older NAFDAC registrations) ──────────────────────

    def test_slash_format(self):
        """'4/1/9086' → '4-9086'"""
        assert normalize_nafdac_no("4/1/9086") == "4-9086"

    def test_slash_format_variant(self):
        """'4/1/4430' → '4-4430'"""
        assert normalize_nafdac_no("4/1/4430") == "4-4430"

    # ── Null / invalid inputs → None ──────────────────────────────────────────

    def test_none_input(self):
        assert normalize_nafdac_no(None) is None

    def test_empty_string(self):
        assert normalize_nafdac_no("") is None

    def test_whitespace_only(self):
        assert normalize_nafdac_no("   ") is None

    def test_na_string(self):
        assert normalize_nafdac_no("NA") is None

    def test_not_available_yet(self):
        assert normalize_nafdac_no("Not available yet") is None

    def test_completely_invalid(self):
        """'FAKE-XYZ' — no numeric serial — cannot normalise"""
        assert normalize_nafdac_no("FAKE-XYZ") is None

    def test_random_text(self):
        assert normalize_nafdac_no("not a registration number") is None


class TestIsValidNafdacNo:

    def test_canonical_alpha(self):
        assert is_valid_nafdac_no("A8-4114") is True

    def test_canonical_numeric_prefix(self):
        assert is_valid_nafdac_no("01-0132") is True

    def test_canonical_letter_suffix(self):
        assert is_valid_nafdac_no("A8-8893L") is True

    def test_none_invalid(self):
        assert is_valid_nafdac_no(None) is False

    def test_empty_invalid(self):
        assert is_valid_nafdac_no("") is False

    def test_raw_form_invalid(self):
        """Raw forms are NOT valid canonical — must call normalize first."""
        assert is_valid_nafdac_no("\xa001-0132") is False

    def test_spaced_dash_invalid(self):
        assert is_valid_nafdac_no("A4 - 5180") is False