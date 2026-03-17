"""
Shared data classes for the SabiLens scan pipeline.
All agent runners read from this file.

RESPONSIBILITIES OF THIS FILE:
  - Define AgentSignal   - the standard envelope every agent returns
  - Define PipelineResult - the final object returned to D1 Backend
  - Define PIPELINE_ORDER - the call sequence
  - Define MOCK_CONFIDENCE - placeholder for unmocked visual/ocr signals

WHAT IS NOT HERE (and why):
  - SIGNAL_WEIGHTS      -> lives in fusion_engine/config/weights.py
                          fusion owns all weight logic. Orchestrator does not score.
  - THRESHOLD_AUTHENTIC -> lives in fusion_engine/config/thresholds.py
  - THRESHOLD_SUSPICIOUS-> same
  - CRITICAL_STATUSES   -> lives in fusion_engine/signals/rag_adapter.py
  - Any scoring logic   -> fusion's job exclusively

  The orchestrator collects signals and hands them to fusion.
  fusion scores, weighs, overrides, and produces the verdict.
  These two responsibilities must never be mixed.
"""

from dataclasses import dataclass, field


@dataclass
class AgentSignal:
    """
    Standard output envelope produced by one agent after processing a scan request.
    Every agent runner (_run_ocr, _run_vision, _run_regulatory) returns one of these.
    fusion receives all three and produces the fusion AgentSignal.
    """
    agent_id:   str    # "vision" | "ocr" | "regulatory" | "fusion"
    available:  bool   # False if the module is offline or not yet integrated
    confidence: float  # normalised score 0.0–1.0 from the agent
    payload:    dict   # full result dict - shape depends on agent_id
    mocked:     bool = False  # True when a placeholder was used instead of a real run


@dataclass
class PipelineResult:
    """
    Complete output of one orchestrated scan.
    Returned by ScanOrchestrator.scan() to D1 Backend.

    All verdict fields (final_verdict, final_score, final_severity) come
    directly from fusion's ScanResult - the orchestrator does not compute them.
    """
    vision_signal:     AgentSignal    # visual classification signal
    ocr_signal:        AgentSignal    # OCR text extraction signal
    regulatory_signal: AgentSignal    # reg NAFDAC verification signal
    fusion_signal:     AgentSignal    # fusion fused verdict signal

    # Fields populated from fusion's ScanResult 
    final_verdict:     str   = ""     # "AUTHENTIC" | "SUSPICIOUS" | "FAKE"
    final_score:       float = 0.0    # fused confidence score 0.0–1.0
    final_severity:    str   = ""     # "NONE" | "MEDIUM" | "CRITICAL"
    summary:           str   = ""     # one-line verdict for D3 mobile display
    detail:            str   = ""     # full sentence for D6 voice / N-ATLAS
    action:            str   = ""     # "BUY" | "CAUTION" | "DO NOT BUY"
    simple_instruction:str   = ""     # voice-first instruction for Mama Bola
    atlas_instruction: str   = ""     # full N-ATLAS string
    report_priority:   str   = ""     # "AUTO" | "PROMPT" | "NONE"
    override_applied:  bool  = False  # True if a hard override fired
    override_summary:  str   = ""     # human-readable override explanation
    warnings:          list  = field(default_factory=list)   # near-expiry, lookalike chars etc.
    breakdown:         dict  = field(default_factory=dict)   # per-signal weighted scores
    evidence_package:  dict  = field(default_factory=dict)   # GPS, fingerprint, NAFDAC report
    signals_used:      list  = field(default_factory=list)   # agent IDs with non-zero weight
    scan_id:           str   = ""     # UUID from fusion
    rescan_required:   bool  = False  # True if blur was too extreme for a verdict
    status:            str   = ""     # "SUCCESS" | "PARTIAL" | "FAILSAFE" | "RESCAN_REQUIRED"


#  Pipeline metadata ─

# Call order for every scan request
PIPELINE_ORDER = ["ocr", "regulatory", "vision", "fusion"]

# Placeholder confidence used for visual and ocr until those modules are fully integrated.
# When a module is mocked, AgentSignal.mocked=True so fusion and the D5 audit panel
# can display which signals were real vs placeholder.
MOCK_CONFIDENCE = 0.80
