"""
utils/nafdac_normalizer.py
--------------------------
Standalone utility for cleaning and canonicalising NAFDAC registration numbers
(referred to interchangeably as NAFDAC numbers or NRNs throughout the project).

WHY A STANDALONE MODULE?
  Normalisation logic is shared across three layers:
    1. ingestion/excel_loader.py   — cleaning source data on load
    2. retrieval/retriever.py      — cleaning OCR output before lookup
    3. tests/                      — unit-testing normalisation in isolation

  One module → one fix propagates everywhere.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EDGE CASES OBSERVED IN nafdac_database.xlsx  (15 rows)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Standard — alpha prefix   : 'A8-4114',  'A2-5334',  'A1-0291'
  Standard — numeric prefix : '01-0132',  '08-8836',  '02-8608'
  Long serial               : 'A8-100798','A8-103753','A2-102856','A2-106037'
  Letter suffix             : 'A8-8893L'                (kept as-is — valid format)
  Leading U+00A0 (NBSP)     : '\xa001-0132', '\xa002-8608'   → strip and normalise
  Spaces around dash        : 'A4 - 5180'  (from earlier Greenbook; handled for robustness)
  En-dash / em-dash         : '04–2045'    (same)
  Slash format (legacy)     : '4/1/9086'   (same)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
from typing import Optional

# ── Unicode character substitution table ──────────────────────────────────────
# Applied as the first cleaning step before any regex matching.
_UNICODE_SUBS = str.maketrans({
    "\u2013": "-",    # en-dash  → ASCII hyphen
    "\u2014": "-",    # em-dash  → ASCII hyphen
    "\u2212": "-",    # minus    → ASCII hyphen
    "\u00a0": "",     # non-breaking space → empty (strip)
    "\u00ad": "",     # soft hyphen         → empty
})

# ── Regex patterns ─────────────────────────────────────────────────────────────
# NRN with spaces around the dash:  'A4 - 5180',  '04 - 1508'
_SPACED_DASH = re.compile(r"^([A-Za-z0-9]+)\s*[-–—]\s*(\d+[A-Za-z]?)$")

# Old slash-format NRNs:  '4/1/9086'  → '4-9086'
_SLASH_FORMAT = re.compile(r"^(\d+)/\d+/(\d+[A-Za-z]?)$")

# Canonical form after all cleaning:  prefix + hyphen + digits (+ optional letter)
_CANONICAL_PATTERN = re.compile(r"^[A-Z0-9]+-\d+[A-Z]?$")

# Strings that unambiguously mean "no NAFDAC number available"
_NULL_SENTINELS = frozenset({
    "", "na", "n/a", "nan", "none", "null", "-",
    "not available", "not available yet",
})


def normalize_nafdac_no(raw: Optional[str]) -> Optional[str]:
    """
    Clean and canonicalise a raw NAFDAC registration number string.

    Canonical form: UPPERCASE, single ASCII hyphen, no whitespace.
    Examples of canonical form: 'A8-4114', '01-0132', 'A8-8893L'

    The function applies transformations in a strict priority order so that
    each edge case is handled by exactly one branch.

    Args:
        raw: Raw NAFDAC number string from Excel, OCR output, or user input.
             May be None, empty, contain Unicode whitespace, en-dashes, etc.

    Returns:
        Normalised string in canonical form, or None if the input is invalid
        or definitively represents "no NAFDAC number".

    Examples:
        >>> normalize_nafdac_no("A8-4114")
        'A8-4114'
        >>> normalize_nafdac_no("\\xa001-0132")    # leading non-breaking space
        '01-0132'
        >>> normalize_nafdac_no("A8-8893L")        # letter suffix — kept
        'A8-8893L'
        >>> normalize_nafdac_no("A4 - 5180")       # spaces around dash
        'A4-5180'
        >>> normalize_nafdac_no("04–2045")          # en-dash
        '04-2045'
        >>> normalize_nafdac_no("4/1/9086")         # legacy slash format
        '4-9086'
        >>> normalize_nafdac_no(None)
        None
        >>> normalize_nafdac_no("\\xa002-8608")     # NBSP prefix (real data row 9)
        '02-8608'
    """
    if raw is None:
        return None

    # Step 1 — convert to string (guards against pandas float NaN passed in)
    working = str(raw)

    # Step 2 — apply Unicode substitutions (NBSP strip, dash unification)
    working = working.translate(_UNICODE_SUBS)

    # Step 3 — strip remaining ASCII whitespace
    working = working.strip()

    # Step 4 — check against null sentinels (case-insensitive)
    if working.lower() in _NULL_SENTINELS:
        return None

    # Step 5 — attempt spaced-dash pattern  ('A4 - 5180', 'A10 - 0803')
    spaced_match = _SPACED_DASH.match(working)
    if spaced_match:
        prefix, serial = spaced_match.groups()
        return f"{prefix.upper()}-{serial.upper()}"

    # Step 6 — attempt slash pattern  ('4/1/9086')
    slash_match = _SLASH_FORMAT.match(working)
    if slash_match:
        prefix, serial = slash_match.groups()
        return f"{prefix.upper()}-{serial.upper()}"

    # Step 7 — strip all internal whitespace and uppercase
    canonical = re.sub(r"\s+", "", working).upper()

    # Step 8 — final validation against canonical pattern
    if _CANONICAL_PATTERN.match(canonical):
        return canonical

    # Could not produce a valid canonical form — return None
    return None


def is_valid_nafdac_no(nafdac_no: Optional[str]) -> bool:
    """
    Return True if the given string is already in valid canonical form.

    Call this AFTER normalize_nafdac_no(), not on raw strings.

    Args:
        nafdac_no: String to validate.  Should be the output of normalize_nafdac_no().

    Returns:
        True  — matches canonical pattern '[A-Z0-9]+-\\d+[A-Z]?'
        False — None, empty, or non-canonical.

    Examples:
        >>> is_valid_nafdac_no("A8-4114")
        True
        >>> is_valid_nafdac_no(None)
        False
        >>> is_valid_nafdac_no("A8 - 4114")   # raw, not yet normalised
        False
    """
    if not nafdac_no:
        return False
    return bool(_CANONICAL_PATTERN.match(nafdac_no))