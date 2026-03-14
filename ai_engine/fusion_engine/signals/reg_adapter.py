
"""
This file contains the Fusion Engine's Regulatory (reg Signal Adapter)

Normalises the output of regulatory_scorer.compute_verification_score()
into a standard FusionSignal that Fusion engine can consume directly.

REG engine OUTPUT CONTRACT (regulatory_scorer.py):
  {
      # Core fields - same shape as legacy regulatory_scorer
      "verified":           bool,
      "verification_score": float,   # 0.0 | 0.1 | 0.2 | 0.85 | 1.0
      "status_code":        str,     
      "severity":           str,     # "NONE" | "WARNING" | "HIGH" | "CRITICAL"
      "summary":            str,     # One-line verdict headline
      "detail":             str,     # Full explanation for N-ATLAS translation
      "expiry_check":       dict | None,
      "alignment":          dict | None,
      "matched_record":     dict | None,
      "all_records":        list,

      # ReAct agent-only fields
      "fallback_used":    bool,   # True = semantic_search used, not exact NAFDAC lookup
      "tools_called":     list,   # ["lookup_nafdac", "check_expiry", "check_alignment"]
      "reasoning_trace":  list,   # [{thought, action, action_input, observation_summary}]
  }

RETRIEVAL PATH DERIVATION (from fallback_used and status_code):
  fallback_used=False, no error  -> "nafdac_exact"     -> full A3 weight in fusion
  fallback_used=True             -> "semantic_fallback" -> reduced A3 weight in fusion
  status_code="AGENT_ERROR"      -> "agent_error"       -> A3 weight=0.0 + HARD_FAKE

RETRIEVAL CONFIDENCE DERIVATION (used in warnings and audit):
  nafdac_exact      -> 1.0  (deterministic DB lookup)
  semantic_fallback -> alignment similarity_score if available, else 0.70
  agent_error       -> 0.0

HARD FAKE OVERRIDES:
  NOT_FOUND          - NAFDAC number absent from registered product database
  SUBCATEGORY_MISMATCH - NAFDAC number used on wrong product category
  AGENT_ERROR        - ReAct agent crashed; cannot confirm authenticity

REASONING TRACE:
  Forwarded to evidence_packager for NAFDAC enforcement audit trail.
  NAFDAC officers reviewing a raid can read the exact agent reasoning.

SCALABILITY NOTES:
  - Add new status codes to VALID_STATUS_CODES and _OVERRIDE_REASONS as needed.
  - Do not add scoring logic - scoring belongs in fusion_engine.py.
  - retrieval_path is the key signal fusion_engine uses for weight selection.
"""

from datetime import datetime, timezone


# Status code registry 
VALID_STATUS_CODES = {
    "VERIFIED",
    "VERIFIED_NEAR_EXPIRY",
    "EXPIRED",
    "SUBCATEGORY_MISMATCH",
    "NOT_FOUND",
    "AGENT_ERROR",          # ReAct agent only - not in legacy regulatory_scorer
}

# Status codes that force FAKE - aligned to orchestrator CRITICAL_STATUSES
CRITICAL_STATUSES = {"NOT_FOUND", "SUBCATEGORY_MISMATCH", "AGENT_ERROR", "EXPIRED"}

# Override reason strings - forwarded to evidence and audit panel
_OVERRIDE_REASONS = {
    "NOT_FOUND": (
        "REG: NAFDAC number does not exist in the registered product database. "
        "Definitive counterfeit signal. Verdict forced to FAKE."
    ),
    "SUBCATEGORY_MISMATCH": (
        "REG: NAFDAC number is registered for a different product category. "
        "Classic counterfeit pattern - reused registration number on wrong product. "
        "Verdict forced to FAKE."
    ),
    "AGENT_ERROR": (
        "Regulatory ReAct Agent encountered an unrecoverable error during verification. "
        "Cannot confirm authenticity. System fails closed. Verdict forced to FAKE."
    ),

    "EXPIRED": (
    "REG: NAFDAC registration for this product has expired. "
    "Product may be old stock, repackaged, or counterfeit. "
    "Verdict forced to FAKE."
    ),
}

# Retrieval path labels
_PATH_EXACT    = "nafdac_exact"
_PATH_FALLBACK = "semantic_fallback"
_PATH_ERROR    = "agent_error"

# Default retrieval confidence when semantic match similarity is unavailable
_FALLBACK_CONFIDENCE_DEFAULT = 0.70


