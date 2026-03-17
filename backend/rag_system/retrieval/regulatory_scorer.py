"""
retrieval/regulatory_scorer.py
--------------------------------
Produces the final product-verification verdict consumed by the A4 Fusion Engine.

FOUR-LAYER CHECK SEQUENCE
  Each check runs only if the previous one passed.  The first failure
  determines the final verdict.

  Layer 1  NAFDAC Number Existence
             Is this number in the database at all?
             FAIL → score 0.0, status NOT_FOUND

  Layer 2  Expiry Date
             Has the product's registration expired?
             FAIL → score 0.1, status EXPIRED

  Layer 3  Subcategory Alignment
             Does the scanned product type match the registration category?
             FAIL → score 0.2, status SUBCATEGORY_MISMATCH  ← strongest fake signal

  Layer 4  All Checks Passed
             PASS → score 1.0, status VERIFIED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE SCALE  (fed to A4 Fusion Engine as 'verification_score')
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1.0  — Fully verified: number found, not expired, correct category
  0.2  — Subcategory mismatch: valid number but wrong product type  ← CRITICAL
  0.1  — Expired registration: product no longer authorised for sale
  0.0  — Not found: NAFDAC number does not exist in the database

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL DATA FACTS THAT SHAPE THIS LOGIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • expiry_date in nafdac_database.xlsx ranges from 2026-03-28 to 2031-01-26.
    All dates are FUTURE (relative to today 2026-03-03).  Unlike the Greenbook
    dataset, expiry dates here are real forward-looking deadlines that should
    be checked.  A product whose expiry date has passed is no longer legally
    registered for sale.

  • The dataset has no 'status' column — only the expiry date determines
    whether a registration is currently active.

  • One product (LIPTON YELLOW LABEL TEA, expiry 2026-03-28) expires soon —
    demonstrates the near-expiry warning path.

  • No null NAFDAC numbers in this dataset (all 15 rows have valid numbers).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SEPARATION OF CONCERNS
  This module combines retrieval results into a verdict.
  It does NOT touch ChromaDB, embeddings, or HTTP routing.
"""

from datetime import date, timedelta
from retrieval.subcategory_alignment import check_subcategory_alignment
from config.settings import settings


# ── Score constants ────────────────────────────────────────────────────────────
SCORE_VERIFIED            = 1.0   # All checks passed
SCORE_SUBCATEGORY_MISMATCH = 0.2  # Right number, wrong product type
SCORE_EXPIRED             = 0.1   # Registration has lapsed
SCORE_EXPIRING_SOON       = 0.85  # Valid but expiry within 60 days
SCORE_NOT_FOUND           = 0.0   # Number not in database

# Near-expiry warning window: flag products expiring within 60 days
_NEAR_EXPIRY_DAYS = 60


# ── Private helpers ────────────────────────────────────────────────────────────

