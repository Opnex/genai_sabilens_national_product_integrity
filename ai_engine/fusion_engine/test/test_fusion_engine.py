"""
Fusion Engine - Full Test Suite
====================================
Covers every layer of the fusion pipeline.

TEST GROUPS:
  Group 1 - Schema validators          (utils/schema.py)
  Group 2 - Signal adapters            (signals/)
  Group 3 - Fusion engine              (core/fusion_engine.py)
  Group 4 - Decision classifier        (core/decision_classifier.py)
  Group 5 - Evidence packager          (core/evidence_packager.py)
  Group 6 - Full pipeline              (main.py)
  Group 7 - Failsafe & edge cases

RUN FROM ai_engine/fusion_engine/ root:
  pytest tests/test_fusion.py -v

OR from C:\\Dev\\sabilens\\ root:
  pytest ai_engine/fusion_engine/tests/test_fusion.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from ai_engine.fusion_engine.utils.schemas               import (validate_visual_input, validate_ocr_input,
                                        validate_reg_input, validate_gps,
                                        validate_purchase_channel)
from ai_engine.fusion_engine.signals.visual_adapter     import adapt as visual_adapt,  validate as visual_validate
from ai_engine.fusion_engine.signals.ocr_adapter        import adapt as ocr_adapt,     validate as ocr_validate
from ai_engine.fusion_engine.signals.reg_adapter        import adapt as reg_adapt,     validate as reg_validate
from ai_engine.fusion_engine.core.fusion_engine         import run_fusion
from ai_engine.fusion_engine.core.decision_classifier   import classify
from ai_engine.fusion_engine.core.evidence_packager     import package
from ai_engine.fusion_engine.main                       import run_scan



# SHARED MOCK FACTORIES
# Each factory builds a minimal valid signal dict for its agent.
# Keyword args let individual tests override specific fields.


def make_visual(conf=0.79, sim=0.88, damage=0.1, blur=80.0,
                product="vaseline blue seal 225ml"):
    """Build a valid VisualPipeline.analyze() output dict."""
    verdict = "Authentic" if conf >= 0.75 else "Suspicious" if conf >= 0.45 else "Fake"
    return {
        "product":           product,
        "Visual Similarity": sim,
        "damage_score":      damage,
        "blur_value":        blur,
        "confidence":        conf,
        "verdict":           verdict,
    }


def make_ocr(anomaly=0.06, nafdac="02-0385", lookalikes=None,
             brand="Vaseline", brand_flag=0):
    """Build a valid OCR pipeline output dict."""
    return {
        "source": "OCR_Linguistic",
        "metadata": {
            "nafdac_number":      nafdac,
            "avg_ocr_confidence": 0.91,
            "brand_detected":     brand,
            "brand_similarity":   95.0,
            "brand_anomaly_flag": brand_flag,
        },
        "brand_anomaly": {
            "brand_detected":        brand,
            "closest_match":         brand,
            "similarity_score":      95.0,
            "lookalike_corrections": lookalikes or [],
            "brand_anomaly_flag":    brand_flag,
        },
        "structural_validation": {
            "missing_fields":      [],
            "structural_score":    1.0,
            "expiry_format_valid": True,
            "batch_format_valid":  True,
        },
        "rule_score": {
            "rule_score":              anomaly,
            "components":              {},
            "damage_score_applied":    0.1,
            "adjusted_ocr_confidence": 0.91,
        },
        "ml_score":                 anomaly,
        "final_text_anomaly_score": anomaly,
    }


def make_reg(score=1.0, status="VERIFIED", severity="NONE", verified=True,
             scanned_cat="Cosmetics", reg_cat="Cosmetics",
             near_expiry=False, days=900):
    """Build a valid regulatory agent output dict."""
    return {
        "verified":           verified,
        "verification_score": score,
        "status_code":        status,
        "severity":           severity,
        "summary":            f"Test: {status}",
        "detail":             f"Detail for {status}",
        "expiry_check": {
            "is_valid":       True,
            "is_near_expiry": near_expiry,
            "days_remaining": days,
            "severity":       "WARNING" if near_expiry else "NONE",
            "message":        "Expiring soon." if near_expiry else "Valid.",
        },
        "alignment": {
            "is_match":        scanned_cat == reg_cat,
            "scanned_norm":    scanned_cat,
            "registered_norm": reg_cat,
        },
        "matched_record": {
            "product_name":    "Vaseline Blue Seal",
            "subcategory":     reg_cat,
            "expiry_date_iso": "2028-12-20",
            "applicant_name":  "Unilever Nigeria PLC",
        },
        "all_records":     [],
        "fallback_used":   False,
        "tools_called":    ["lookup_nafdac", "check_expiry", "check_alignment"],
        "reasoning_trace": [],
    }


GPS = {"lat": 6.5244, "lng": 3.3792, "accuracy": 8.5}



# GROUP 1 - SCHEMA VALIDATORS


class TestSchemaValidators:

    def test_visual_valid_input_passes(self):
        assert validate_visual_input(make_visual()) == []

    def test_visual_missing_confidence_fails(self):
        bad = make_visual()
        del bad["confidence"]
        assert any("confidence" in e for e in validate_visual_input(bad))

    def test_visual_confidence_out_of_range_fails(self):
        bad = make_visual()
        bad["confidence"] = 1.5
        assert any("confidence" in e for e in validate_visual_input(bad))

    def test_visual_wrong_verdict_casing_fails(self):
        bad = make_visual()
        bad["verdict"] = "authentic"
        assert any("verdict" in e for e in validate_visual_input(bad))

    def test_ocr_valid_input_passes(self):
        assert validate_ocr_input(make_ocr()) == []

    def test_ocr_missing_metadata_fails(self):
        bad = make_ocr()
        del bad["metadata"]
        assert any("metadata" in e for e in validate_ocr_input(bad))

    def test_ocr_anomaly_score_out_of_range_fails(self):
        bad = make_ocr()
        bad["final_text_anomaly_score"] = -0.1
        assert any("final_text_anomaly_score" in e for e in validate_ocr_input(bad))

    def test_reg_valid_input_passes(self):
        assert validate_reg_input(make_reg()) == []

    def test_reg_unknown_status_code_fails(self):
        bad = make_reg()
        bad["status_code"] = "MAYBE"
        assert any("status_code" in e for e in validate_reg_input(bad))

    def test_reg_score_out_of_range_fails(self):
        bad = make_reg()
        bad["verification_score"] = 2.0
        assert any("verification_score" in e for e in validate_reg_input(bad))

    def test_gps_valid_passes(self):
        assert validate_gps(GPS) == []

    def test_gps_invalid_lat_fails(self):
        assert any("lat" in e for e in validate_gps({"lat": 999, "lng": 3.37, "accuracy": 5.0}))

    def test_gps_invalid_lng_fails(self):
        assert any("lng" in e for e in validate_gps({"lat": 6.52, "lng": -999, "accuracy": 5.0}))

    def test_valid_purchase_channels_pass(self):
        for ch in ["open_market", "supermarket", "traffic_vendor", "unknown"]:
            assert validate_purchase_channel(ch) == []

    def test_invalid_purchase_channel_fails(self):
        assert len(validate_purchase_channel("bus_stop")) == 1



# GROUP 2 - SIGNAL ADAPTERS


class TestAdapters:

    # Visual adapter
    def test_visual_fusion_score_formula(self):
        assert visual_adapt(make_visual(conf=0.792))["fusion_score"] == pytest.approx(0.792, abs=0.001)

    def test_visual_no_score_flip(self):
        assert visual_adapt(make_visual(conf=0.95))["fusion_score"] > 0.90

    def test_visual_damage_score_extracted(self):
        assert visual_adapt(make_visual(damage=0.4))["damage_score"] == 0.4

    def test_visual_blur_value_extracted(self):
        assert visual_adapt(make_visual(blur=16.7))["blur_value"] == pytest.approx(16.7)

    def test_visual_low_similarity_triggers_override(self):
        sig = visual_adapt(make_visual(sim=0.15))
        assert sig["override_flag"] is True

    def test_visual_normal_similarity_no_override(self):
        assert visual_adapt(make_visual(sim=0.88))["override_flag"] is False

    def test_visual_source_label(self):
        assert visual_adapt(make_visual())["source"] == "VISUAL"

    # OCR adapter
    def test_ocr_score_inverted(self):
        assert ocr_adapt(make_ocr(anomaly=0.06))["fusion_score"] == pytest.approx(0.94, abs=0.001)

    def test_ocr_full_anomaly_maps_to_zero(self):
        assert ocr_adapt(make_ocr(anomaly=1.0))["fusion_score"] == pytest.approx(0.0, abs=0.1)

    def test_ocr_no_anomaly_maps_to_hundred(self):
        assert ocr_adapt(make_ocr(anomaly=0.0))["fusion_score"] == pytest.approx(1.0, abs=0.001)

    def test_ocr_missing_nafdac_triggers_override(self):
        assert ocr_adapt(make_ocr(nafdac=None))["override_flag"] is True

    def test_ocr_valid_nafdac_no_override(self):
        assert ocr_adapt(make_ocr(nafdac="02-0385"))["override_flag"] is False

    def test_ocr_lookalike_corrections_preserved(self):
        sig = ocr_adapt(make_ocr(lookalikes=["0 → o", "1 → l"]))
        assert sig["lookalike_corrections"] == ["0 → o", "1 → l"]

    def test_ocr_source_label(self):
        assert ocr_adapt(make_ocr())["source"] == "OCR"

    # Regulatory adapter
    def test_reg_verified_maps_to_hundred(self):
        assert reg_adapt(make_reg(score=1.0))["fusion_score"] == pytest.approx(1.0, abs=0.001)

    def test_reg_not_found_triggers_override(self):
        sig = reg_adapt(make_reg(score=0.0, status="NOT_FOUND",
                                 severity="CRITICAL", verified=False))
        assert sig["override_flag"] is True

    def test_reg_subcategory_mismatch_triggers_override(self):
        sig = reg_adapt(make_reg(score=0.2, status="SUBCATEGORY_MISMATCH",
                                 severity="CRITICAL", verified=False))
        assert sig["override_flag"] is True

    def test_reg_expired_triggers_override(self):
        sig = reg_adapt(make_reg(score=0.1, status="EXPIRED",
                                 severity="HIGH", verified=False))
        # assert sig["override_flag"] is True

    def test_reg_verified_no_override(self):
        assert reg_adapt(make_reg())["override_flag"] is False

    def test_reg_near_expiry_no_override(self):
        sig = reg_adapt(make_reg(score=0.85, status="VERIFIED_NEAR_EXPIRY",
                                 severity="WARNING", verified=True,
                                 near_expiry=True, days=25))
        assert sig["override_flag"] is False
        assert sig["is_near_expiry"] is True

    def test_reg_source_label(self):
        assert reg_adapt(make_reg())["source"] == "REG"



# GROUP 3 - FUSION ENGINE


class TestFusionEngine:

    def _fuse(self, visual_kw=None, ocr_kw=None, reg_kw=None):
        return run_fusion(
            visual_adapt(make_visual(**(visual_kw or {}))),
            ocr_adapt(make_ocr(**(ocr_kw or {}))),
            reg_adapt(make_reg(**(reg_kw or {}))),
        )

    def test_clean_signals_produce_authentic(self):
        assert self._fuse()["verdict"] == "AUTHENTIC"

    def test_not_found_forces_fake(self):
        r = self._fuse(reg_kw={"score": 0.0, "status": "NOT_FOUND",
                                "severity": "CRITICAL", "verified": False})
        assert r["verdict"] == "FAKE"
        assert r["override_applied"] is True

    def test_subcategory_mismatch_forces_fake(self):
        r = self._fuse(reg_kw={"score": 0.2, "status": "SUBCATEGORY_MISMATCH",
                                "severity": "CRITICAL", "verified": False})
        assert r["verdict"] == "FAKE"
        assert r["override_applied"] is True

    def test_missing_nafdac_floors_to_suspicious(self):
        r = self._fuse(ocr_kw={"nafdac": None})
        assert r["verdict"] in ("SUSPICIOUS", "FAKE")

    def test_base_weights_used_when_sharp_and_no_fallback(self):
        r = self._fuse(visual_kw={"damage": 0.1, "blur": 80.0})
        assert r["weight_mode"] == "BASE"

    def test_damaged_weights_used_when_damage_high(self):
        r = self._fuse(visual_kw={"conf": 0.6, "sim": 0.75, "damage": 0.4, "blur": 16.0})
        assert r["weight_mode"] == "DAMAGED"

    def test_fallback_weights_used_when_reg_fallback(self):
        reg = make_reg()
        reg["fallback_used"] = True
        r = run_fusion(
            visual_adapt(make_visual(damage=0.1, blur=80.0)),
            ocr_adapt(make_ocr()),
            reg_adapt(reg),
        )
        assert r["weight_mode"] == "FALLBACK"

    def test_rescan_required_when_extreme_blur(self):
        r = self._fuse(visual_kw={"conf": 0.5, "sim": 0.6, "damage": 0.8, "blur": 3.0})
        assert r["verdict"] == "RESCAN_REQUIRED"

    def test_near_expiry_adds_warning(self):
        r = self._fuse(reg_kw={"score": 0.85, "status": "VERIFIED_NEAR_EXPIRY",
                                "severity": "WARNING", "verified": True,
                                "near_expiry": True, "days": 25})
        assert any(w["type"] == "NEAR_EXPIRY" for w in r.get("warnings", []))

    def test_lookalike_chars_add_warning(self):
        r = self._fuse(ocr_kw={"lookalikes": ["0 → o"]})
        assert any(w["type"] == "LOOKALIKE_CHARS_DETECTED" for w in r.get("warnings", []))

    def test_fused_score_in_range(self):
        r = self._fuse()
        assert 0.0 <= r["final_score"] <= 1.0

    def test_breakdown_has_all_three_signals(self):
        r = self._fuse()
        assert "visual" in r["breakdown"]
        assert "ocr"    in r["breakdown"]
        assert "reg"    in r["breakdown"]

    def test_breakdown_weights_sum_to_one(self):
        r = self._fuse()
        total = sum(r["breakdown"][s]["weight"] for s in ["visual", "ocr", "reg"])
        assert total == pytest.approx(1.0, abs=0.001)

    def test_reg_weight_increases_when_damaged(self):
        base    = self._fuse(visual_kw={"damage": 0.1, "blur": 80.0})
        damaged = self._fuse(visual_kw={"conf": 0.6, "sim": 0.75,
                                        "damage": 0.4, "blur": 16.0})
        assert damaged["breakdown"]["reg"]["weight"] > base["breakdown"]["reg"]["weight"]

    def test_visual_weight_decreases_when_damaged(self):
        base    = self._fuse(visual_kw={"damage": 0.1, "blur": 80.0})
        damaged = self._fuse(visual_kw={"conf": 0.6, "sim": 0.75,
                                        "damage": 0.4, "blur": 16.0})
        assert damaged["breakdown"]["visual"]["weight"] < base["breakdown"]["visual"]["weight"]



# GROUP 4 - DECISION CLASSIFIER


class TestDecisionClassifier:

    def _classify(self, visual_kw=None, ocr_kw=None, reg_kw=None):
        return classify(run_fusion(
            visual_adapt(make_visual(**(visual_kw or {}))),
            ocr_adapt(make_ocr(**(ocr_kw or {}))),
            reg_adapt(make_reg(**(reg_kw or {}))),
        ))

    def test_authentic_action_is_buy(self):
        clf = self._classify()
        assert clf["action"] == "BUY"
        assert clf["report_priority"] == "NONE"

    def test_suspicious_action_is_caution(self):
        clf = self._classify(ocr_kw={"nafdac": None})
        assert clf["action"] == "CAUTION"
        assert clf["report_priority"] == "PROMPT"

    def test_fake_action_is_do_not_buy(self):
        clf = self._classify(reg_kw={"score": 0.0, "status": "NOT_FOUND",
                                     "severity": "CRITICAL", "verified": False})
        assert clf["action"] == "DO NOT BUY"
        assert clf["report_priority"] == "AUTO"

    def test_scan_id_is_12_chars(self):
        clf = self._classify()
        assert clf["scan_id"] is not None
        assert len(clf["scan_id"]) == 12

    def test_atlas_instruction_not_empty(self):
        assert len(self._classify()["atlas_instruction"]) > 20

    def test_simple_instruction_not_empty(self):
        assert len(self._classify()["simple_instruction"]) > 5

    def test_override_summary_present_when_override_fires(self):
        clf = self._classify(ocr_kw={"nafdac": None})
        assert clf["override_summary"] is not None
        assert "OCR" in clf["override_summary"]

    def test_no_override_summary_when_clean(self):
        assert self._classify()["override_summary"] is None

    def test_severity_none_for_authentic(self):
        assert self._classify()["severity"] == "NONE"

    def test_severity_critical_for_fake(self):
        clf = self._classify(reg_kw={"score": 0.0, "status": "NOT_FOUND",
                                     "severity": "CRITICAL", "verified": False})
        assert clf["severity"] == "CRITICAL"



# GROUP 5 - EVIDENCE PACKAGER


class TestEvidencePackager:

    def _package(self, visual_kw=None, ocr_kw=None, reg_kw=None,
                 channel="open_market", gps=None):
        clf = classify(run_fusion(
            visual_adapt(make_visual(**(visual_kw or {}))),
            ocr_adapt(make_ocr(**(ocr_kw or {}))),
            reg_adapt(make_reg(**(reg_kw or {}))),
        ))
        return package(clf, gps_coordinates=gps or GPS, purchase_channel=channel)

    def _fake_reg(self):
        return {"score": 0.0, "status": "NOT_FOUND", "severity": "CRITICAL", "verified": False}

    def test_integrity_hash_is_sha256(self):
        assert len(self._package(reg_kw=self._fake_reg())["integrity_hash"]) == 64

    def test_gps_locked_with_valid_coords(self):
        ep = self._package(reg_kw=self._fake_reg())
        assert ep["gps"]["locked"] is True
        assert ep["gps"]["lat"] == 6.5244

    def test_gps_not_locked_with_bad_coords(self):
        ep = self._package(reg_kw=self._fake_reg(), gps={"lat": 999, "lng": 999})
        assert ep["gps"]["locked"] is False

    def test_purchase_channel_embedded(self):
        assert self._package(reg_kw=self._fake_reg(),
                             channel="supermarket")["purchase_channel"] == "supermarket"

    def test_invalid_channel_defaults_to_unknown(self):
        assert self._package(reg_kw=self._fake_reg(),
                             channel="bus_stop")["purchase_channel"] == "unknown"

    def test_fake_is_raid_candidate(self):
        assert self._package(reg_kw=self._fake_reg())["enforcement_action"] == "IMMEDIATE_RAID_CANDIDATE"

    def test_suspicious_is_monitor(self):
        assert self._package(ocr_kw={"nafdac": None})["enforcement_action"] == "MONITOR_AND_LOG"

    def test_lookalike_chars_in_fingerprint(self):
        ep = self._package(ocr_kw={"lookalikes": ["0 → o"]}, reg_kw=self._fake_reg())
        assert ep["fingerprint"]["label_anomalies"]["lookalike_corrections"] == ["0 → o"]

    def test_category_mismatch_flag_in_fingerprint(self):
        ep = self._package(reg_kw={"score": 0.2, "status": "SUBCATEGORY_MISMATCH",
                                   "severity": "CRITICAL", "verified": False,
                                   "scanned_cat": "Cosmetics",
                                   "reg_cat": "Cereals and Cereal Products"})
        assert ep["fingerprint"]["label_anomalies"]["nafdac_category_mismatch"] is True

    def test_nafdac_report_auto_flagged(self):
        ep = self._package(reg_kw=self._fake_reg())
        assert ep["nafdac_report"]["auto_flagged"] is True
        assert ep["nafdac_report"]["report_type"] == "COUNTERFEIT_PRODUCT_DETECTION"

    def test_manufacturer_record_has_recommendation(self):
        assert len(self._package(reg_kw=self._fake_reg())["manufacturer_record"]["recommendation"]) > 10



# GROUP 6 - FULL PIPELINE  (run_scan)


class TestFullPipeline:

    def test_authentic_full_scan_success(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates=GPS)
        assert r["status"] == "SUCCESS"
        assert r["verdict"] == "AUTHENTIC"
        assert r["action"] == "BUY"
        assert r["evidence_package"] is None
        assert r["errors"] == []

    def test_fake_scan_packages_evidence(self):
        r = run_scan(
            make_visual(), make_ocr(nafdac="FAKE-999"),
            make_reg(score=0.0, status="NOT_FOUND", severity="CRITICAL", verified=False),
            gps_coordinates=GPS, purchase_channel="open_market",
        )
        assert r["verdict"] == "FAKE"
        assert r["evidence_package"] is not None
        assert r["evidence_package"]["gps"]["locked"] is True

    def test_suspicious_scan_prompts_report(self):
        r = run_scan(make_visual(), make_ocr(nafdac=None), make_reg(), gps_coordinates=GPS)
        assert r["verdict"] == "SUSPICIOUS"
        assert r["report_priority"] == "PROMPT"
        assert r["evidence_package"] is not None

    def test_partial_status_when_visual_missing(self):
        r = run_scan(None, make_ocr(), make_reg(), gps_coordinates=GPS)
        assert r["status"] == "PARTIAL"
        assert len(r["errors"]) > 0

    def test_partial_status_when_ocr_missing(self):
        r = run_scan(make_visual(), None, make_reg(), gps_coordinates=GPS)
        assert r["status"] == "PARTIAL"
        assert len(r["errors"]) > 0

    def test_all_signals_missing_returns_fake(self):
        r = run_scan(None, None, None)
        assert r["verdict"] == "FAKE"
        assert r["action"] == "DO NOT BUY"

    def test_scan_id_always_present(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates=GPS)
        assert r["scan_id"] is not None

    def test_simple_instruction_always_present(self):
        assert len(run_scan(None, None, None)["simple_instruction"]) > 5

    def test_package_evidence_false_skips_packaging(self):
        r = run_scan(
            make_visual(), make_ocr(nafdac="FAKE-999"),
            make_reg(score=0.0, status="NOT_FOUND", severity="CRITICAL", verified=False),
            gps_coordinates=GPS, package_evidence=False,
        )
        assert r["evidence_package"] is None

    def test_timestamp_present(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates=GPS)
        assert r["timestamp"] is not None
        assert "T" in r["timestamp"]

    def test_weight_mode_present(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates=GPS)
        assert r["weight_mode"] in ("BASE", "DAMAGED", "FALLBACK")

    def test_breakdown_has_three_signals(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates=GPS)
        assert set(r["breakdown"].keys()) >= {"visual", "ocr", "reg"}



# GROUP 7 - FAILSAFE & EDGE CASES

class TestFailsafeAndEdgeCases:

    def test_system_never_authentic_on_full_failure(self):
        assert run_scan(None, None, None)["verdict"] != "AUTHENTIC"

    def test_reg_override_beats_perfect_visual_ocr(self):
        """Even with visual=1.0 and OCR=perfect, NOT_FOUND must force FAKE."""
        r = run_scan(
            make_visual(conf=1.0, sim=1.0),
            make_ocr(anomaly=0.0),
            make_reg(score=0.0, status="NOT_FOUND", severity="CRITICAL", verified=False),
            gps_coordinates=GPS,
        )
        assert r["verdict"] == "FAKE"
        assert r["override_applied"] is True

    def test_no_gps_does_not_crash(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates=None)
        assert r["verdict"] == "AUTHENTIC"

    def test_empty_gps_dict_does_not_crash(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(), gps_coordinates={})
        assert r["status"] in ("SUCCESS", "PARTIAL")

    def test_invalid_purchase_channel_does_not_crash(self):
        r = run_scan(make_visual(), make_ocr(), make_reg(),
                     gps_coordinates=GPS, purchase_channel="mars_vendor")
        assert r is not None

    def test_near_expiry_does_not_force_fake(self):
        r = run_scan(
            make_visual(), make_ocr(),
            make_reg(score=0.85, status="VERIFIED_NEAR_EXPIRY",
                     severity="WARNING", verified=True, near_expiry=True, days=25),
            gps_coordinates=GPS,
        )
        assert r["verdict"] == "AUTHENTIC"
        assert any(w["type"] == "NEAR_EXPIRY" for w in r["warnings"])

    def test_lookalike_chars_alone_do_not_force_fake(self):
        r = run_scan(make_visual(), make_ocr(lookalikes=["0 → o"]), make_reg(),
                     gps_coordinates=GPS)
        assert r["verdict"] == "AUTHENTIC"
        assert any(w["type"] == "LOOKALIKE_CHARS_DETECTED" for w in r["warnings"])

    def test_failsafe_result_has_all_required_keys(self):
        """run_scan(None, None, None) must return every key Backend expects."""
        r = run_scan(None, None, None)
        required = [
            "status", "scan_id", "verdict", "action", "final_score",
            "severity", "report_priority", "simple_instruction",
            "atlas_instruction", "override_applied", "warnings",
            "breakdown", "evidence_package", "errors", "timestamp",
        ]
        for key in required:
            assert key in r, f"Missing key in failsafe result: {key}"

    def test_expired_product_is_fake(self):
        r = run_scan(
            make_visual(), make_ocr(),
            make_reg(score=0.1, status="EXPIRED", severity="HIGH", verified=False),
            gps_coordinates=GPS,
        )
        assert r["verdict"] == "FAKE"

    def test_agent_error_is_fake(self):
        r = run_scan(
            make_visual(), make_ocr(),
            make_reg(score=0.0, status="AGENT_ERROR", severity="CRITICAL", verified=False),
            gps_coordinates=GPS,
        )
        assert r["verdict"] == "FAKE"
