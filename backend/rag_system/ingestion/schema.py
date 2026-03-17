"""
ingestion/schema.py
-------------------
Typed data contracts for the SabiLens NAFDAC food-product ingestion pipeline.

Uses only Python standard-library dataclasses — no external schema dependencies
so the module is importable even before pip install completes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL DATA FACTS  (discovered by inspecting nafdac_database.xlsx, 15 rows)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Column inventory:
  S/n            – Row serial number 1–15.  Dropped after load (no analytical value).
  product_name   – Free-text product name.  Mixed ALL-CAPS / Title Case.
  nafdac_no      – NAFDAC registration number.  Formats: 'A8-4114', '01-0132'.
                   Row 2 ('\xa001-0132') and Row 9 ('\xa002-8608') carry a
                   non-breaking-space prefix (U+00A0) — must be stripped.
                   Row 11 ('A8-8893L') has a letter suffix — kept as-is.
  subcategory    – Product type within the food/cosmetics domain.
                   Values observed:
                     'Cereals and Cereal Products'  (4 rows)
                     'Cosmetics'                    (5 rows)  ← NAFDAC classifies
                     'Fats and oils, and Fat Emulsions' (2 rows)     cosmetics here
                     'Salts, Spices, Soups, Sauces, Salads and Seasoning' (2 rows)
                     'Beverages'                    (1 row)
                     'Sweeteners'                   (1 row)
  presentation   – Packaging description.  Plain text, variable length (6–119 chars).
                   Some rows describe physical appearance (colour, container type).
  applicant_name – Company that holds the NAFDAC registration.
                   Row 3 has a leading U+00A0: '\xa0UNILEVER NIGERIA PLC'.
  country        – Always 'Nigeria' across all 15 rows.  Kept for completeness.
  manufacturer   – Manufacturing entity.  May differ from applicant.
                   Row 2 has a leading tab: '\tUNILEVER NIG. PLC'.
  expiry_date    – Registration expiry date as a datetime string from Excel.
                   Format after pandas read: '2029-07-30 00:00:00'.
                   Range in this dataset: 2026-03-28 → 2031-01-26.
                   ALL dates are in the FUTURE (unlike the Greenbook dataset
                   where all dates were historical).  Expiry check is therefore
                   a meaningful, hard-enforced validation layer here.

No nulls anywhere in the dataset.  All 15 rows have valid values in all 9 columns.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass, asdict
from typing import Optional


# ── Canonical subcategory names (exact strings as they appear after normalisation) ──
VALID_SUBCATEGORIES = {
    "Cereals and Cereal Products",
    "Cosmetics",
    "Fats and oils, and Fat Emulsions",
    "Salts, Spices, Soups, Sauces, Salads and Seasoning",
    "Beverages",
    "Sweeteners",
    "Unknown",          # Fallback for any row whose subcategory is blank/null.
}


@dataclass
class NAFDACEntry:
    """
    Validated representation of one row from nafdac_database.xlsx.

    Populated by ingestion/excel_loader.py after all cleaning steps.
    Each field maps directly to a source column (S/n is dropped).

    Attributes:
        nafdac_no          Raw NAFDAC number as read from Excel (may still carry
                           whitespace if used before loader strips it).
        nafdac_no_clean    Canonical form produced by utils/nafdac_normalizer.py.
                           Used as the primary lookup key.
        product_name       Original product name (mixed casing preserved for display).
        product_name_upper Upper-cased version for case-insensitive text search.
        subcategory        One of the six real subcategory values above.
        presentation       Packaging / physical description string.
        applicant_name     NAFDAC-registered applicant company name.
        country            Always 'Nigeria' in this dataset.
        manufacturer       Manufacturing entity name.
        expiry_date_raw    Raw expiry string from Excel (e.g. '2029-07-30 00:00:00').
        expiry_date_iso    ISO-8601 date string extracted from raw ('2029-07-30').
                           Empty string '' if parsing failed.
    """
    nafdac_no: str
    nafdac_no_clean: str
    product_name: str
    product_name_upper: str
    subcategory: str
    presentation: str
    applicant_name: str
    country: str
    manufacturer: str
    expiry_date_raw: str
    expiry_date_iso: str          # 'YYYY-MM-DD' or ''


@dataclass
class ProductChunk:
    """
    The atomic unit stored in ChromaDB — one row equals one chunk.

    Why single-row chunks?
      Each NAFDAC registration is a discrete, indivisible regulatory fact.
      Merging rows would corrupt the nafdac_no ↔ product relationship.
      Splitting within a row would make no semantic sense for this schema.

    Attributes:
        chunk_id       Deterministic MD5 hash of (nafdac_no_clean + product_name_upper).
                       Guarantees safe re-ingestion via upsert without duplicates.
        text           Rich natural-language string built from all relevant fields.
                       This is what the embedding model encodes into a vector.
        metadata       Flat string-valued dict of all columns — required by ChromaDB
                       for WHERE-clause filtering without vector search.
        subcategory    Denormalised copy of subcategory for fast category filtering.
        nafdac_no_clean Denormalised clean NAFDAC number for fast NRN exact-match.
        expiry_date_iso Denormalised ISO date for expiry range queries.
    """
    chunk_id: str
    text: str
    metadata: dict               # All string values — ChromaDB requirement
    subcategory: str
    nafdac_no_clean: str
    expiry_date_iso: str         # '' when not parseable

    def model_dump(self) -> dict:
        """Serialise to a plain dict for json.dump().  Called by save_chunks()."""
        return asdict(self)