def _check_expiry(expiry_date_iso: str) -> dict:
    """
    Evaluate whether a product's registration has expired or is near expiry.

    KEY DIFFERENCE FROM GREENBOOK DATASET:
      In nafdac_database.xlsx, expiry dates are genuine future deadlines
      (2026–2031).  We treat them as hard cutoffs: past the expiry date,
      the product is no longer legally authorised for sale in Nigeria.

    Args:
        expiry_date_iso: ISO date string 'YYYY-MM-DD', or '' if unavailable.

    Returns:
        Dict with:
          is_valid        (bool)       : True if not yet expired
          is_near_expiry  (bool)       : True if within 60 days of expiry
          expiry_date     (str | None) : The parsed date or None
          days_remaining  (int | None) : Days until expiry, or None
          severity        (str)        : 'NONE', 'WARNING', or 'EXPIRED'
          message         (str)        : Human-readable expiry status

    Examples:
        _check_expiry('2029-07-30') → {is_valid: True, severity: 'NONE', ...}
        _check_expiry('2026-03-28') → {is_valid: True, severity: 'WARNING',
                                       days_remaining: 25, ...}
        _check_expiry('2025-01-01') → {is_valid: False, severity: 'EXPIRED', ...}
    """
    if not expiry_date_iso:
        # No expiry date in the record — cannot determine; do not fail
        return {
            "is_valid"      : True,
            "is_near_expiry": False,
            "expiry_date"   : None,
            "days_remaining": None,
            "severity"      : "NONE",
            "message"       : "No expiry date on record.",
        }

    try:
        expiry  = date.fromisoformat(expiry_date_iso)
        today   = date.fromisoformat(settings.REFERENCE_DATE)
        delta   = (expiry - today).days

        if delta < 0:
            # Already expired
            return {
                "is_valid"      : False,
                "is_near_expiry": False,
                "expiry_date"   : expiry_date_iso,
                "days_remaining": delta,           # Negative = days since expiry
                "severity"      : "EXPIRED",
                "message"       : (
                    f"Registration expired on {expiry_date_iso} "
                    f"({abs(delta)} day(s) ago). "
                    f"This product is no longer authorised for sale."
                ),
            }
        elif delta <= _NEAR_EXPIRY_DAYS:
            # Valid but expiring very soon — flag as a warning
            return {
                "is_valid"      : True,
                "is_near_expiry": True,
                "expiry_date"   : expiry_date_iso,
                "days_remaining": delta,
                "severity"      : "WARNING",
                "message"       : (
                    f"Registration expires on {expiry_date_iso} "
                    f"(in {delta} day(s)). "
                    f"Product is currently valid but renewal is due soon."
                ),
            }
        else:
            # Fully valid, well within expiry
            return {
                "is_valid"      : True,
                "is_near_expiry": False,
                "expiry_date"   : expiry_date_iso,
                "days_remaining": delta,
                "severity"      : "NONE",
                "message"       : (
                    f"Registration valid until {expiry_date_iso} "
                    f"({delta} day(s) remaining)."
                ),
            }
    except (ValueError, TypeError) as exc:
        # Cannot parse the date — don't penalise the product
        return {
            "is_valid"      : True,
            "is_near_expiry": False,
            "expiry_date"   : expiry_date_iso,
            "days_remaining": None,
            "severity"      : "NONE",
            "message"       : f"Could not parse expiry date '{expiry_date_iso}': {exc}",
        }


def _pick_best_record(records: list[dict], scanned_subcategory: str) -> dict:
    """
    Choose the most relevant record when multiple share the same NAFDAC number.

    Strategy: prefer a record whose subcategory aligns with scanned_subcategory.
    If none match, fall back to the first record (earliest registration).

    Args:
        records:              List of metadata dicts from retrieve_by_nafdac_no().
        scanned_subcategory:  Subcategory text from the A1/A2 pipeline.

    Returns:
        Single metadata dict — the best-matching record.
    """
    if len(records) == 1:
        return records[0]

    from retrieval.subcategory_alignment import normalize_subcategory
    scanned_norm = normalize_subcategory(scanned_subcategory)

    for record in records:
        if normalize_subcategory(record.get("subcategory", "")) == scanned_norm:
            return record

    # No category match — default to first record
    return records[0]


# ── Public interface ───────────────────────────────────────────────────────────

