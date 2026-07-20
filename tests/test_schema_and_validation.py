"""
Tests for scripts/validate_submission.py and the submission schema itself.

Run with: pytest tests/ -v
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from jsonschema import Draft7Validator  # noqa: E402

SCHEMA_PATH = REPO_ROOT / "data" / "templates" / "submission_schema.json"
TEMPLATE_PATH = REPO_ROOT / "data" / "templates" / "submission_template.json"


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_schema_itself_is_valid_json_schema(schema):
    Draft7Validator.check_schema(schema)


def test_template_validates_against_schema(schema):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = json.load(f)
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(template))
    assert errors == [], f"Template should be valid, got errors: {errors}"


def test_all_seed_entries_validate_against_schema(schema):
    validator = Draft7Validator(schema)
    data_dir = REPO_ROOT / "data"
    failures = []

    for domain_dir in data_dir.iterdir():
        if not domain_dir.is_dir() or domain_dir.name == "templates":
            continue
        for json_file in domain_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                entry = json.load(f)
            errors = list(validator.iter_errors(entry))
            if errors:
                failures.append((str(json_file), errors))

    assert failures == [], f"Some seed entries failed validation: {failures}"


def test_missing_required_field_is_rejected(schema):
    validator = Draft7Validator(schema)
    broken_entry = {
        "domain": "Oncology",
        # missing experiment_id, target_disease, etc.
    }
    errors = list(validator.iter_errors(broken_entry))
    assert len(errors) > 0


def test_invalid_domain_enum_is_rejected(schema):
    validator = Draft7Validator(schema)
    entry = {
        "experiment_id": "TEST_001",
        "domain": "NotARealDomain",
        "target_disease": "Test Disease",
        "tested_intervention": {"type": "Drug", "name": "Test Drug"},
        "hypothesis": "Test hypothesis text.",
        "outcome": "Test outcome text.",
        "methodology_summary": "Test methodology.",
        "institution_type": "University Research Lab",
        "date_concluded": "2025-01-01",
        "license": "CC0-1.0",
    }
    errors = list(validator.iter_errors(entry))
    assert any("domain" in str(e.path) for e in errors)


def test_invalid_orcid_format_is_rejected(schema):
    validator = Draft7Validator(schema)
    entry = {
        "experiment_id": "TEST_002",
        "domain": "Oncology",
        "target_disease": "Test Disease",
        "tested_intervention": {"type": "Drug", "name": "Test Drug"},
        "hypothesis": "Test hypothesis text.",
        "outcome": "Test outcome text.",
        "methodology_summary": "Test methodology.",
        "researcher_orcid": "not-an-orcid",
        "institution_type": "University Research Lab",
        "date_concluded": "2025-01-01",
        "license": "CC0-1.0",
    }
    errors = list(validator.iter_errors(entry))
    assert any("researcher_orcid" in str(e.path) for e in errors)
