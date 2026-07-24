#!/usr/bin/env python3
"""
test_generate_search_index.py

Covers scripts/generate_search_index.py, which builds site/data_index.json
from data/. Had zero test coverage; a silent regression here would break
the static search page without any CI signal.
"""
import importlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def make_entry(tmp_path, domain, name, **overrides):
    domain_dir = tmp_path / "data" / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "experiment_id": f"{domain.upper()}-001",
        "domain": domain.capitalize(),
        "target_disease": "Test Disease",
        "tested_intervention": {"type": "Drug", "name": "Test Compound"},
        "outcome": "No effect observed.",
        "date_concluded": "2025-01-01",
        "institution_type": "University Research Lab",
        "source_url": "https://example.org",
    }
    entry.update(overrides)
    with open(domain_dir / name, "w", encoding="utf-8") as f:
        json.dump(entry, f)
    return entry


def load_module_pointed_at(tmp_path, monkeypatch):
    """Reload the module with REPO_ROOT/DATA_DIR/SITE_DIR redirected to a
    scratch directory, so the test never touches the real dataset."""
    import generate_search_index as gsi
    importlib.reload(gsi)
    monkeypatch.setattr(gsi, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gsi, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(gsi, "SITE_DIR", tmp_path / "site")
    return gsi


def test_build_index_includes_all_domain_entries(tmp_path, monkeypatch):
    make_entry(tmp_path, "oncology", "e1.json")
    make_entry(tmp_path, "cardiology", "e1.json")
    gsi = load_module_pointed_at(tmp_path, monkeypatch)

    index = gsi.build_index()

    assert len(index) == 2
    assert {e["experiment_id"] for e in index} == {"ONCOLOGY-001", "CARDIOLOGY-001"}


def test_build_index_excludes_templates_dir(tmp_path, monkeypatch):
    make_entry(tmp_path, "templates", "submission_template.json")
    make_entry(tmp_path, "oncology", "e1.json")
    gsi = load_module_pointed_at(tmp_path, monkeypatch)

    index = gsi.build_index()

    assert len(index) == 1
    assert index[0]["domain"] == "Oncology"


def test_build_index_flattens_intervention_name(tmp_path, monkeypatch):
    make_entry(tmp_path, "oncology", "e1.json")
    gsi = load_module_pointed_at(tmp_path, monkeypatch)

    index = gsi.build_index()

    assert index[0]["intervention_name"] == "Test Compound"


def test_build_index_missing_optional_fields_default_empty(tmp_path, monkeypatch):
    domain_dir = tmp_path / "data" / "oncology"
    domain_dir.mkdir(parents=True)
    with open(domain_dir / "sparse.json", "w", encoding="utf-8") as f:
        json.dump({"experiment_id": "SPARSE-001"}, f)
    gsi = load_module_pointed_at(tmp_path, monkeypatch)

    index = gsi.build_index()

    assert index[0]["target_disease"] == ""
    assert index[0]["intervention_name"] == ""


def test_main_writes_index_file_to_disk(tmp_path, monkeypatch, capsys):
    make_entry(tmp_path, "oncology", "e1.json")
    gsi = load_module_pointed_at(tmp_path, monkeypatch)

    gsi.main()

    out_path = tmp_path / "site" / "data_index.json"
    assert out_path.exists()
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(written) == 1
    assert "Wrote 1 entries" in capsys.readouterr().out
