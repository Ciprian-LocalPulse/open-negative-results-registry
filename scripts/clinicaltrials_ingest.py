#!/usr/bin/env python3
"""
clinicaltrials_ingest.py

Level-1 data-ingestion pipeline: pulls candidate negative-result
entries from the public ClinicalTrials.gov API v2 at scale, scores
each one for how likely it is to represent a genuine negative or null
result, and auto-classifies it into one of this registry's domain
categories where the mapping is confident enough to trust.

This is an evolution of clinicaltrials_seed_extractor.py, not a
replacement -- it keeps the same output schema and the same hard rule
from docs/CURATION_GUIDE.md ("Batch imports are treated as drafts,
never as verified data"): everything this script produces still goes
into a drafts/ folder, still requires one-at-a-time human curator
review, and is never bulk-merged automatically.

Usage:
    python clinicaltrials_ingest.py --condition "breast cancer" --limit 100 --out drafts/
    python clinicaltrials_ingest.py --domain-sweep --limit 50 --out drafts/
        (runs one search per registry domain, using the seed terms in
        DOMAIN_SEED_CONDITIONS below -- this is what the scheduled
        GitHub Actions workflow calls)

Requires:
    pip install requests
"""

import argparse
import json
import re
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency. Install with: pip install requests --break-system-packages")
    raise SystemExit(1)

API_URL = "https://clinicaltrials.gov/api/v2/studies"

# Trial statuses ordered by how strong a negative-result signal they
# represent on their own, without needing the results section.
# TERMINATED / WITHDRAWN / SUSPENDED are the strongest signal available
# from status alone: something stopped the trial before it produced the
# result it set out to produce, and "whyStopped" (when present) usually
# says why. COMPLETED trials are weaker signal in isolation -- most
# completed trials are positive -- so they are included but scored
# lower, and flagged for the curator to check the results section
# manually rather than assumed negative.
STATUS_CONFIDENCE = {
    "TERMINATED": "high",
    "WITHDRAWN": "high",
    "SUSPENDED": "medium",
    "COMPLETED": "low",   # needs manual results-section check
}

# Maps ClinicalTrials.gov condition/MeSH-style free text to this
# registry's controlled domain vocabulary (data/templates/submission_schema.json).
# Deliberately conservative: a condition only maps if a keyword match
# is specific enough to be trustworthy without a human looking at it.
# Anything that doesn't match stays "Unclassified - please review"
# rather than being guessed into the wrong bucket, because a wrong
# auto-classification costs the curator MORE time to catch and fix
# than an honest "I don't know" would.
DOMAIN_KEYWORDS = {
    "Oncology": ["cancer", "carcinoma", "tumor", "tumour", "neoplasm", "leukemia",
                 "lymphoma", "melanoma", "sarcoma", "oncology"],
    "Neurology": ["alzheimer", "parkinson", "epilepsy", "stroke", "migraine",
                  "multiple sclerosis", "neuropathy", "dementia"],
    "Pharmacology": ["pharmacokinetic", "drug interaction", "dose-finding",
                      "bioavailability"],
    "Cardiology": ["heart failure", "myocardial", "cardiac", "coronary",
                   "arrhythmia", "hypertension", "atrial fibrillation"],
    "Psychiatry": ["depress", "anxiety", "schizophrenia", "bipolar",
                   "psychiatric", "ptsd", "mental health"],
    "Immunology": ["autoimmune", "rheumatoid arthritis", "lupus", "psoriasis",
                   "immunology", "allergy", "immunodeficiency"],
    "Infectious Disease": ["tuberculosis", "hiv", "hepatitis", "malaria",
                            "sepsis", "covid", "influenza", "bacterial infection",
                            "viral infection"],
    "Endocrinology": ["diabetes", "thyroid", "obesity", "endocrine",
                       "hormone"],
}


