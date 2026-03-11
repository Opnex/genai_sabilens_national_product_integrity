"""
tests/test_excel_loader.py
---------------------------
Unit and integration tests for ingestion/excel_loader.py.

Tests cover:
  - Successful load of the real nafdac_database.xlsx (15 rows)
  - Data-quality issues in the file: NBSP in nafdac_no [rows 2,9],
    NBSP in applicant_name [row 3], tab in manufacturer [row 2]
  - Column header normalisation and slugification
  - expiry_date ISO extraction from Excel datetime strings
  - All 15 expiry dates are future (2026-2031)
  - Correct subcategory breakdown across 6 categories
  - Error handling: missing file, missing required columns

Run:
    pytest tests/test_excel_loader.py -v
"""
import sys, os, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingestion.excel_loader import load_database, _parse_expiry_date
from ingestion.schema import NAFDACEntry


def get_entries():
    return load_database("./data/raw/nafdac_database.xlsx")

def find_product(entries, frag):
    f = frag.upper()
    for e in entries:
        if f in e.product_name_upper:
            return e
    raise AssertionError(f"No entry containing '{frag}'")


class TestLoadDatabaseIntegration:

    def test_returns_15_entries(self):
        entries, _ = get_entries()
        assert len(entries) == 15

    def test_report_total_rows_15(self):
        _, report = get_entries()
        assert report["total_rows"] == 15

    def test_report_entries_built_15(self):
        _, report = get_entries()
        assert report["entries_built"] == 15

    def test_zero_null_nafdac_rows(self):
        _, report = get_entries()
        assert report["null_nafdac_rows"] == 0

    def test_subcategory_breakdown_exact(self):
        _, report = get_entries()
        bd = report["subcategory_breakdown"]
        assert bd["Cereals and Cereal Products"]                         == 4
        assert bd["Cosmetics"]                                           == 5
        assert bd["Fats and oils, and Fat Emulsions"]                    == 2
        assert bd["Salts, Spices, Soups, Sauces, Salads and Seasoning"] == 2
        assert bd["Beverages"]                                           == 1
        assert bd["Sweeteners"]                                          == 1

    def test_all_entries_are_nafdac_entry_instances(self):
        entries, _ = get_entries()
        assert all(isinstance(e, NAFDACEntry) for e in entries)

    def test_no_empty_product_names(self):
        entries, _ = get_entries()
        for e in entries:
            assert e.product_name.strip() != ""

    def test_all_expiry_dates_present_and_formatted(self):
        entries, _ = get_entries()
        for e in entries:
            assert len(e.expiry_date_iso) == 10, f"Bad expiry for {e.product_name}"

    def test_country_always_nigeria(self):
        entries, _ = get_entries()
        assert all(e.country == "Nigeria" for e in entries)

    def test_product_name_upper_correct(self):
        entries, _ = get_entries()
        for e in entries:
            assert e.product_name_upper == e.product_name.upper()

    def test_all_expiry_dates_are_future(self):
        from datetime import date
        entries, _ = get_entries()
        today = date(2026, 3, 3)
        for e in entries:
            assert date.fromisoformat(e.expiry_date_iso) > today, \
                f"{e.product_name}: {e.expiry_date_iso} is not in the future"


