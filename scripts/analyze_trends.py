#!/usr/bin/env python3
"""
analyze_trends.py

Scans all negative-result JSON entries under data/<domain>/ and produces
summary statistics: which interventions, disease targets, and domains
show up most often as "negative results" (failed hypotheses).

Usage:
    python analyze_trends.py
    python analyze_trends.py --domain oncology
    python analyze_trends.py --top 20 --export report.csv
"""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
EXCLUDED_DIRS = {"templates"}


def load_entries(domain_filter=None):
    entries = []
    for domain_dir in DATA_DIR.iterdir():
        if not domain_dir.is_dir() or domain_dir.name in EXCLUDED_DIRS:
            continue
        if domain_filter and domain_dir.name.lower() != domain_filter.lower():
            continue
        for json_file in domain_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_file"] = str(json_file.relative_to(REPO_ROOT))
                    entries.append(data)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {json_file}")
    return entries


def summarize(entries):
    domains = Counter()
    interventions = Counter()
    diseases = Counter()
    institutions = Counter()

    for e in entries:
        domains[e.get("domain", "Unknown")] += 1
        interventions[e.get("tested_intervention", {}).get("name", "Unknown")] += 1
        diseases[e.get("target_disease", "Unknown")] += 1
        institutions[e.get("institution_type", "Unknown")] += 1

    return domains, interventions, diseases, institutions


def print_top(counter: Counter, title: str, top_n: int):
    print(f"\n=== {title} (top {top_n}) ===")
    for name, count in counter.most_common(top_n):
        print(f"  {count:>4}  {name}")


def export_csv(entries, path: str):
    if not entries:
        print("No entries to export.")
        return
    fieldnames = [
        "experiment_id", "domain", "target_disease",
        "intervention_name", "outcome", "institution_type", "date_concluded", "_file"
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            writer.writerow({
                "experiment_id": e.get("experiment_id", ""),
                "domain": e.get("domain", ""),
                "target_disease": e.get("target_disease", ""),
                "intervention_name": e.get("tested_intervention", {}).get("name", ""),
                "outcome": e.get("outcome", ""),
                "institution_type": e.get("institution_type", ""),
                "date_concluded": e.get("date_concluded", ""),
                "_file": e.get("_file", ""),
            })
    print(f"\nExported {len(entries)} entries to {path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze trends across negative-result submissions.")
    parser.add_argument("--domain", help="Filter by a single domain folder name (e.g. oncology)")
    parser.add_argument("--top", type=int, default=10, help="How many top items to show per category")
    parser.add_argument("--export", help="Optional path to export a flattened CSV report")
    args = parser.parse_args()

    entries = load_entries(domain_filter=args.domain)
    print(f"Loaded {len(entries)} entries from {DATA_DIR}")

    if not entries:
        print("No data found yet. Add submissions under data/<domain>/ to see trends.")
        return

    domains, interventions, diseases, institutions = summarize(entries)

    print_top(domains, "Entries per Domain", args.top)
    print_top(interventions, "Most Frequently Failed Interventions", args.top)
    print_top(diseases, "Most Frequently Studied Disease Targets", args.top)
    print_top(institutions, "Submissions by Institution Type", args.top)

    if args.export:
        export_csv(entries, args.export)


if __name__ == "__main__":
    main()