def classify_domain(conditions: list) -> tuple:
    """Returns (domain, was_confident). Falls back to the valid enum
    value 'Other' rather than an invalid placeholder string when no
    keyword match is found -- the schema's domain field is a strict
    enum (data/templates/submission_schema.json) and a draft that
    fails validation never even reaches a curator's queue.

    Multi-word keywords (e.g. "rheumatoid arthritis") match as long as
    every word in the phrase appears somewhere in the condition text,
    regardless of order or adjacency. This is deliberate: ClinicalTrials.gov
    condition strings frequently use inverted MeSH-style phrasing, e.g.
    "Arthritis, Rheumatoid" or "Diabetes Mellitus, Type 2" instead of the
    natural word order -- a plain substring check on "rheumatoid arthritis"
    silently misses these and dumps real, classifiable data into "Other".
    """
    text = " ".join(conditions).lower()
    words_in_text = set(re.findall(r"[a-z]+", text))
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            kw_words = kw.replace("-", " ").split()
            if len(kw_words) == 1:
                if kw in text:
                    return domain, True
            elif all(w in words_in_text for w in kw_words):
                return domain, True
    return "Other", False


def score_confidence(study: dict) -> tuple:
    """Return (confidence_label, reason_string) for how likely this
    study is to be a genuine, usable negative-result candidate."""
    status_module = study.get("protocolSection", {}).get("statusModule", {})
    status = status_module.get("overallStatus", "")
    why_stopped = status_module.get("whyStopped", "")

    confidence = STATUS_CONFIDENCE.get(status, "very_low")
    reason = f"Status: {status}."
    if why_stopped:
        reason += f" Reason given: {why_stopped!r}."
        # A small number of "whyStopped" reasons are administrative,
        # not scientific -- e.g. funding lapses, not a finding about
        # the intervention. Downgrade confidence when detected, so the
        # curator isn't misled into thinking there's a result to write up.
        admin_patterns = r"(fund|budget|business decision|company decision|" \
                          r"lack of enrollment|slow accrual|recruitment)"
        if re.search(admin_patterns, why_stopped, re.IGNORECASE):
            confidence = "low"
            reason += " (Downgraded: reason appears administrative, not scientific.)"
    if status == "COMPLETED":
        reason += " Completed trials require manual results-section review " \
                  "before assuming a negative outcome -- see docs/CURATION_GUIDE.md."
    return confidence, reason


def fetch_studies(condition: str, limit: int) -> list:
    results = []
    page_token = None
    page_size = min(limit, 100)

    while len(results) < limit:
        params = {"query.cond": condition, "pageSize": page_size, "format": "json"}
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
        time.sleep(0.5)  # polite to the public API

    return results[:limit]


def to_draft_entry(study: dict) -> dict:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    arms_module = protocol.get("armsInterventionsModule", {})
    design_module = protocol.get("designModule", {})
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})

    interventions = arms_module.get("interventions", [])
    intervention_name = interventions[0].get("name") if interventions else "Unknown"
    intervention_type = interventions[0].get("type", "Other").title() if interventions else "Other"
    if intervention_type not in ("Molecule", "Drug", "Biologic", "Device",
                                  "Behavioral", "Procedure", "Other"):
        intervention_type = "Other"

    conditions = conditions_module.get("conditions", ["Unknown"])
    confidence, reason = score_confidence(study)
    domain, domain_confident = classify_domain(conditions)

    lead_sponsor_class = sponsor_module.get("leadSponsor", {}).get("class", "")
    institution_map = {
        "INDUSTRY": "Pharmaceutical Company",
        "OTHER_GOV": "Government Institute",
        "NIH": "Government Institute",
        "FED": "Government Institute",
    }
    # Falls back to the valid enum value "Other" rather than an
    # invalid placeholder -- same reasoning as classify_domain() above.
    institution_type = institution_map.get(lead_sponsor_class, "Other")
    institution_confident = lead_sponsor_class in institution_map

    review_flags = ["draft", "needs_review", "clinicaltrials_gov",
                     f"confidence_{confidence}"]
    if not domain_confident:
        review_flags.append("domain_unconfirmed")
    if not institution_confident:
        review_flags.append("institution_unconfirmed")

    return {
        "experiment_id": identification.get("nctId", "UNKNOWN"),
        "domain": domain,
        "target_disease": ", ".join(conditions),
        "tested_intervention": {
            "type": intervention_type,
            "name": intervention_name,
            "dosage": "See ClinicalTrials.gov record",
        },
        "hypothesis": "DRAFT - fill in based on study record.",
        "outcome": f"Trial status: {status_module.get('overallStatus', 'Unknown')}. "
                   f"{reason} Human curator must confirm whether this represents "
                   f"a genuine negative/null result before merging."
                   + ("" if domain_confident else " NOTE: domain auto-classification "
                      "was not confident -- verify before merging."),
        "methodology_summary": design_module.get("studyType", "Unknown study design"),
        "researcher_orcid": "0000-0000-0000-0000",
        "institution_type": institution_type,
        "date_concluded": status_module.get("completionDateStruct", {}).get("date", ""),
        "source_type": "public_database_extraction",
        "source_url": f"https://clinicaltrials.gov/study/{identification.get('nctId', '')}",
        "license": "CC0-1.0",
        "contact_email_optional": "",
        "keywords": review_flags,
        "_ingest_confidence": confidence,   # internal field, stripped before final merge
    }


