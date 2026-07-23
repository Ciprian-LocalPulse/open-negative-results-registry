"""
Tests for scripts/analyze_trends.py summarization functions.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from analyze_trends import summarize  # noqa: E402


def make_entry(domain, intervention_name, disease, institution="University Research Lab"):
    return {
        "domain": domain,
        "tested_intervention": {"name": intervention_name},
        "target_disease": disease,
        "institution_type": institution,
    }


def test_summarize_counts_domains_correctly():
    entries = [
        make_entry("Oncology", "Drug_A", "Breast Cancer"),
        make_entry("Oncology", "Drug_B", "Lung Cancer"),
        make_entry("Neurology", "Drug_C", "Alzheimer's"),
    ]
    domains, interventions, diseases, institutions = summarize(entries)
    assert domains["Oncology"] == 2
    assert domains["Neurology"] == 1


def test_summarize_counts_interventions_correctly():
    entries = [
        make_entry("Oncology", "Drug_A", "Breast Cancer"),
        make_entry("Oncology", "Drug_A", "Lung Cancer"),
    ]
    _, interventions, _, _ = summarize(entries)
    assert interventions["Drug_A"] == 2


def test_summarize_handles_missing_fields_gracefully():
    entries = [{}]  # completely empty entry
    domains, interventions, diseases, institutions = summarize(entries)
    assert domains["Unknown"] == 1
    assert interventions["Unknown"] == 1
    assert diseases["Unknown"] == 1
    assert institutions["Unknown"] == 1


def test_summarize_empty_list_returns_empty_counters():
    domains, interventions, diseases, institutions = summarize([])
    assert len(domains) == 0
    assert len(interventions) == 0
