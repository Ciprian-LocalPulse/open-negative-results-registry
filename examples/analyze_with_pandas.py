#!/usr/bin/env python3
"""
examples/analyze_with_pandas.py

A worked example showing how to load the Dark Data Medicine dataset
into a pandas DataFrame for downstream analysis -- filtering, cross-
tabulation, export to CSV/Parquet for R or Excel, or feeding into a
larger evidence-synthesis pipeline.

This does not depend on any script in scripts/ -- it reads the raw
JSON files directly, which is the intended integration point for
external tooling per docs/DATA_DICTIONARY.md.

Usage:
    python examples/analyze_with_pandas.py
    python examples/analyze_with_pandas.py --data-dir data/ --domain oncology
"""
import argparse
import json
from pathlib import Path

import pandas as pd

KNOWN_DOMAIN_DIRS = [
    "oncology", "neurology", "pharmacology", "cardiology",
    "psychiatry", "immunology", "infectious_disease", "endocrinology",
]


def load_entries(data_dir: Path, domain_filter: str | None = None) -> pd.DataFrame:
    """Load every entry JSON file into a flat DataFrame, one row per entry."""
    rows = []
    domain_dirs = [domain_filter] if domain_filter else KNOWN_DOMAIN_DIRS
    for domain_dir in domain_dirs:
        d = data_dir / domain_dir
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            with open(f, encoding="utf-8") as fh:
                entry = json.load(fh)
            # Flatten the one nested object (tested_intervention) so it
            # survives a straightforward pd.DataFrame() call cleanly.
            flat = dict(entry)
            intervention = flat.pop("tested_intervention", {}) or {}
            flat["intervention_type"] = intervention.get("type")
            flat["intervention_name"] = intervention.get("name")
            flat["_source_file"] = str(f.relative_to(data_dir))
            rows.append(flat)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default="data", help="Path to the data/ directory")
    ap.add_argument("--domain", default=None, help="Restrict to a single domain folder")
    args = ap.parse_args()

    df = load_entries(Path(args.data_dir), args.domain)

    if df.empty:
        print("No entries found -- check --data-dir points at the repo's data/ folder.")
        return

    pd.set_option("display.max_colwidth", 40)

    print(f"Loaded {len(df)} entries from {args.data_dir}\n")

    print("=== Entries per domain ===")
    print(df["domain"].value_counts().to_string())
    print()

    print("=== Entries per intervention type ===")
    print(df["intervention_type"].value_counts().to_string())
    print()

    print("=== Entries per institution type ===")
    print(df["institution_type"].value_counts().to_string())
    print()

    print("=== Full table (selected columns) ===")
    cols = ["experiment_id", "domain", "target_disease", "intervention_name",
            "institution_type", "date_concluded", "license"]
    cols = [c for c in cols if c in df.columns]
    print(df[cols].to_string(index=False))

    # Uncomment to export for use in R, Excel, or a larger pipeline:
    # df.to_csv("darkdata_flat.csv", index=False)
    # df.to_parquet("darkdata_flat.parquet", index=False)


if __name__ == "__main__":
    main()
