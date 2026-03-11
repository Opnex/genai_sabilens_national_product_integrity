"""
tests/test_chunk_builder.py
-----------------------------
Unit tests for ingestion/chunk_builder.py.

Verifies:
  - build_chunks() produces one chunk per unique (NAFDAC no + product name)
  - True duplicates are detected and skipped with a count
  - chunk_id is deterministic and 32-char hex
  - Different products always get different IDs
  - Chunk text contains all important fields in the correct format
  - Empty presentation field is omitted from chunk text
  - All metadata values are plain strings (ChromaDB requirement)
  - All expected metadata keys are present
  - save_chunks() writes valid JSON with the correct structure
  - Subcategory breakdown stats are accurate

Fixtures are built from real product data in nafdac_database.xlsx.

Run:
    pytest tests/test_chunk_builder.py -v
"""
import sys, os, json, tempfile, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingestion.schema import NAFDACEntry
from ingestion.chunk_builder import build_chunks, save_chunks, _build_chunk_id, _build_text


# ── Fixture factory ────────────────────────────────────────────────────────────

def make_entry(**kwargs) -> NAFDACEntry:
    """Build a NAFDACEntry with Kellogg's Corn Flakes defaults, overridable by kwargs."""
    defaults = dict(
        nafdac_no          = "A8-4114",
        nafdac_no_clean    = "A8-4114",
        product_name       = "KELLOGG'S CORN FLAKES",
        product_name_upper = "KELLOGG'S CORN FLAKES",
        subcategory        = "Cereals and Cereal Products",
        presentation       = "300G HARDBOARD PACK",
        applicant_name     = "KELLOGG TOLARAM NIGERIA LIMTED",
        country            = "Nigeria",
        manufacturer       = "KT LFTZ ENTERPRISE",
        expiry_date_raw    = "2029-07-30 00:00:00",
        expiry_date_iso    = "2029-07-30",
    )
    defaults.update(kwargs)
    return NAFDACEntry(**defaults)


# Reusable real-data fixtures
CORN_FLAKES = make_entry()
COCO_POPS   = make_entry(
    nafdac_no="A8-2361", nafdac_no_clean="A8-2361",
    product_name="KELLOGG'S COCO POPS", product_name_upper="KELLOGG'S COCO POPS",
)
LIPTON      = make_entry(
    nafdac_no="01-0132", nafdac_no_clean="01-0132",
    product_name="LIPTON YELLOW LABEL TEA", product_name_upper="LIPTON YELLOW LABEL TEA",
    subcategory="Beverages", presentation="25 x 2.0g in Hard board pack",
    applicant_name="UNILEVER NIGERIA PLC", manufacturer="UNILEVER NIG. PLC",
    expiry_date_iso="2026-03-28",
)
VASELINE    = make_entry(
    nafdac_no="02-0385", nafdac_no_clean="02-0385",
    product_name="Vaseline blueseal pure petroleum jelly original",
    product_name_upper="VASELINE BLUESEAL PURE PETROLEUM JELLY ORIGINAL",
    subcategory="Cosmetics",
    presentation="Light yellow gel with a blue cover and transparent body PET 225ml",
    applicant_name="UNILEVER NIGERIA PLC", expiry_date_iso="2028-12-20",
)
DANGOTE     = make_entry(
    nafdac_no="A8-100798", nafdac_no_clean="A8-100798",
    product_name="DANGOTE SUGAR REFINED GRANULATED WHITE SUGAR",
    product_name_upper="DANGOTE SUGAR REFINED GRANULATED WHITE SUGAR",
    subcategory="Sweeteners", presentation="",   # Empty presentation — real data
    applicant_name="DANGOTE SUGAR REFINERY PLC",
    manufacturer="Dangote Sugar refinery Plc",
    expiry_date_iso="2027-01-26",
)


class TestBuildChunks:

    def test_3_entries_produce_3_chunks(self):
        chunks, stats = build_chunks([CORN_FLAKES, COCO_POPS, LIPTON])
        assert stats["chunks_built"] == 3
        assert stats["duplicates_skipped"] == 0

    def test_duplicate_entry_is_skipped(self):
        """Two identical entries (same NAFDAC + same product name) → only 1 chunk."""
        chunks, stats = build_chunks([CORN_FLAKES, CORN_FLAKES, COCO_POPS])
        assert stats["chunks_built"] == 2
        assert stats["duplicates_skipped"] == 1

    def test_multiple_duplicates_all_skipped(self):
        chunks, stats = build_chunks([CORN_FLAKES, CORN_FLAKES, CORN_FLAKES])
        assert stats["chunks_built"] == 1
        assert stats["duplicates_skipped"] == 2

    def test_different_product_same_nafdac_not_duplicate(self):
        """Same NAFDAC number but different product_name → two distinct chunks."""
        variant = make_entry(product_name="KELLOGG'S VARIANT", product_name_upper="KELLOGG'S VARIANT")
        chunks, stats = build_chunks([CORN_FLAKES, variant])
        assert stats["chunks_built"] == 2
        assert stats["duplicates_skipped"] == 0

    def test_empty_list_returns_empty(self):
        chunks, stats = build_chunks([])
        assert stats["chunks_built"] == 0
        assert stats["duplicates_skipped"] == 0

    def test_subcategory_breakdown(self):
        chunks, stats = build_chunks([CORN_FLAKES, COCO_POPS, LIPTON, VASELINE, DANGOTE])
        bd = stats["subcategory_breakdown"]
        assert bd["Cereals and Cereal Products"] == 2
        assert bd["Beverages"]  == 1
        assert bd["Cosmetics"]  == 1
        assert bd["Sweeteners"] == 1

    def test_null_nafdac_chunk_count(self):
        no_nafdac = make_entry(nafdac_no_clean="")
        chunks, stats = build_chunks([no_nafdac, CORN_FLAKES])
        assert stats["null_nafdac_chunks"] == 1


