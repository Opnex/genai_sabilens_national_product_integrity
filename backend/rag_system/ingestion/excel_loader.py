"""
ingestion/excel_loader.py
--------------------------
Loads, validates, and normalises the NAFDAC food-product Excel database into a
clean list of NAFDACEntry objects ready for the chunk builder.

SINGLE RESPONSIBILITY
  This module handles file I/O and data cleaning only.
  It does not build chunks, embed text, or touch ChromaDB.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA-QUALITY ISSUES IN nafdac_database.xlsx  (all handled here)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Issue                               Rows affected  Fix applied
  ──────────────────────────────────  ─────────────  ─────────────────────────
  U+00A0 prefix in nafdac_no          2 (rows 2, 9)  normalize_nafdac_no()
  U+00A0 prefix in applicant_name     1 (row 3)      strip_nonstandard_whitespace()
  Leading tab (\t) in manufacturer    1 (row 2)      strip_nonstandard_whitespace()
  Mixed ALL-CAPS / Title Case names   many           preserved for display;
                                                     upper-cased copy created for search
  Letter suffix on nafdac_no          1 (row 11)     handled by normaliser (kept)
  expiry_date stored as datetime str  all 15         parsed to ISO 'YYYY-MM-DD'
  S/n column (serial number)          all 15         dropped — no analytical value
  country always 'Nigeria'            all 15         kept for completeness
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
import pandas as pd
from pathlib import Path
from typing import Tuple

from config.settings import settings
from ingestion.schema import NAFDACEntry
from utils.nafdac_normalizer import normalize_nafdac_no


# ── Expected source columns (lowercase, post-header-normalisation) ─────────────
_REQUIRED_COLUMNS = {"product_name", "nafdac_no", "subcategory", "applicant_name"}
_ALL_EXPECTED_COLUMNS = {
    "s/n", "product_name", "nafdac_no", "subcategory",
    "presentation", "applicant_name", "country", "manufacturer", "expiry_date",
}

# ── Non-standard whitespace characters to strip from string fields ──────────────
# U+00A0 = non-breaking space (found in nafdac_no, applicant_name)
# \t     = tab (found in manufacturer)
_NONSTANDARD_WS_PATTERN = re.compile(r"[\u00a0\t\r]+")


# ── Private helpers ────────────────────────────────────────────────────────────

def _normalise_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lowercase, strip, and slugify all column headers.

    Converts 'S/n' → 's/n', 'Product_Name' → 'product_name', etc.
    Called immediately after pd.read_excel so all downstream references
    use consistent lowercase names.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    """
    Raise ValueError if any required column is absent from the DataFrame.

    Surfaces problems early with a clear message rather than a cryptic KeyError
    later in the pipeline.

    Raises:
        ValueError: Lists the missing columns and what was actually found.
    """
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"[Loader] Required columns missing from database: {missing}\n"
            f"Found columns: {sorted(df.columns.tolist())}\n"
            f"Expected at minimum: {sorted(_REQUIRED_COLUMNS)}"
        )


def _clean_string_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip standard and non-standard whitespace from every string column.

    Handles:
      - Leading/trailing ASCII whitespace (spaces, newlines)
      - U+00A0 non-breaking spaces embedded anywhere in the string
      - Leading tab characters (\\t) found in the 'manufacturer' column
      - Replaces pure-whitespace values with empty string ''
    """
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .apply(lambda v: _NONSTANDARD_WS_PATTERN.sub(" ", v).strip())
        )
        # Collapse anything that became '' or 'nan' after strip
        df[col] = df[col].replace({"nan": "", "None": "", "NaN": ""})
    return df


def _parse_expiry_date(raw: str) -> str:
    """
    Extract the ISO-8601 date portion from an Excel datetime string.

    Excel reads the expiry_date column as '2029-07-30 00:00:00' (datetime
    string with a zero-time suffix).  We want only the date part: '2029-07-30'.

    Args:
        raw: String like '2029-07-30 00:00:00', '2026-03-28', or ''.

    Returns:
        'YYYY-MM-DD' string, or '' if parsing fails.

    Examples:
        >>> _parse_expiry_date('2029-07-30 00:00:00')
        '2029-07-30'
        >>> _parse_expiry_date('2026-03-28')
        '2026-03-28'
        >>> _parse_expiry_date('')
        ''
    """
    if not raw or raw in ("", "nan", "None"):
        return ""
    try:
        # pandas Timestamp is forgiving with both date-only and datetime strings
        ts = pd.Timestamp(raw)
        return ts.strftime("%Y-%m-%d")
    except Exception:
        return ""


