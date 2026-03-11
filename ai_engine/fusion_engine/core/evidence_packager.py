# Bundles result + GPS + metadata for Tier IV
"""
This file contains Fusion Engine's Evidence Packager
Builds tamper-proof evidence packages from classification results.
Triggered automatically for FAKE verdicts (AUTO) and optionally
for SUSPICIOUS verdicts when the user opts to report (PROMPT).

POSITION IN PIPELINE:
  decision_classifier.classify()  ->  package()  ->  Intelligence DB / NAFDAC API

RESPONSIBILITIES:
  1. Bundle all scan signals into a tamper-proof evidence dict
  2. Embed GPS coordinates (locked at point of scan)
  3. Attach purchase channel metadata
  4. Compute a SHA-256 integrity hash over core fields
  5. Generate a structured NAFDAC enforcement report payload
  6. Generate a manufacturer intelligence record (B2B portal feed)
  7. Build a counterfeit fingerprint (how the fake was caught)

EVIDENCE FILE CONSUMERS:
  - Intelligence Database          - written as-is for heatmap queries
  - NAFDAC Enforcement API         - nafdac_report sub-dict posted directly
  - Manufacturer Subscription Portal - manufacturer_record sub-dict streamed
  - Regulatory Heatmap Dashboard   - gps + verdict for geographic clustering

TAMPER-PROOF DESIGN:
  SHA-256 hash is computed over a stable set of core fields before any
  optional fields are added. Any post-creation modification invalidates
  the hash - making evidence files legally robust for raid prosecution.

  core_fields (hashed):
    scan_id, timestamp_utc, verdict, final_score, severity, action,
    nafdac_number, brand_detected, product_visual_match,
    registered_product, reg_status_code, purchase_channel,
    gps_lat, gps_lng, gps_accuracy_meters

PURCHASE CHANNEL OPTIONS (from SabiLens proposal Tier IV):
  "traffic_vendor"  - roadside / go-slow seller
  "roadside_store"  - small roadside kiosk
  "open_market"     - Oshodi, Onitsha, Alaba-style markets
  "supermarket"     - formal retail (Shoprite, Spar, etc.)
  "supplier"        - wholesale distributor
  "online"          - e-commerce / social media vendor
  "unknown"         - user did not specify

SCALABILITY NOTES:
  - Add new purchase channels to VALID_PURCHASE_CHANNELS as Tier IV expands.
  - Add new enforcement actions to _ENFORCEMENT_ACTION as NAFDAC tiers grow.
  - Add new fingerprint detection signals in _build_fingerprint() as Visual/OCR/REG
    expose more component-level scores.
  - Never change which fields are included in core_fields after deployment -
    this would invalidate all previously issued evidence hashes.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone


# Purchase channel registry 
# Extend this set as new purchase channels are identified in the field.
VALID_PURCHASE_CHANNELS = {
    "traffic_vendor",   # Roadside / go-slow seller — highest counterfeit risk
    "roadside_store",   # Small roadside kiosk
    "open_market",      # Oshodi, Onitsha, Alaba-style markets
    "supermarket",      # Formal retail (Shoprite, Spar, etc.)
    "supplier",         # Wholesale distributor
    "online",           # E-commerce / social media vendor
    "unknown",          # User did not specify
}


# Severity -> enforcement action map 
# Determines the enforcement urgency level sent to the NAFDAC enforcement API.
_ENFORCEMENT_ACTION = {
    "CRITICAL": "IMMEDIATE_RAID_CANDIDATE",
    "MEDIUM":   "MONITOR_AND_LOG",
    "NONE":     "NO_ACTION",
}


def package(
    classification:   dict,
    gps_coordinates:  dict,
    purchase_channel: str  = "unknown",
    receipt_image:    str  = None,
    storefront_image: str  = None,
) -> dict:
    """
    Build a complete, tamper-proof evidence package from a classification result.

    Args:
        classification:   Output of core/decision_classifier.classify()
        gps_coordinates:  Dict with keys: lat (float), lng (float), accuracy (float)
                          Example: {"lat": 6.5244, "lng": 3.3792, "accuracy": 10.0}
        purchase_channel: Where the product was purchased. One of VALID_PURCHASE_CHANNELS.
        receipt_image:    Optional file path or base64 string of receipt photo.
        storefront_image: Optional file path or base64 string of storefront photo.

    Returns:
        EvidencePackage dict - fully structured, hash-verified, ready for:
          - Intelligence Database write
          - NAFDAC enforcement API POST
          - Manufacturer portal feed
          - Heatmap dashboard data point
    """

    # Validate inputs
    if purchase_channel not in VALID_PURCHASE_CHANNELS:
        purchase_channel = "unknown"

    gps = _validate_gps(gps_coordinates)

    # Extract fields from classification 
    verdict          = classification.get("verdict",          "FAKE")
    final_score      = classification.get("final_score",      0.0)
    severity         = classification.get("severity",         "CRITICAL")
    action           = classification.get("action",           "DO NOT BUY")
    scan_id          = classification.get("scan_id")          or _generate_scan_id()
    override_applied = classification.get("override_applied", False)
    override_summary = classification.get("override_summary")
    warnings         = classification.get("warnings",         [])
    breakdown        = classification.get("breakdown",        {})
    evidence         = classification.get("evidence",         {})

    timestamp_utc = datetime.now(timezone.utc).isoformat()

    # Build core evidence fields (these are hashed) 

    core_fields = {
        "scan_id":             scan_id,
        "timestamp_utc":       timestamp_utc,
        "verdict":             verdict,
        "final_score":         final_score,
        "severity":            severity,
        "action":              action,
        "nafdac_number":       evidence.get("nafdac_number"),
        "brand_detected":      evidence.get("brand_detected"),
        "product_visual_match":evidence.get("product_matched_visual"),
        "registered_product":  evidence.get("nafdac_registered_product"),
        "reg_status_code":      evidence.get("reg_status_code"),
        "purchase_channel":    purchase_channel,
        "gps_lat":             gps.get("lat"),
        "gps_lng":             gps.get("lng"),
        "gps_accuracy_meters": gps.get("accuracy"),
    }

    # Compute integrity hash 
    integrity_hash = _compute_hash(core_fields)

    # Build counterfeit fingerprint
    fingerprint         = _build_fingerprint(evidence, breakdown, classification)

    # Build NAFDAC enforcement payload
    nafdac_report       = _build_nafdac_report(
        core             = core_fields,
        fingerprint      = fingerprint,
        gps              = gps,
        purchase_channel = purchase_channel,
        override_applied = override_applied,
        override_summary = override_summary,
        warnings         = warnings,
    )

    # Build manufacturer intelligence record
    manufacturer_record = _build_manufacturer_record(
        core             = core_fields,
        fingerprint      = fingerprint,
        breakdown        = breakdown,
        gps              = gps,
        purchase_channel = purchase_channel,
    )

 
    # Assemble full evidence package 
    return {
        # Identity
        "scan_id":          scan_id,
        "timestamp_utc":    timestamp_utc,
        "integrity_hash":   integrity_hash,

        # Verdict summary
        "verdict":          verdict,
        "final_score":      final_score,
        "severity":         severity,
        "action":           action,
        "enforcement_action": _ENFORCEMENT_ACTION.get(severity, "NO_ACTION"),

        # Location
        "gps":              gps,
        "purchase_channel": purchase_channel,

        # Product identity
        "nafdac_number":    evidence.get("nafdac_number"),
        "brand_detected":   evidence.get("brand_detected"),
        "registered_product": evidence.get("nafdac_registered_product"),
        "reg_status_code":   evidence.get("reg_status_code"),
        "reg_severity":      evidence.get("reg_severity"),

        # Counterfeit fingerprint
        "fingerprint":      fingerprint,

        # Override tracking
        "override_applied": override_applied,
        "override_summary": override_summary,

        # Warnings
        "warnings":         warnings,

        # Secondary evidence
        "receipt_image":    receipt_image,
        "storefront_image": storefront_image,

        # Signal breakdown
        "score_breakdown":  breakdown,

        # Downstream payloads
        "nafdac_report":            nafdac_report,
        "manufacturer_record":      manufacturer_record,
    }


# Private builders 

def _build_fingerprint(evidence: dict, breakdown: dict, classification: dict) -> dict:
    """
    Build the counterfeit fingerprint — documents exactly HOW this fake was detected.

    Used by:
      - Manufacturer portal: shows brands how their security features are bypassed
      - NAFDAC enforcement: provides pattern context for raid prioritisation
      - Intelligence DB: enables pattern clustering across multiple scan events
    
    Args:
        evidence:       Evidence dict from FusionResult.
        breakdown:      Per-signal score breakdown from FusionResult.
        classification: Full ClassificationResult dict.

    """
    visual = breakdown.get("visual", {})
    ocr = breakdown.get("ocr", {})
    reg = breakdown.get("reg", {})

    # ocr_anomaly_score: re-derive from ocr raw_score (which is already 0.0-1.0 authentic)
    ocr_raw = ocr.get("raw_score", 1.0)
    ocr_anomaly = round(1.0 - ocr_raw, 4)

    applied_override = classification.get("applied_override") or {}

    return {
        "detection_signals": {
            "visual_confidence":    visual.get("raw_score"),
            "visual_damage_score":  visual.get("damage_score"),
            "visual_weight_mode":   visual.get("weight_mode"),
            "ocr_anomaly_score":    ocr_anomaly,
            "structural_score":     ocr.get("structural_score"),
            "brand_anomaly_flag":   evidence.get("brand_anomaly_flag"),
            "regulatory_score":     reg.get("raw_score"),
            "regulatory_status":    reg.get("status_code"),
            "retrieval_path":       reg.get("retrieval_path"),
            "fallback_used":        reg.get("fallback_used"),
        },
        "label_anomalies": {
            "lookalike_chars_detected": bool(evidence.get("lookalike_corrections")),
            "lookalike_corrections":    evidence.get("lookalike_corrections", []),
            "missing_fields":           evidence.get("missing_fields",        []),
            "nafdac_category_mismatch": evidence.get("reg_status_code") == "SUBCATEGORY_MISMATCH",
            "nafdac_not_found":         evidence.get("reg_status_code") == "NOT_FOUND",
            "registration_expired":     evidence.get("reg_status_code") == "EXPIRED",
            "nafdac_agent_error":       evidence.get("reg_status_code") == "AGENT_ERROR",
        },
        "override_fired": classification.get("override_applied", False),
        "override_type":  applied_override.get("type"),
        "override_source":applied_override.get("source"),
    }

def _build_nafdac_report(
    core: dict, fingerprint: dict, gps: dict,
    purchase_channel: str, override_applied: bool,
    override_summary: str, warnings: list
) -> dict:
    """Structured NAFDAC enforcement report payload.

    This dict is posted directly to the NAFDAC enforcement API on FAKE verdicts.
    Format follows the NAFDAC Digital Intelligence Submission Standard (NAFDAC-DISS).

    Args:
        core:             Core evidence fields (already hashed).
        fingerprint:      CounterfeitFingerprint dict.
        gps:              Validated GPS dict.
        purchase_channel: Sanitised purchase channel string.
        override_applied: Whether a hard override fired.
        override_summary: Human-readable override description.
        warnings:         List of warning dicts from FusionResult.

    Returns:
        Structured NAFDAC report dict.
    
    """
    return {
        "report_type":       "COUNTERFEIT_PRODUCT_DETECTION",
        "schema_version":    "1.0",                              # bump when structure changes
        "scan_id":           core["scan_id"],
        "timestamp_utc":     core["timestamp_utc"],
        "verdict":           core["verdict"],
        "severity":          core["severity"],
        "nafdac_number":     core["nafdac_number"],
        "brand":             core["brand_detected"],
        "registered_product":core["registered_product"],
        "failure_reason":    core["reg_status_code"],
        "enforcement_location": {
            "latitude":         gps.get("lat"),
            "longitude":        gps.get("lng"),
            "gps_accuracy_m":   gps.get("accuracy"),
            "gps_locked":       gps.get("locked", False),
            "purchase_channel": purchase_channel,
        },
        "label_anomalies":   fingerprint["label_anomalies"],
        "detection_signals": fingerprint["detection_signals"],
        "override_applied":  override_applied,
        "override_summary":  override_summary,
        "warning_types":     [w.get("type") for w in warnings if w.get("type")],
        "auto_flagged":      True,
    }



def _build_manufacturer_record(
    core:             dict,
    fingerprint:      dict,
    breakdown:        dict,
    gps:              dict,
    purchase_channel: str,
) -> dict:
    """
    Build the manufacturer B2B intelligence record.

    This record is streamed to the Manufacturer Subscription Portal so brands
    can see exactly how their security features are being bypassed and where
    counterfeit versions of their products are appearing in the market.

    Args:
        core:             Core evidence fields.
        fingerprint:      CounterfeitFingerprint dict.
        breakdown:        Per-signal score breakdown.
        gps:              Validated GPS dict.
        purchase_channel: Sanitised purchase channel string.

    Returns:
        ManufacturerRecord dict.
    """
    visual_score = breakdown.get("visual", {}).get("raw_score")

    return {
        "brand":              core["brand_detected"],
        "registered_product": core["registered_product"],
        "scan_id":            core["scan_id"],
        "timestamp_utc":      core["timestamp_utc"],
        "counterfeit_location": {
            "lat":              gps.get("lat"),
            "lng":              gps.get("lng"),
            "purchase_channel": purchase_channel,
        },
        "bypass_method": {
            "visual_similarity":    visual_score,
            "lookalike_chars_used": fingerprint["label_anomalies"]["lookalike_corrections"],
            "nafdac_misuse_type":   core["reg_status_code"],
            "missing_label_fields": fingerprint["label_anomalies"]["missing_fields"],
            "retrieval_path":       fingerprint["detection_signals"].get("retrieval_path"),
        },
        "recommendation": _manufacturer_recommendation(fingerprint),
    }


def _manufacturer_recommendation(fingerprint: dict) -> str:
    """
    Generate a targeted security recommendation for the manufacturer.

    Evaluates the fingerprint in priority order — the most severe bypass
    pattern is reported first. Multiple patterns are not combined to
    keep the recommendation actionable rather than overwhelming.

    Args:
        fingerprint: CounterfeitFingerprint dict.

    Returns:
        Single recommendation string.
    """
    anomalies = fingerprint["label_anomalies"]
    signals   = fingerprint["detection_signals"]

    if anomalies["nafdac_category_mismatch"]:
        return (
            "Counterfeiters are reusing your NAFDAC number on a different product category. "
            "Consider applying for category-locked holographic seals and reporting this "
            "pattern to NAFDAC for cross-category registration abuse tracking."
        )
    if anomalies["lookalike_chars_detected"]:
        return (
            "Lookalike character substitutions were detected on the label "
            f"({anomalies['lookalike_corrections']}). "
            "Strengthen font security features and apply microprint on all "
            "critical regulatory fields to resist character-substitution attacks."
        )
    if anomalies["nafdac_not_found"]:
        return (
            "The counterfeit product carries a completely fabricated NAFDAC number. "
            "A QR code linking directly to your product verification page would "
            "eliminate this attack vector for consumers with internet access."
        )
    if anomalies["registration_expired"]:
        return (
            "The NAFDAC registration associated with this product has expired. "
            "Ensure all active products maintain current registrations. "
            "Expired registrations create exploitable verification gaps."
        )
    visual_score = signals.get("visual_confidence")
    if visual_score is not None and visual_score < 0.50:
        return (
            f"Visual similarity to authentic product is low (score={visual_score:.2f}). "
            "The counterfeit packaging is visually detectable. Consider updating "
            "packaging design with security inks, serialised holograms, or "
            "machine-readable tamper seals."
        )
    return (
        "No dominant bypass pattern was detected. "
        "Continue monitoring scan data for emerging counterfeit techniques in your category."
    )


def _validate_gps(gps: dict) -> dict:
    """
    Validate and sanitise GPS input.

    Invalid or missing coordinates are returned as None with locked=False.
    This prevents bad GPS data from silently corrupting enforcement records
    while still allowing the scan to proceed.

    Args:
        gps: Raw GPS dict from the orchestrator or mobile client.

    Returns:
        Sanitised GPS dict with a 'locked' boolean field.
    """
    if not gps or not isinstance(gps, dict):
        return {"lat": None, "lng": None, "accuracy": None, "locked": False}

    lat      = gps.get("lat")
    lng      = gps.get("lng")
    accuracy = gps.get("accuracy")

    valid = (
        lat is not None and lng is not None and
        isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and
        -90  <= float(lat) <= 90  and
        -180 <= float(lng) <= 180
    )
    
    return {
        "lat":      float(lat) if valid and lat is not None else None,
        "lng":      float(lng) if valid and lng is not None else None,
        "accuracy": float(accuracy) if accuracy is not None else None,
        "locked":   valid,
    }


def _compute_hash(core_fields: dict) -> str:
    """
    Compute a SHA-256 integrity hash over the core evidence fields.

    The hash is a legal tamper-detection seal.
    JSON is serialised with sort_keys=True and a str() default
    so the hash is deterministic regardless of field insertion order.

    Args:
        core_fields: Dict of fields to hash (see module docstring).

    Returns:
        64-character lowercase hex string (SHA-256 digest).
    """
    serialised = json.dumps(core_fields, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()


def _generate_scan_id() -> str:
    """
    Fallback scan_id generator for cases where the classifier did not produce one.
    Returns a 12-character uppercase hex string derived from a UUID4.
    """
    return uuid.uuid4().hex[:12].upper()