class TestChunkId:

    def test_deterministic_across_calls(self):
        id1 = _build_chunk_id("A8-4114", "KELLOGG'S CORN FLAKES")
        id2 = _build_chunk_id("A8-4114", "KELLOGG'S CORN FLAKES")
        assert id1 == id2

    def test_is_32_char_hex(self):
        chunk_id = _build_chunk_id("A8-4114", "KELLOGG'S CORN FLAKES")
        assert len(chunk_id) == 32
        assert all(c in "0123456789abcdef" for c in chunk_id)

    def test_different_nafdac_different_id(self):
        id1 = _build_chunk_id("A8-4114", "PRODUCT X")
        id2 = _build_chunk_id("A8-2361", "PRODUCT X")
        assert id1 != id2

    def test_different_product_name_different_id(self):
        id1 = _build_chunk_id("A8-4114", "PRODUCT A")
        id2 = _build_chunk_id("A8-4114", "PRODUCT B")
        assert id1 != id2

    def test_empty_nafdac_still_generates_id(self):
        chunk_id = _build_chunk_id("", "SOME PRODUCT")
        assert len(chunk_id) == 32


class TestBuildText:

    def test_contains_product_name(self):
        assert "KELLOGG'S CORN FLAKES" in _build_text(CORN_FLAKES)

    def test_contains_nafdac_no(self):
        assert "A8-4114" in _build_text(CORN_FLAKES)

    def test_contains_subcategory(self):
        assert "Cereals and Cereal Products" in _build_text(CORN_FLAKES)

    def test_contains_applicant(self):
        assert "KELLOGG TOLARAM" in _build_text(CORN_FLAKES)

    def test_contains_manufacturer(self):
        assert "KT LFTZ ENTERPRISE" in _build_text(CORN_FLAKES)

    def test_contains_expiry_date(self):
        assert "2029-07-30" in _build_text(CORN_FLAKES)

    def test_contains_presentation_when_present(self):
        assert "300G HARDBOARD PACK" in _build_text(CORN_FLAKES)

    def test_contains_country(self):
        assert "Nigeria" in _build_text(CORN_FLAKES)

    def test_empty_presentation_omitted(self):
        """Dangote Sugar has an empty presentation field — it must not appear in text."""
        text = _build_text(DANGOTE)
        assert "Presentation:" not in text

    def test_long_presentation_fully_included(self):
        """
        Vaseline has a 66-char presentation:
        'Light yellow gel with a blue cover and transparent body PET 225ml'
        Must be fully included for packaging-based semantic search.
        """
        text = _build_text(VASELINE)
        assert "Light yellow gel" in text

    def test_lipton_near_expiry_text(self):
        text = _build_text(LIPTON)
        assert "2026-03-28" in text
        assert "Beverages" in text


class TestMetadata:

    def test_all_metadata_values_are_strings(self):
        """ChromaDB requires all metadata values to be strings."""
        chunks, _ = build_chunks([CORN_FLAKES])
        for key, val in chunks[0].metadata.items():
            assert isinstance(val, str), \
                f"metadata['{key}'] is {type(val).__name__}, expected str"

    def test_all_required_metadata_keys_present(self):
        chunks, _ = build_chunks([CORN_FLAKES])
        expected = {
            "nafdac_no", "nafdac_no_clean", "product_name", "product_name_upper",
            "subcategory", "presentation", "applicant_name", "country",
            "manufacturer", "expiry_date_raw", "expiry_date_iso",
        }
        assert expected.issubset(set(chunks[0].metadata.keys()))

    def test_metadata_nafdac_no_clean_correct(self):
        chunks, _ = build_chunks([CORN_FLAKES])
        assert chunks[0].metadata["nafdac_no_clean"] == "A8-4114"

    def test_metadata_subcategory_correct(self):
        chunks, _ = build_chunks([VASELINE])
        assert chunks[0].metadata["subcategory"] == "Cosmetics"


class TestSaveChunks:

    def test_writes_valid_json(self):
        chunks, _ = build_chunks([CORN_FLAKES, LIPTON])
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "out", "chunks.json")
            save_chunks(chunks, path)
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert len(data) == 2

    def test_saved_chunk_has_required_keys(self):
        chunks, _ = build_chunks([CORN_FLAKES])
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "chunks.json")
            save_chunks(chunks, path)
            with open(path) as f:
                data = json.load(f)
            assert "chunk_id"  in data[0]
            assert "text"      in data[0]
            assert "metadata"  in data[0]

    def test_creates_parent_directories(self):
        chunks, _ = build_chunks([CORN_FLAKES])
        with tempfile.TemporaryDirectory() as td:
            deep_path = os.path.join(td, "a", "b", "c", "chunks.json")
            save_chunks(chunks, deep_path)
            assert os.path.exists(deep_path)