def adapt(reg_output: dict) -> dict:
    """
    Normalise Regulatory ReAct agent output into a standard FusionSignal.

    Args:
        reg_output: Raw dict from agent_scorer.compute_verification_score()

    Returns:
        FusionSignal dict with retrieval_path and retrieval_confidence
        for dynamic weight resolution in fusion_engine._resolve_weights().
    """
    verification_score = float(reg_output.get("verification_score", 0.0))
    status_code        = reg_output.get("status_code", "NOT_FOUND")
    severity           = reg_output.get("severity",    "CRITICAL")
    verified           = bool(reg_output.get("verified", False))
    summary            = reg_output.get("summary", "")
    detail             = reg_output.get("detail",  "")
    matched_record     = reg_output.get("matched_record")
    expiry_check       = reg_output.get("expiry_check") or {}
    alignment          = reg_output.get("alignment")    or {}

    #  ReAct agent fields 
    fallback_used   = bool(reg_output.get("fallback_used",   False))
    tools_called    = list(reg_output.get("tools_called",    []))
    reasoning_trace = list(reg_output.get("reasoning_trace", []))

    #  Derive retrieval path
    if status_code == "AGENT_ERROR":
        retrieval_path       = _PATH_ERROR
        retrieval_confidence = 0.0
    elif fallback_used:
        retrieval_path = _PATH_FALLBACK
        # Use alignment similarity if the agent found a semantic match
        retrieval_confidence = float(
            alignment.get("similarity_score", _FALLBACK_CONFIDENCE_DEFAULT)
            if alignment else _FALLBACK_CONFIDENCE_DEFAULT
        )
    else:
        retrieval_path       = _PATH_EXACT
        retrieval_confidence = 1.0

    #  Extract registered product fields
    nafdac_registered_product  = matched_record.get("product_name")  if matched_record else None
    nafdac_registered_category = matched_record.get("subcategory")   if matched_record else None
    expiry_date_iso            = matched_record.get("expiry_date_iso")if matched_record else None
    days_remaining             = expiry_check.get("days_remaining")
    is_near_expiry             = bool(expiry_check.get("is_near_expiry", False))
    scanned_category           = alignment.get("scanned_norm")

    #  Hard override logic
    override_flag   = False
    override_reason = None

    if status_code in CRITICAL_STATUSES:
        override_flag   = True
        override_reason = _OVERRIDE_REASONS.get(
            status_code,
            f"Regulatory critical status '{status_code}' - verdict forced to FAKE."
        )

    return {
        #  Core signal 
        "source":       "REG",
        "fusion_score": round(verification_score, 4),  # 0.0–1.0 positive direction

        #  Raw A3 values (preserved for audit) 
        "raw_verification_score": round(verification_score, 4),
        "verified":               verified,
        "status_code":            status_code,
        "severity":               severity,
        "summary":                summary,
        "detail":                 detail,

        #  Dynamic weight signals - read by fusion_engine._resolve_weights() 
        "retrieval_path":       retrieval_path,
        "retrieval_confidence": round(retrieval_confidence, 4),
        "fallback_used":        fallback_used,
        "tools_called":         tools_called,

        #  Registered product fields 
        "nafdac_registered_product":   nafdac_registered_product,
        "nafdac_registered_category":  nafdac_registered_category,
        "scanned_category":            scanned_category,
        "expiry_date_iso":             expiry_date_iso,
        "days_remaining":              days_remaining,
        "is_near_expiry":              is_near_expiry,
        "matched_record":              matched_record,

        #  Override 
        "override_flag":   override_flag,
        "override_reason": override_reason,

        #  Audit trail (forwarded to evidence_packager → NAFDAC enforcement) 
        "reasoning_trace": reasoning_trace,
        "atlas_detail":    detail,          # Pre-formatted for N-ATLAS translation

        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def validate(reg_output: dict) -> list: # Validate A3 output before adaptation.
    errors   = []
    required = [
        "verified", "verification_score", "status_code",
        "severity", "summary", "detail",
    ]

    for key in required:
        if key not in reg_output:
            errors.append(f"Missing required top-level key: '{key}'")

    score = reg_output.get("verification_score", -1)
    if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
        errors.append(
            f"'verification_score' must be float in [0.0, 1.0], got: {score!r}"
        )

    status = reg_output.get("status_code", "")
    if status not in VALID_STATUS_CODES:
        errors.append(
            f"Unknown status_code: {status!r}. "
            f"Expected one of: {sorted(VALID_STATUS_CODES)}"
        )

    return errors
