#!/usr/bin/env python3
"""
test_validate_submission.py

Covers scripts/validate_submission.py, which had zero test coverage
despite being the schema gate CI runs on every submission PR.
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_submission import load_schema, validate_file, gather_targets  # noqa: E402

VALID_ENTRY = {
    "experiment_id": "TEST-0001",
    "domain": "Oncology",
    "target_disease": "Test Disease",
    "tested_intervention": {"type": "Drug", "name": "Test Compound"},
    "hypothesis": "Test compound reduces tumor size.",
    "outcome": "No significant difference from placebo.",
    "methodology_summary": "Randomized controlled trial, n=200.",
    "institution_type": "University Research Lab",
    "date_concluded": "2025-01-01",
    "license": "CC0-1.0",
}


@pytest.fixture
def schema():
    return load_schema()


def write_json(tmp_path, name, data):
    path = tmp_path / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return path


def test_valid_entry_passes(tmp_path, schema, capsys):
    path = write_json(tmp_path, "valid.json", VALID_ENTRY)
    assert validate_file(path, schema) is True
    assert "[OK]" in capsys.readouterr().out


def test_missing_required_field_fails(tmp_path, schema, capsys):
    entry = dict(VALID_ENTRY)
    del entry["hypothesis"]
    path = write_json(tmp_path, "missing.json", entry)
    assert validate_file(path, schema) is False
    assert "[FAIL]" in capsys.readouterr().out


def test_invalid_domain_enum_fails(tmp_path, schema):
    entry = dict(VALID_ENTRY)
    entry["domain"] = "Not A Real Domain"
    path = write_json(tmp_path, "bad_domain.json", entry)
    assert validate_file(path, schema) is False


def test_malformed_json_reports_fail_not_crash(tmp_path, schema, capsys):
    path = tmp_path / "broken.json"
    path.write_text("{not valid json", encoding="utf-8")
    assert validate_file(path, schema) is False
    assert "invalid JSON" in capsys.readouterr().out


def test_gather_targets_single_file(tmp_path):
    path = write_json(tmp_path, "one.json", VALID_ENTRY)
    assert gather_targets(path) == [path]


def test_gather_targets_folder_excludes_templates(tmp_path):
    (tmp_path / "templates").mkdir()
    write_json(tmp_path / "templates", "submission_template.json", VALID_ENTRY)
    real = write_json(tmp_path, "real_entry.json", VALID_ENTRY)

    targets = gather_targets(tmp_path)

    assert real in targets
    assert all("templates" not in t.parts for t in targets)


def test_gather_targets_folder_finds_nested_json(tmp_path):
    (tmp_path / "oncology").mkdir()
    nested = write_json(tmp_path / "oncology", "entry.json", VALID_ENTRY)
    assert nested in gather_targets(tmp_path)