def compute_verification_score(
    nafdac_no:           str,
    scanned_subcategory: str,
    db_records:          list[dict],
) -> dict:
    """
    Compute the four-layer product verification verdict.

    Called by the API route after ProductRetriever.retrieve_by_nafdac_no().
    Also consumed directly by the A4 Fusion Engine for weighted signal fusion.

    Args:
        nafdac_no:           Raw NAFDAC number from OCR (used in display messages).
        scanned_subcategory: Product subcategory from A1/A2 classifier pipeline.
                             Raw text is fine — normalisation applied internally.
        db_records:          List of database metadata dicts from retrieval.
                             Empty list means the NAFDAC number was not found.

    Returns:
        Dict with keys:
          verified           (bool)        — Overall pass/fail
          verification_score (float)       — 0.0–1.0 for A4 Fusion weighting
          status_code        (str)         — Machine-readable verdict
          severity           (str)         — 'NONE', 'WARNING', 'HIGH', 'CRITICAL'
          summary            (str)         — One-line UI headline
          detail             (str)         — Full explanation → N-ATLAS translation
          expiry_check       (dict | None) — Expiry layer result
          alignment          (dict | None) — Subcategory alignment result
          matched_record     (dict | None) — Best-matching DB record
          all_records        (list)        — All records with this NAFDAC number

    Score interpretation for A4 Fusion:
      1.0  → Authentic signal — weight regulatory check heavily
      0.2  → Strong fake signal — subcategory mismatch
      0.1  → Expired registration — suspicious but not necessarily fake
      0.0  → No record exists — strong fake signal

    Demo scenarios with this 15-product dataset:
      NAFDAC 'A8-4114' + subcategory 'cereal'     → score 1.0, VERIFIED
      NAFDAC 'A8-4114' + subcategory 'cosmetics'  → score 0.2, SUBCATEGORY_MISMATCH
      NAFDAC 'FAKE-999' + any subcategory          → score 0.0, NOT_FOUND
      NAFDAC '01-0132' + subcategory 'tea'         → score 0.85–1.0 (near expiry warning)
    """

    # ── Layer 1: NAFDAC number existence ─────────────────────────────────────
    if not db_records:
        return {
            "verified"           : False,
            "verification_score" : SCORE_NOT_FOUND,
            "status_code"        : "NOT_FOUND",
            "severity"           : "CRITICAL",
            "summary"            : (
                f"NAFDAC number '{nafdac_no}' not found in the database."
            ),
            "detail"             : (
                f"The NAFDAC number '{nafdac_no}' does not exist in the registered "
                f"product database. This product has no valid NAFDAC registration. "
                f"Do not purchase this product."
            ),
            "expiry_check"       : None,
            "alignment"          : None,
            "matched_record"     : None,
            "all_records"        : [],
        }

    # Select best matching record (handles duplicates gracefully)
    best = _pick_best_record(db_records, scanned_subcategory)
    product_name  = best.get("product_name",  "Unknown Product")
    applicant     = best.get("applicant_name", "Unknown Applicant")
    expiry_iso    = best.get("expiry_date_iso", "")

    # ── Layer 2: Expiry date check ────────────────────────────────────────────
    expiry_check = _check_expiry(expiry_iso)

    if not expiry_check["is_valid"]:
        return {
            "verified"           : False,
            "verification_score" : SCORE_EXPIRED,
            "status_code"        : "EXPIRED",
            "severity"           : "HIGH",
            "summary"            : (
                f"Registration for '{product_name}' has expired."
            ),
            "detail"             : (
                f"NAFDAC number '{nafdac_no}' belongs to '{product_name}' "
                f"by '{applicant}'. {expiry_check['message']} "
                f"Do not purchase this product."
            ),
            "expiry_check"       : expiry_check,
            "alignment"          : None,
            "matched_record"     : best,
            "all_records"        : db_records,
        }

    # ── Layer 3: Subcategory alignment check ──────────────────────────────────
    registered_subcategory = best.get("subcategory", "Unknown")
    alignment = check_subcategory_alignment(scanned_subcategory, registered_subcategory)

    if not alignment["is_match"]:
        return {
            "verified"           : False,
            "verification_score" : SCORE_SUBCATEGORY_MISMATCH,
            "status_code"        : "SUBCATEGORY_MISMATCH",
            "severity"           : "CRITICAL",
            "summary"            : (
                f"NAFDAC '{nafdac_no}' registered for '{registered_subcategory}', "
                f"not '{alignment['scanned_norm']}'."
            ),
            "detail"             : (
                f"CRITICAL: NAFDAC number '{nafdac_no}' belongs to "
                f"'{product_name}' ({registered_subcategory}) by '{applicant}'. "
                f"However, the scanned product appears to be "
                f"'{alignment['scanned_norm']}'. "
                f"This NAFDAC number has been misused. "
                f"This is a strong sign of a counterfeit product. Do not buy."
            ),
            "expiry_check"       : expiry_check,
            "alignment"          : alignment,
            "matched_record"     : best,
            "all_records"        : db_records,
        }

    # ── Layer 4: All checks passed ────────────────────────────────────────────
    # Adjust score slightly if the product is near expiry
    near_expiry_penalty = 0.15 if expiry_check["is_near_expiry"] else 0.0
    final_score = round(SCORE_VERIFIED - near_expiry_penalty, 2)

    status_code = "VERIFIED_NEAR_EXPIRY" if expiry_check["is_near_expiry"] else "VERIFIED"
    severity    = "WARNING"              if expiry_check["is_near_expiry"] else "NONE"

    expiry_note = (
        f"  Note: {expiry_check['message']}" if expiry_check["is_near_expiry"] else ""
    )

    return {
        "verified"           : True,
        "verification_score" : final_score,
        "status_code"        : status_code,
        "severity"           : severity,
        "summary"            : (
            f"'{product_name}' is a valid, registered NAFDAC product."
        ),
        "detail"             : (
            f"Verification passed. '{product_name}' by '{applicant}' "
            f"is a registered {registered_subcategory} product "
            f"(NAFDAC No: {nafdac_no}).{expiry_note}"
        ),
        "expiry_check"       : expiry_check,
        "alignment"          : alignment,
        "matched_record"     : best,
        "all_records"        : db_records,
    }