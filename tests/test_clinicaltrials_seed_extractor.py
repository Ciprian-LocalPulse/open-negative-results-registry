#!/usr/bin/env python3
"""
test_clinicaltrials_seed_extractor.py

Covers the pure transform logic in the deprecated
scripts/clinicaltrials_seed_extractor.py (to_draft_entry). Deliberately
does NOT test fetch_studies, since that hits the live ClinicalTrials.gov
API -- CI shouldn't depend on a third-party service being up. Uses the
same real fixture as test_clinicaltrials_ingest.py so both scripts are
checked against the same real-world payload shape.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from clinicaltrials_seed_extractor import to_draft_entry  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "real_ctgov_sample.json"


def load_studies():
    with open(FIXTURE, "r", encoding="utf-8") as f:
        return json.load(f)["studies"]


def test_to_draft_entry_produces_all_required_schema_fields():
    study = load_studies()[0]
    entry = to_draft_entry(study)

    for field in (
        "experiment_id", "domain", "target_disease", "tested_intervention",
        "hypothesis", "outcome", "methodology_summary", "institution_type",
        "date_concluded", "license",
    ):
        assert field in entry


def test_to_draft_entry_flags_domain_for_manual_review():
    study = load_studies()[0]
    entry = to_draft_entry(study)
    # Unlike clinicaltrials_ingest.py, the deprecated extractor never
    # auto-classifies domain -- it always defers to a human curator.
    assert entry["domain"] == "Unclassified - please review"


def test_to_draft_entry_handles_study_with_no_interventions():
    study = {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT00000000"},
            "statusModule": {"overallStatus": "TERMINATED"},
            "conditionsModule": {"conditions": ["Test Condition"]},
            "armsInterventionsModule": {},
            "designModule": {},
        }
    }
    entry = to_draft_entry(study)
    assert entry["tested_intervention"]["name"] == "Unknown"
    assert entry["tested_intervention"]["type"] == "Other"


def test_to_draft_entry_builds_source_url_from_nct_id():
    study = load_studies()[0]
    entry = to_draft_entry(study)
    nct_id = entry["experiment_id"]
    assert entry["source_url"] == f"https://clinicaltrials.gov/study/{nct_id}"


def test_to_draft_entry_always_marks_draft_keywords():
    study = load_studies()[0]
    entry = to_draft_entry(study)
    assert "draft" in entry["keywords"]
    assert "needs_review" in entry["keywords"]