DOMAIN_SEED_CONDITIONS = {
    "Oncology": "cancer",
    "Neurology": "alzheimer disease",
    "Pharmacology": "pharmacokinetics",
    "Cardiology": "heart failure",
    "Psychiatry": "major depressive disorder",
    "Immunology": "rheumatoid arthritis",
    "Infectious Disease": "tuberculosis",
    "Endocrinology": "type 2 diabetes",
}


def run_for_condition(condition: str, limit: int, out_dir: Path) -> dict:
    print(f"Fetching up to {limit} studies for condition: {condition}")
    studies = fetch_studies(condition, limit)
    print(f"Retrieved {len(studies)} studies.")

    counts = {"high": 0, "medium": 0, "low": 0, "very_low": 0}
    written = 0
    for study in studies:
        entry = to_draft_entry(study)
        confidence = entry.pop("_ingest_confidence")
        counts[confidence] = counts.get(confidence, 0) + 1

        # Only write drafts with at least "low" confidence -- "very_low"
        # (e.g. RECRUITING, ACTIVE_NOT_RECRUITING, NOT_YET_RECRUITING)
        # means the trial hasn't concluded and has no negative-result
        # signal to offer yet.
        if confidence == "very_low":
            continue

        filename = f"{entry['experiment_id']}_draft.json"
        with open(out_dir / filename, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        written += 1

    return {"condition": condition, "retrieved": len(studies),
            "written": written, "by_confidence": counts}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--condition", help='Single condition to search, e.g. "breast cancer"')
    ap.add_argument("--domain-sweep", action="store_true",
                     help="Run one search per registry domain using built-in seed terms")
    ap.add_argument("--limit", type=int, default=50, help="Max studies per condition")
    ap.add_argument("--out", default="drafts", help="Output folder for draft JSON files")
    args = ap.parse_args()

    if not args.condition and not args.domain_sweep:
        ap.error("Provide --condition \"...\" or --domain-sweep")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    if args.domain_sweep:
        for domain, seed_condition in DOMAIN_SEED_CONDITIONS.items():
            report = run_for_condition(seed_condition, args.limit, out_dir)
            report["target_domain"] = domain
            reports.append(report)
    else:
        reports.append(run_for_condition(args.condition, args.limit, out_dir))

    print("\n=== Ingestion summary ===")
    total_written = 0
    for r in reports:
        print(f"  {r['condition']:30s} retrieved={r['retrieved']:4d}  "
              f"written={r['written']:4d}  by_confidence={r['by_confidence']}")
        total_written += r["written"]
    print(f"\nTotal drafts written: {total_written} -> {out_dir}/")
    print("IMPORTANT: every file here is a DRAFT. Per docs/CURATION_GUIDE.md, a human")
    print("curator must review each one individually -- confirm domain classification,")
    print("write a real hypothesis/outcome/methodology summary, and check the results")
    print("section for COMPLETED trials -- before any of these are merged into data/.")
    print("Files are tagged confidence_high / confidence_medium / confidence_low in")
    print("their keywords field so curators can triage by priority.")


if __name__ == "__main__":
    main()

# trigger CI re-run