class TestProductFieldValues:

    def test_kelloggs_corn_flakes(self):
        entries, _ = get_entries()
        e = find_product(entries, "KELLOGG'S CORN FLAKES")
        assert e.nafdac_no_clean == "A8-4114"
        assert e.subcategory     == "Cereals and Cereal Products"
        assert e.expiry_date_iso == "2029-07-30"

    def test_lipton_nbsp_stripped_from_nafdac(self):
        """Row 2: nafdac_no is '\\xa001-0132' in Excel. Must become '01-0132'."""
        entries, _ = get_entries()
        e = find_product(entries, "LIPTON")
        assert e.nafdac_no_clean == "01-0132"
        assert "\xa0" not in e.nafdac_no_clean

    def test_lipton_near_expiry_date(self):
        entries, _ = get_entries()
        e = find_product(entries, "LIPTON")
        assert e.expiry_date_iso == "2026-03-28"

    def test_lipton_tab_stripped_from_manufacturer(self):
        """Row 2: manufacturer is '\\tUNILEVER NIG. PLC' in Excel. Tab must be stripped."""
        entries, _ = get_entries()
        e = find_product(entries, "LIPTON")
        assert "\t" not in e.manufacturer

    def test_pepsodent_nbsp_stripped_from_nafdac(self):
        """Row 9: nafdac_no is '\\xa002-8608' in Excel. Must become '02-8608'."""
        entries, _ = get_entries()
        e = find_product(entries, "Pepsodent")
        assert e.nafdac_no_clean == "02-8608"
        assert "\xa0" not in e.nafdac_no_clean

    def test_closeup_nbsp_stripped_from_applicant(self):
        """Row 3: applicant_name is '\\xa0UNILEVER NIGERIA PLC'. Must be stripped."""
        entries, _ = get_entries()
        e = find_product(entries, "Closeup")
        assert "\xa0" not in e.applicant_name
        assert e.nafdac_no_clean == "A2-5334"

    def test_sedoso_letter_suffix_preserved(self):
        """'A8-8893L' has a letter suffix — must be kept, not stripped."""
        entries, _ = get_entries()
        e = find_product(entries, "SEDOSO")
        assert e.nafdac_no_clean == "A8-8893L"

    def test_dangote_sugar(self):
        entries, _ = get_entries()
        e = find_product(entries, "DANGOTE")
        assert e.nafdac_no_clean == "A8-100798"
        assert e.subcategory     == "Sweeteners"

    def test_indomie_noodles(self):
        entries, _ = get_entries()
        e = find_product(entries, "INDOMIE")
        assert e.nafdac_no_clean == "01-0877"
        assert e.subcategory     == "Cereals and Cereal Products"

    def test_vaseline_blueseal(self):
        entries, _ = get_entries()
        e = find_product(entries, "Vaseline blueseal")
        assert e.nafdac_no_clean == "02-0385"
        assert e.subcategory     == "Cosmetics"

    def test_golden_terra_soya_oil(self):
        entries, _ = get_entries()
        e = find_product(entries, "GOLDEN TERRA")
        assert e.nafdac_no_clean == "A8-4890"
        assert e.subcategory     == "Fats and oils, and Fat Emulsions"

    def test_peppe_terra_seasoning(self):
        entries, _ = get_entries()
        e = find_product(entries, "PEPPE TERRA")
        assert e.nafdac_no_clean == "A8-103753"
        assert e.subcategory     == "Salts, Spices, Soups, Sauces, Salads and Seasoning"


class TestParseExpiryDate:

    def test_excel_datetime_format(self):
        assert _parse_expiry_date("2029-07-30 00:00:00") == "2029-07-30"

    def test_date_only_string(self):
        assert _parse_expiry_date("2026-03-28") == "2026-03-28"

    def test_empty_returns_empty(self):
        assert _parse_expiry_date("") == ""

    def test_nan_returns_empty(self):
        assert _parse_expiry_date("nan") == ""

    def test_none_returns_empty(self):
        assert _parse_expiry_date("None") == ""

    def test_invalid_returns_empty(self):
        assert _parse_expiry_date("not-a-date") == ""

    def test_all_15_real_dates_parse(self):
        """Every expiry date value from nafdac_database.xlsx must parse correctly."""
        real_dates = [
            "2029-07-30 00:00:00", "2029-07-30 00:00:00", "2026-03-28 00:00:00",
            "2031-01-26 00:00:00", "2027-01-26 00:00:00", "2028-12-20 00:00:00",
            "2029-12-17 00:00:00", "2027-01-26 00:00:00", "2029-09-24 00:00:00",
            "2029-04-29 00:00:00", "2028-12-20 00:00:00", "2026-12-17 00:00:00",
            "2029-07-30 00:00:00", "2028-12-20 00:00:00", "2030-01-29 00:00:00",
        ]
        for raw in real_dates:
            result = _parse_expiry_date(raw)
            assert len(result) == 10, f"Failed to parse: {raw!r}"
            assert 2026 <= int(result[:4]) <= 2031, f"Unexpected year: {result}"


class TestLoadDatabaseErrors:

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError, match="Database not found"):
            load_database("./data/raw/does_not_exist.xlsx")

    def test_missing_required_columns_raises(self, tmp_path):
        import pandas as pd
        bad_path = tmp_path / "bad.xlsx"
        pd.DataFrame({"foo": ["bar"]}).to_excel(bad_path, index=False)
        with pytest.raises(ValueError, match="Required columns missing"):
            load_database(str(bad_path))
