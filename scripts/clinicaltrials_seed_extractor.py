#!/usr/bin/env python3
"""
clinicaltrials_seed_extractor.py

Helper script to seed the repository with candidate negative-result entries
pulled from the public ClinicalTrials.gov API (no key required).

This produces DRAFT entries only -- a human curator must review each one,
fill in the outcome/methodology summary properly, and move it into the
correct data/<domain>/ folder before it is considered a valid submission.

Usage:
    python clinicaltrials_seed_extractor.py --condition "breast cancer" --limit 50 --out drafts/

Requires:
    pip install requests
"""

import argparse
import json
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency. Install with: pip install requests --break-system-packages")
    raise SystemExit(1)

API_URL = "https://clinicaltrials.gov/api/v2/studies"

# Statuses that typically indicate a trial did not produce a positive result
CANDIDATE_STATUSES = ["TERMINATED", "WITHDRAWN", "SUSPENDED", "COMPLETED"]


def fetch_studies(condition: str, limit: int):
    results = []
    page_token = None
    page_size = min(limit, 100)

    while len(results) < limit:
        params = {
            "query.cond": condition,
            "pageSize": page_size,
            "format": "json",
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        studies = data.get("studies", [])
        results.extend(studies)

        page_token = data.get("nextPageToken")
        if not page_token or not studies:
            break

        time.sleep(0.5)  # be polite to the public API

    return results[:limit]


def to_draft_entry(study: dict) -> dict:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    arms_module = protocol.get("armsInterventionsModule", {})
    design_module = protocol.get("designModule", {})

    interventions = arms_module.get("interventions", [])
    intervention_name = interventions[0].get("name") if interventions else "Unknown"
    intervention_type = interventions[0].get("type") if interventions else "Other"

    return {
        "experiment_id": identification.get("nctId", "UNKNOWN"),
        "domain": "Unclassified - please review",
        "target_disease": ", ".join(conditions_module.get("conditions", ["Unknown"])),
        "tested_intervention": {
            "type": intervention_type,
            "name": intervention_name,
            "dosage": "See ClinicalTrials.gov record",
        },
        "hypothesis": "DRAFT - fill in based on study record.",
        "outcome": f"Trial status: {status_module.get('overallStatus', 'Unknown')}. "
                   f"Human curator must confirm whether primary endpoint was met.",
        "methodology_summary": design_module.get("studyType", "Unknown study design"),
        "researcher_orcid": "0000-0000-0000-0000",
        "institution_type": "Unknown - please review",
        "date_concluded": status_module.get("completionDateStruct", {}).get("date", ""),
        "source_type": "public_database_extraction",
        "source_url": f"https://clinicaltrials.gov/study/{identification.get('nctId', '')}",
        "license": "CC0-1.0",
        "contact_email_optional": "",
        "keywords": ["draft", "needs_review", "clinicaltrials_gov"],
    }


def main():
    parser = argparse.ArgumentParser(description="Pull draft negative-result candidates from ClinicalTrials.gov")
    parser.add_argument("--condition", required=True, help='Condition/disease to search, e.g. "breast cancer"')
    parser.add_argument("--limit", type=int, default=50, help="Max number of studies to fetch")
    parser.add_argument("--out", default="drafts", help="Output folder for draft JSON files")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching up to {args.limit} studies for condition: {args.condition}")
    studies = fetch_studies(args.condition, args.limit)
    print(f"Retrieved {len(studies)} studies.")

    written = 0
    for study in studies:
        entry = to_draft_entry(study)
        status = study.get("protocolSection", {}).get("statusModule", {}).get("overallStatus", "")
        if status not in CANDIDATE_STATUSES:
            continue

        filename = f"{entry['experiment_id']}_draft.json"
        with open(out_dir / filename, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        written += 1

    print(f"\nWrote {written} DRAFT entries to {out_dir}/")
    print("IMPORTANT: These are drafts only. A human must review, classify the correct")
    print("domain, and write a real outcome/methodology summary before merging into data/.")


if __name__ == "__main__":
    main()
