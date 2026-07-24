#!/usr/bin/env python3
"""
test_clinicaltrials_ingest.py

Tests the ingestion pipeline's parsing, scoring, and classification
logic entirely offline, against a fixture of REAL ClinicalTrials.gov
v2 API response records (captured 2026-07-22, see
tests/fixtures/real_ctgov_sample.json) -- not synthetic data. This
means these tests exercise the actual field paths a live API response
contains, not an idealized shape someone assumed the API would have.

Network access is intentionally NOT exercised here (see comment in
CONTRIBUTING.md on why network-dependent tests are kept separate) --
that keeps this suite fast, deterministic, and runnable in CI without
outbound network permissions.
"""
import json
import sys
from pathlib import Path

import jsonschema
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from clinicaltrials_ingest import (
    classify_domain, score_confidence, to_draft_entry, STATUS_CONFIDENCE
)

FIXTURE = Path(__file__).parent / "fixtures" / "real_ctgov_sample.json"
SCHEMA_PATH = Path(__file__).parent.parent / "data" / "templates" / "submission_schema.json"


@pytest.fixture
def real_studies():
    return json.load(open(FIXTURE))["studies"]


@pytest.fixture
def schema():
    if SCHEMA_PATH.exists():
        return json.load(open(SCHEMA_PATH))
    pytest.skip("submission_schema.json not found at expected repo-relative path")


def test_fixture_loads_and_has_studies(real_studies):
    assert len(real_studies) >= 5


def test_all_generated_drafts_validate_against_real_schema(real_studies, schema):
    for study in real_studies:
        entry = to_draft_entry(study)
        entry.pop("_ingest_confidence", None)
        jsonschema.validate(entry, schema)  # raises on failure


def test_domain_classification_never_returns_invalid_value(real_studies):
    valid_domains = {"Oncology", "Neurology", "Pharmacology", "Cardiology",
                      "Psychiatry", "Immunology", "Infectious Disease",
                      "Endocrinology", "Other"}
    for study in real_studies:
        entry = to_draft_entry(study)
        assert entry["domain"] in valid_domains


def test_institution_classification_never_returns_invalid_value(real_studies):
    valid_institutions = {"University Research Lab", "Hospital / Clinical Center",
                           "Pharmaceutical Company", "Independent Researcher",
                           "Government Institute", "Other"}
    for study in real_studies:
        entry = to_draft_entry(study)
        assert entry["institution_type"] in valid_institutions


def test_withdrawn_with_sponsor_hold_scores_high_confidence():
    study = {
        "protocolSection": {
            "statusModule": {"overallStatus": "WITHDRAWN", "whyStopped": "Sponsor Hold"}
        }
    }
    confidence, reason = score_confidence(study)
    assert confidence == "high"
    assert "Sponsor Hold" in reason


def test_withdrawn_for_funding_reasons_is_downgraded():
    study = {
        "protocolSection": {
            "statusModule": {"overallStatus": "WITHDRAWN",
                              "whyStopped": "Lack of funding for continuation"}
        }
    }
    confidence, reason = score_confidence(study)
    assert confidence == "low"
    assert "administrative" in reason.lower()


def test_completed_trials_flagged_for_manual_results_check():
    study = {"protocolSection": {"statusModule": {"overallStatus": "COMPLETED"}}}
    confidence, reason = score_confidence(study)
    assert confidence == "low"
    assert "results-section" in reason.lower()


def test_recruiting_trials_get_very_low_confidence():
    study = {"protocolSection": {"statusModule": {"overallStatus": "RECRUITING"}}}
    confidence, _ = score_confidence(study)
    assert confidence == "very_low"


def test_oncology_keyword_match():
    domain, confident = classify_domain(["Non-Small Cell Lung Cancer"])
    assert domain == "Oncology"
    assert confident is True


def test_unmatched_condition_falls_back_to_other_not_invalid_string():
    domain, confident = classify_domain(["Some Extremely Rare Undescribed Syndrome"])
    assert domain == "Other"          # must be a valid enum member
    assert confident is False          # but correctly flagged as unconfirmed


def test_every_known_status_has_a_defined_confidence_tier():
    for status in ("TERMINATED", "WITHDRAWN", "SUSPENDED", "COMPLETED"):
        assert status in STATUS_CONFIDENCE