def _build_entry(row: pd.Series, warnings: list) -> NAFDACEntry:
    """
    Construct a single NAFDACEntry from a cleaned DataFrame row.

    Normalises the nafdac_no, parses the expiry date, and uppercases the
    product_name for case-insensitive search support.

    Args:
        row:      A single row from the cleaned DataFrame (as a pd.Series).
        warnings: Mutable list — any data-quality observations are appended here
                  for inclusion in the final ingestion report.

    Returns:
        A populated NAFDACEntry dataclass instance.
    """
    raw_nafdac = str(row.get("nafdac_no", "")).strip()
    clean_nafdac = normalize_nafdac_no(raw_nafdac) or ""

    # Log cases where normalisation actually changed the value
    if clean_nafdac and clean_nafdac != raw_nafdac.upper():
        warnings.append(
            f"NAFDAC normalised: {repr(raw_nafdac)} → {repr(clean_nafdac)}"
        )
    elif not clean_nafdac and raw_nafdac:
        warnings.append(
            f"NAFDAC could not be normalised (set to empty): {repr(raw_nafdac)}"
        )

    product_name = str(row.get("product_name", "")).strip()
    expiry_raw   = str(row.get("expiry_date", "")).strip()
    expiry_iso   = _parse_expiry_date(expiry_raw)

    return NAFDACEntry(
        nafdac_no          = raw_nafdac,
        nafdac_no_clean    = clean_nafdac,
        product_name       = product_name,
        product_name_upper = product_name.upper(),
        subcategory        = str(row.get("subcategory", "Unknown")).strip() or "Unknown",
        presentation       = str(row.get("presentation", "")).strip(),
        applicant_name     = str(row.get("applicant_name", "")).strip(),
        country            = str(row.get("country", "Nigeria")).strip(),
        manufacturer       = str(row.get("manufacturer", "")).strip(),
        expiry_date_raw    = expiry_raw,
        expiry_date_iso    = expiry_iso,
    )


# ── Public interface ───────────────────────────────────────────────────────────

def load_database(path: str = None) -> Tuple[list, dict]:
    """
    Load and validate the NAFDAC food-product Excel file.

    This is the only public function in this module.  All private helpers
    are called in the strict sequence documented in the Returns section below.

    Args:
        path: Optional file path override.  Defaults to settings.DATABASE_PATH.
              Supply an alternative path when running tests with fixture files.

    Returns:
        Tuple of:
          entries (list[NAFDACEntry]): One entry per valid row, fully cleaned.
          report  (dict):             Data-quality summary for the ingestion log.
            Keys:
              total_rows        — rows read from Excel (15 for this dataset)
              entries_built     — entries successfully constructed
              null_nafdac_rows  — rows where normalised NAFDAC number is empty
              subcategory_breakdown — {subcategory: count}
              warnings          — list of data-quality observation strings

    Raises:
        FileNotFoundError: Database Excel file not found at the specified path.
        ValueError:        Required columns are missing from the file.

    Example:
        >>> entries, report = load_database()
        >>> print(f"Loaded {len(entries)} products")
        Loaded 15 products
        >>> print(report['subcategory_breakdown'])
        {'Cosmetics': 5, 'Cereals and Cereal Products': 4, ...}
    """
    filepath = path or settings.DATABASE_PATH
    warnings: list[str] = []

    # ── Step 1: file existence ───────────────────────────────────────────────
    if not Path(filepath).exists():
        raise FileNotFoundError(
            f"[Loader] Database not found at: {filepath}\n"
            f"Place nafdac_database.xlsx at that path or set "
            f"the DATABASE_PATH environment variable."
        )

    print(f"[Loader] Reading: {filepath}")

    # ── Step 2: read Excel ───────────────────────────────────────────────────
    # dtype=str prevents pandas from coercing NAFDAC numbers or percentage
    # strengths into wrong Python types.
    df = pd.read_excel(filepath, dtype=str)
    total_rows = len(df)
    print(f"[Loader] Read {total_rows} rows across {len(df.columns)} columns.")

    # ── Step 3: normalise column headers ────────────────────────────────────
    df = _normalise_headers(df)

    # ── Step 4: validate required columns ───────────────────────────────────
    _validate_columns(df)

    # ── Step 5: clean non-standard whitespace from all string fields ─────────
    df = _clean_string_fields(df)

    # ── Step 6: drop S/n column (serial row number — no analytical value) ───
    if "s/n" in df.columns:
        df = df.drop(columns=["s/n"])

    # ── Step 7: build NAFDACEntry objects for each row ───────────────────────
    entries: list[NAFDACEntry] = []
    for idx, row in df.iterrows():
        entry = _build_entry(row, warnings)
        entries.append(entry)

    # ── Step 8: count rows with unresolvable NAFDAC numbers ─────────────────
    null_nafdac = sum(1 for e in entries if not e.nafdac_no_clean)
    if null_nafdac > 0:
        warnings.append(
            f"{null_nafdac} row(s) have no valid NAFDAC number — "
            f"they are included but cannot be retrieved by NAFDAC number lookup."
        )

    # ── Step 9: build report ─────────────────────────────────────────────────
    from collections import Counter
    subcategory_counts = Counter(e.subcategory for e in entries)

    report = {
        "total_rows"            : total_rows,
        "entries_built"         : len(entries),
        "null_nafdac_rows"      : null_nafdac,
        "subcategory_breakdown" : dict(subcategory_counts),
        "warnings"              : warnings,
    }

    print(f"[Loader] Built {len(entries)} entries.")
    print(f"[Loader] Subcategories: {dict(subcategory_counts)}")
    if warnings:
        print(f"[Loader] {len(warnings)} data-quality warnings — "
              f"see ingestion report for details.")

    return entries, report