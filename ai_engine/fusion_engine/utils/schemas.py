# Pydantic models (input/output contracts)
""""
Single source of truth for every input and output data contract in A4.

WHY THIS FILE EXISTS:
  - Adapters reference these to guarantee output field consistency
  - Tests use the dataclasses to build valid mock payloads
  - FastAPI can use these for request/response validation (pydantic migration path)
  - Evidence packager uses them to type-check before writing to DB
  - Any engineer touching A4 starts here to understand data shapes

STRUCTURE:
  Section 1 : Upstream input contracts     (VISUAL, OCR, REGULATORY raw module outputs)
  Section 2 : Adapter output contracts     (normalised FusionSignals)
  Section 3 : Core engine output contracts (FusionResult, ClassificationResult)
  Section 4 : Evidence package contracts   (GPS, Fingerprint, NAFDACReport, ManufacturerRecord)
  Section 5 : Top-level ScanResult         (what D1 Backend / FastAPI returns to frontend)
  Section 6 : Validator helpers            (runtime field and type checks)

SCORE SCALE NOTE:
  All fusion_score values in this file are 0.0-1.0.
  1.0 = AUTHENTIC. 0.0 = FAKE.
  The only exception is OCR's final_text_anomaly_score which is INVERTED
  (1.0 = FAKE). The ocr_adapter handles the inversion before fusion.

SCALABILITY NOTES:
  - Add new dataclass fields here before updating any adapter or core module.
  - Deprecate fields by marking them Optional before removal.
  - VALID_STATUS_CODES and VALID_PURCHASE_CHANNELS must stay in sync with
    reg_adapter.py and evidence_packager.py respectively.
  - The to_dict() method on ScanResult is the API serialisation path.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing      import Optional



# SECTION 1 : UPSTREAM INPUT CONTRACTS
# These document what Fusion expects to receive from VISUAL, OCR, and REG.
# Adapters validate against these contracts before normalising.


@dataclass
class VisualInput:
    """
    Raw output contract from VisualPipeline.analyze() : Visual Engine.
    Source: visual_pipeline.py -> VisualPipeline.analyze()

    Score direction: confidence 1.0 = AUTHENTIC (positive). No flip in adapter.
    """
    product:           str    # Best matched product name from embedding store
    confidence:        float  # 0.0-1.0 damage-adjusted similarity (similarity × (1 - damage))
    damage_score:      float  # Scan quality: 0.1=sharp | 0.4=moderate | 0.8=blurry
    blur_value:        float  # Raw Laplacian variance : new field from DamageDetector
    verdict:           str    # "Authentic" | "Suspicious" | "Fake" (Title case exactly)

    # Field name contains a space : matches output key "Visual Similarity"
    visual_similarity: float  # Raw cosine similarity before damage adjustment

    REQUIRED_FIELDS = ["product", "confidence", "damage_score", "verdict", "Visual Similarity"]
    VALID_VERDICTS  = {"Authentic", "Suspicious", "Fake"}


@dataclass
class OCRInput:
    """
    Raw output contract from pipeline.run_pipeline() : OCR/Linguistic Engine.
    Source: pipeline.py -> run_pipeline()

    Score direction: final_text_anomaly_score 1.0 = FAKE (INVERTED vs A4).
        ocr_adapter flips this: fusion_score = 1.0 - final_text_anomaly_score.
    """
    source:                    str    # Always "OCR_Linguistic"
    final_text_anomaly_score:  float  # 0.0-1.0 anomaly score (higher = worse)
    ml_score:                  float  # 0.0-1.0 ML anomaly component
    metadata:                  dict   # nafdac_number, avg_ocr_confidence,
                                      # brand_detected, batch_number, expiry_date
    brand_anomaly:             dict   # brand_detected, similarity_score,
                                      # brand_anomaly_flag, lookalike_corrections
    structural_validation:     dict   # missing_fields, structural_score,
                                      # expiry_format_valid, batch_format_valid
    rule_score:                dict   # rule_score, components, damage_score_applied,
                                      # adjusted_ocr_confidence

    REQUIRED_FIELDS = [
        "metadata", "brand_anomaly", "structural_validation",
        "rule_score", "ml_score", "final_text_anomaly_score",
    ]


@dataclass
class REGInput:
    """
    Raw output contract from agent_scorer.compute_verification_score() : REG ReAct Agent.
    Source: agent_scorer.py -> _verdict_to_dict(AgentVerdict)

    Score direction: verification_score 1.0 = AUTHENTIC (positive). No flip in adapter.
    """
    verified:           bool           # Overall regulatory pass/fail
    verification_score: float          # 0.0 | 0.1 | 0.2 | 0.85 | 1.0
    status_code:        str            # See VALID_STATUS_CODES below
    severity:           str            # "NONE" | "WARNING" | "HIGH" | "CRITICAL"
    summary:            str            # One-line verdict headline for D3 mobile UI
    detail:             str            # Full explanation for N-ATLAS translation
    expiry_check:       Optional[dict] # Expiry layer result dict
    alignment:          Optional[dict] # Subcategory alignment result dict
    matched_record:     Optional[dict] # Best-matching NAFDAC DB record
    all_records:        list           # All records found for this NAFDAC number

    # ReAct agent-only fields : absent in legacy regulatory_scorer output
    fallback_used:    bool  # True = semantic_search used, not exact NAFDAC DB lookup
    tools_called:     list  # ["lookup_nafdac", "check_expiry", "check_alignment"]
    reasoning_trace:  list  # [{thought, action, action_input, observation_summary}]

    REQUIRED_FIELDS = [
        "verified", "verification_score", "status_code",
        "severity", "summary", "detail",
    ]
    VALID_STATUS_CODES = {
        "VERIFIED",
        "VERIFIED_NEAR_EXPIRY",
        "EXPIRED",
        "SUBCATEGORY_MISMATCH",
        "NOT_FOUND",
        "AGENT_ERROR",            # ReAct agent only
    }
    VALID_SEVERITIES = {"NONE", "WARNING", "HIGH", "CRITICAL"}



# SECTION 2 : ADAPTER OUTPUT CONTRACTS (normalised FusionSignals)
# All adapters produce a dict that conforms to FusionSignal (base) plus
# the extended fields defined in VISUALFusionSignal, OCRFusionSignal, REGFusionSignal.


@dataclass
class FusionSignal:
    """
    Base normalised signal produced by any adapter.
    fusion_score is ALWAYS 0.0-1.0 with 1.0 = AUTHENTIC (positive direction).
    All adapters normalise to this direction before returning.
    """
    source:          str            # "VISUAL" | "OCR" | "REG"
    fusion_score:    float          # 0.0-1.0 positive (1.0 = authentic)
    override_flag:   bool           # True = this signal triggers a hard override
    override_reason: Optional[str]  # Human-readable explanation for D5 audit panel
    timestamp:       str            # UTC ISO 8601 string


@dataclass
class VisualFusionSignal(FusionSignal):
    """Extended FusionSignal for Visual adapter output."""
    raw_confidence:  float  # VISUAL's damage-adjusted confidence (same as fusion_score)
    raw_similarity:  float  # Pre-damage cosine similarity : used for override check
    damage_score:    float  # Forwarded to fusion_engine for weight selection
    blur_value:      float  # Forwarded to fusion_engine for RESCAN_REQUIRED check
    product_matched: str    # Product name VISUAL identified (for evidence and D5 audit)
    visual_verdict:      str    # VISUAL's own verdict string (preserved for audit trail)


@dataclass
class OcrFusionSignal(FusionSignal):
    """Extended FusionSignal for OCR adapter output."""
    raw_anomaly_score:      float         # OCR's original anomaly score (pre-inversion)
    rule_score:             float         # Rule engine anomaly component
    ml_score:               float         # ML anomaly component
    nafdac_number:          Optional[str] # Extracted NAFDAC number (None = not found -> override)
    brand_detected:         Optional[str] # Brand name detected on label
    brand_anomaly_flag:     int           # 0 = no anomaly | 1 = anomaly detected
    brand_similarity:       float         # Rapidfuzz similarity score 0.0-100.0
    lookalike_corrections:  list          # Character substitutions found (counterfeit fingerprint)
    structural_score:       float         # 0.0-1.0 label completeness score
    missing_fields:         list          # Required label fields that are absent
    avg_ocr_confidence:     float         # Average OCR confidence across all extracted text
    damage_already_applied: float         # Informational : DO NOT re-apply in A4


@dataclass
class RegFusionSignal(FusionSignal):
    """Extended FusionSignal for RAG adapter output."""
    raw_verification_score:      float
    verified:                    bool
    status_code:                 str
    severity:                    str
    summary:                     str
    detail:                      str           # Pre-formatted for N-ATLAS translation
    retrieval_path:              str           # "nafdac_exact" | "semantic_fallback" | "agent_error"
    retrieval_confidence:        float         # 1.0 (exact) | 0.7 (fallback) | 0.0 (error)
    fallback_used:               bool          # Key dynamic weight signal for fusion_engine
    tools_called:                list
    nafdac_registered_product:   Optional[str]
    nafdac_registered_category:  Optional[str]
    scanned_category:            Optional[str]
    expiry_date_iso:             Optional[str]
    days_remaining:              Optional[int]
    is_near_expiry:              bool
    matched_record:              Optional[dict]
    reasoning_trace:             list          # Forwarded to evidence_packager for NAFDAC audit
    atlas_detail:                str           # Pre-formatted for N-ATLAS


# SECTION 3 : CORE ENGINE OUTPUT CONTRACTS


@dataclass
class FusionResult:
    """
    Output of core/fusion_engine.run_fusion().
    Consumed by decision_classifier.classify().
    """
    verdict:          str            # "AUTHENTIC" | "SUSPICIOUS" | "FAKE" | "RESCAN_REQUIRED"
    final_score:      Optional[float]# 0.0-1.0 weighted fusion score (None if RESCAN_REQUIRED)
    severity:         str            # "NONE" | "MEDIUM" | "CRITICAL"
    confidence_label: str            # "VERY HIGH" | "HIGH" | "MODERATE" | "LOW" | "VERY LOW" | "NONE"
    rescan_required:  bool           # True only when verdict="RESCAN_REQUIRED"
    weight_mode:      Optional[str]  # "BASE" | "DAMAGED" | "FALLBACK" | "REJECTED"
    weights_used:     Optional[dict] # The weight set that was applied
    retrieval_path:   Optional[str]  # REG retrieval path used in weight selection
    override_applied: bool
    applied_override: Optional[dict] # {"source", "type", "reason"}
    all_overrides:    list           # All override flags that fired
    breakdown:        dict           # Per-signal: raw_score, weight, weighted
    warnings:         list           # [{type, message}]
    atlas_detail:     str            # Pre-formatted for N-ATLAS
    atlas_summary:    str
    evidence:         dict           # Fields forwarded to evidence_packager
    timestamp:        str


@dataclass
class ClassificationResult:
    """
    Output of core/decision_classifier.classify().
    Consumed by evidence_packager.package() and the FastAPI response layer.
    """
    action:             str            # "BUY" | "CAUTION" | "DO NOT BUY" | "RESCAN"
    verdict:            str
    final_score:        Optional[float]
    severity:           str
    confidence_label:   str
    report_priority:    str            # "AUTO" | "PROMPT" | "NONE"
    instruction:        str            # Context-enriched instruction -> N-ATLAS
    simple_instruction: str            # Short voice-first instruction for Mama Bola
    atlas_instruction:  str            # instruction + warning appendages
    override_applied:   bool
    override_summary:   Optional[str]  # Formatted override explanation for D5 audit
    warnings:           list
    evidence:           dict           # Forwarded to evidence_packager
    breakdown:          dict
    scan_id:            str
    timestamp:          str



# SECTION 4 : EVIDENCE PACKAGE CONTRACTS


@dataclass
class GPSCoordinates:
    """
    GPS lock at point of scan.
    locked=True means the coordinates are valid and within range.
    locked=False means the GPS lock failed or coordinates are out of range.
    """
    lat:      Optional[float]  # Latitude  -90 to +90
    lng:      Optional[float]  # Longitude -180 to +180
    accuracy: Optional[float]  # Accuracy in metres (lower = better)
    locked:   bool             # True if lat/lng are valid


@dataclass
class CounterfeitFingerprint:
    """
    Documents exactly HOW a counterfeit was detected.
    Primary input for the Manufacturer Subscription Portal intelligence feed.
    Used by NAFDAC for pattern clustering across enforcement cases.
    """
    detection_signals: dict          # Per-signal scores at time of detection
    label_anomalies:   dict          # lookalike_chars, missing_fields, mismatch flags
    override_fired:    bool          # True if a hard override determined the verdict
    override_type:     Optional[str] # "HARD_FAKE" | "SUSPICIOUS_FLOOR" | None
    override_source:   Optional[str] # "VISUAL" | "OCR" | "REG" | None


@dataclass
class NAFDACReport:
    """
    Structured enforcement report posted to the NAFDAC Digital Intelligence API.
    Auto-generated on FAKE verdicts. User-prompted on SUSPICIOUS.
    Follows NAFDAC-DISS v1.0 submission format.
    """
    report_type:          str            # Always "COUNTERFEIT_PRODUCT_DETECTION"
    schema_version:       str            # "1.0" : bump on structural changes
    scan_id:              str
    timestamp_utc:        str
    verdict:              str
    severity:             str
    nafdac_number:        Optional[str]
    brand:                Optional[str]
    registered_product:   Optional[str]
    failure_reason:       Optional[str]  # REG status_code
    enforcement_location: dict           # lat, lng, accuracy, gps_locked, purchase_channel
    label_anomalies:      dict
    detection_signals:    dict
    override_applied:     bool
    override_summary:     Optional[str]
    warning_types:        list           # List of warning type strings
    auto_flagged:         bool


@dataclass
class ManufacturerRecord:
    """
    B2B intelligence record for the Manufacturer Subscription Portal.
    Shows brands exactly how counterfeiters are bypassing their security features
    and where counterfeit products are appearing geographically.
    """
    brand:                Optional[str]
    registered_product:   Optional[str]
    scan_id:              str
    timestamp_utc:        str
    counterfeit_location: dict  # lat, lng, purchase_channel
    bypass_method:        dict  # visual_similarity, lookalike_chars, nafdac_misuse_type,
                                # missing_label_fields, retrieval_path
    recommendation:       str   # Targeted security recommendation


# SECTION 5 : TOP-LEVEL SCAN RESULT
# The final dict returned by main.run_scan() to the orchestrator and Backend.


@dataclass
class ScanResult:
    """
    Final output of main.run_scan(). Returned to ScanOrchestrator and D1 Backend.

    status values:
      SUCCESS          : all signals valid, full pipeline ran cleanly
      PARTIAL          : one or more signals failed validation; failsafe used;
                         result is still a valid verdict
      FAILSAFE         : catastrophic exception; worst-case FAKE returned
      RESCAN_REQUIRED  : image too blurry to score; no verdict issued
    """
    status:             str            # "SUCCESS" | "PARTIAL" | "FAILSAFE" | "RESCAN_REQUIRED"
    scan_id:            str
    verdict:            str            # "AUTHENTIC" | "SUSPICIOUS" | "FAKE" | "RESCAN_REQUIRED"
    action:             str            # "BUY" | "CAUTION" | "DO NOT BUY" | "RESCAN"
    final_score:        Optional[float]# 0.0-1.0 (None if RESCAN_REQUIRED)
    severity:           str            # "NONE" | "MEDIUM" | "CRITICAL"
    confidence_label:   str
    report_priority:    str            # "AUTO" | "PROMPT" | "NONE"
    simple_instruction: str            # Voice-first for Mama Bola
    atlas_instruction:  str            # Full instruction for N-ATLAS translation
    atlas_summary:      str            # One-line summary from REG
    override_applied:   bool
    override_summary:   Optional[str]
    warnings:           list
    breakdown:          dict           # Per-signal weighted score breakdown
    weight_mode:        Optional[str]  # "BASE" | "DAMAGED" | "FALLBACK" | "REJECTED" | None
    evidence_package:   Optional[dict] # None if AUTHENTIC or RESCAN_REQUIRED
    errors:             list           # Non-fatal errors encountered during scan
    timestamp:          str            # UTC ISO 8601 scan start time

    def to_dict(self) -> dict:
        """Serialise to a plain dict for FastAPI JSON response."""
        return asdict(self)


# SECTION 6 : VALIDATOR HELPERS
# Runtime field and type checks used by adapters and tests.
# These are standalone functions, not methods on the dataclasses
# so they can be called without constructing a full dataclass instance.


def validate_visual_input(data: dict) -> list:
    """
    Validate VISUAL raw input before adaptation.
    Returns list of error strings (empty = valid).
    """
    errors   = []
    required = ["product", "confidence", "damage_score", "verdict", "Visual Similarity"]

    for f in required:
        if f not in data:
            errors.append(f"Missing required field: '{f}'")

    conf = data.get("confidence", -1)
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        errors.append(f"'confidence' must be float in [0.0, 1.0], got: {conf!r}")

    sim = data.get("Visual Similarity", -1)
    if not isinstance(sim, (int, float)) or not (0.0 <= float(sim) <= 1.0):
        errors.append(f"'Visual Similarity' must be float in [0.0, 1.0], got: {sim!r}")

    verdict = data.get("verdict", "")
    if verdict not in VisualInput.VALID_VERDICTS:
        errors.append(
            f"'verdict' must be one of {VisualInput.VALID_VERDICTS}, got: {verdict!r}"
        )

    if "blur_value" not in data:
        errors.append(
            "WARNING: 'blur_value' missing. "
            "Update damage_detector.py and visual_pipeline.py. "
            "Defaulting to 60.0 (sharp)."
        )

    return errors


def validate_ocr_input(data: dict) -> list:
    """
    Validate OCR raw input before adaptation.
    Returns list of error strings (empty = valid).
    """
    errors   = []
    required = [
        "metadata", "brand_anomaly", "structural_validation",
        "rule_score", "ml_score", "final_text_anomaly_score",
    ]

    for key in required:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")

    score = data.get("final_text_anomaly_score", -1)
    if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
        errors.append(
            f"'final_text_anomaly_score' must be float in [0.0, 1.0], got: {score!r}"
        )

    return errors


def validate_reg_input(data: dict) -> list:
    """
    Validate REG raw input before adaptation.
    Returns list of error strings (empty = valid).
    """
    errors   = []
    required = [
        "verified", "verification_score", "status_code",
        "severity", "summary", "detail",
    ]

    for key in required:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")

    score = data.get("verification_score", -1)
    if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
        errors.append(
            f"'verification_score' must be float in [0.0, 1.0], got: {score!r}"
        )

    status = data.get("status_code", "")
    if status not in REGInput.VALID_STATUS_CODES:
        errors.append(
            f"Unknown status_code: {status!r}. "
            f"Expected one of: {sorted(REGInput.VALID_STATUS_CODES)}"
        )

    return errors


def validate_gps(data: dict) -> list:
    """
    Validate GPS coordinates before evidence packaging.
    Returns list of error strings (empty = valid).
    """
    if not data or not isinstance(data, dict):
        return ["GPS coordinates must be a non-empty dict with lat, lng, accuracy."]

    errors = []
    lat    = data.get("lat")
    lng    = data.get("lng")

    if lat is None or not isinstance(lat, (int, float)) or not (-90 <= float(lat) <= 90):
        errors.append(f"'lat' must be float in [-90, 90], got: {lat!r}")

    if lng is None or not isinstance(lng, (int, float)) or not (-180 <= float(lng) <= 180):
        errors.append(f"'lng' must be float in [-180, 180], got: {lng!r}")

    return errors


def validate_purchase_channel(channel: str) -> list:
    """
    Validate purchase channel string.
    Returns list of error strings (empty = valid).
    """
    from core.evidence_packager import VALID_PURCHASE_CHANNELS
    if channel not in VALID_PURCHASE_CHANNELS:
        return [
            f"Invalid purchase_channel: {channel!r}. "
            f"Must be one of: {sorted(VALID_PURCHASE_CHANNELS)}"
        ]
    return []
