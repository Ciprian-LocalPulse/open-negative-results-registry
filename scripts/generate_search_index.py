#!/usr/bin/env python3
"""
generate_search_index.py

Builds a single flattened JSON index (site/data_index.json) from every
entry under data/<domain>/, for use by the static client-side search page
in site/index.html. Run this after any data change, or wire it into CI.

Usage:
    python scripts/generate_search_index.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SITE_DIR = REPO_ROOT / "site"
EXCLUDED_DIRS = {"templates"}


def build_index():
    index = []
    for domain_dir in sorted(DATA_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name in EXCLUDED_DIRS:
            continue
        for json_file in sorted(domain_dir.glob("*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                entry = json.load(f)
            intervention = entry.get("tested_intervention", {})
            index.append({
                "experiment_id": entry.get("experiment_id", ""),
                "domain": entry.get("domain", ""),
                "target_disease": entry.get("target_disease", ""),
                "intervention_name": intervention.get("name", ""),
                "outcome": entry.get("outcome", ""),
                "date_concluded": entry.get("date_concluded", ""),
                "institution_type": entry.get("institution_type", ""),
                "source_url": entry.get("source_url", ""),
                "file": str(json_file.relative_to(REPO_ROOT)),
            })
    return index


def main():
    SITE_DIR.mkdir(exist_ok=True)
    index = build_index()
    out_path = SITE_DIR / "data_index.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(index)} entries to {out_path}")


if __name__ == "__main__":
    main()
