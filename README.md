# 🧬 Dark Data Medicine — The Open Negative Results Registry

![Dark Data Medicine](assets/dark-data-medicine-banner.png)

> **A free, open, and permanent home for medical "negative results" — the failed
> hypotheses, terminated trials, and null findings that never get published,
> but that could save other researchers years of repeated effort.**

[![License: MIT](https://img.shields.io/badge/code%20license-MIT-blue.svg)](LICENSE)
[![Data License: CC0](https://img.shields.io/badge/data%20license-CC0--1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/HOW_TO_CONTRIBUTE.md)

---

## The Problem

An estimated majority of clinical and preclinical study results are never
published — mostly because they're negative. A drug that didn't work, a
molecule that showed no effect, a hypothesis that wasn't confirmed. This
creates **publication bias**: other labs unknowingly repeat the same failed
experiments, wasting time, funding, and — in clinical contexts — potentially
exposing patients to interventions already shown not to work elsewhere.

This "dark data" is a massive, invisible, and recoverable resource.

## The Solution

This repository is a structured, open, and free database of negative and null
results across medicine and the life sciences. It is:

- **Free** — no paywall, no account required to read the data
- **Structured** — every entry follows a strict JSON schema, so it's machine-readable
- **Citable** — periodic data releases get a DOI via Zenodo
- **Open to everyone** — from a single independent researcher to a full hospital lab
- **Non-technical-friendly** — you don't need to know Git to contribute (see below)

## Repository Structure

```
DarkData-Medicine/
│
├── data/                       # The actual negative-result entries, by domain
│   ├── oncology/
│   ├── neurology/
│   ├── pharmacology/
│   ├── cardiology/
│   ├── psychiatry/
│   └── templates/              # Submission template + JSON Schema
│       ├── submission_template.json
│       └── submission_schema.json
│
├── scripts/                    # Free tooling for anyone to use
│   ├── analyze_trends.py           # Which interventions/targets fail most often
│   ├── validate_submission.py      # Validates a submission against the schema
│   ├── export_to_excel.py          # Exports the whole DB to a formatted .xlsx
│   └── clinicaltrials_seed_extractor.py  # Pulls draft candidates from ClinicalTrials.gov
│
├── docs/                       # Documentation written for clinicians, not programmers
│   ├── HOW_TO_CONTRIBUTE.md
│   └── DATA_DICTIONARY.md
│
├── .github/workflows/          # Automated validation of every new submission
├── assets/                     # Images used in this README
├── LICENSE                     # MIT (code) — data entries are CC0-1.0 / CC-BY-4.0
├── FUNDING.md                  # Optional ways to support the maintainer
└── README.md
```

## How to Contribute

**You do not need to know how to use GitHub.**

1. **Non-technical (recommended):** fill out a short form describing your
   negative result — see [`docs/HOW_TO_CONTRIBUTE.md`](docs/HOW_TO_CONTRIBUTE.md).
   It gets automatically converted and queued for review.
2. **Technical:** copy the template at
   [`data/templates/submission_template.json`](data/templates/submission_template.json),
   fill it in, validate it locally with `scripts/validate_submission.py`, and
   open a Pull Request.

Every submission is reviewed by a human curator before being merged into the
public dataset — this keeps the data trustworthy and spam-free.

## Using the Data

```bash
# See trends across the whole database
python scripts/analyze_trends.py --top 20

# Export everything to a formatted Excel workbook
python scripts/export_to_excel.py --output DarkData_Export.xlsx

# Validate a submission before opening a PR
python scripts/validate_submission.py data/oncology/my_new_entry.json
```

## Data Licensing & Attribution

- **Code** in this repository (scripts, tooling, website) is MIT licensed.
- **Data entries** are released individually under CC0-1.0 (public domain) or
  CC-BY-4.0 (attribution required), as specified in each entry's `license` field.
- Contributors who provide an ORCID iD are credited, and periodic dataset
  snapshots receive a Zenodo DOI so contributions can be formally cited.

## Roadmap

- [ ] Seed the database with the first 500–1,000 entries mined from public
      registries (ClinicalTrials.gov, EU CTR, PubMed Central)
- [ ] Publish a searchable web interface via GitHub Pages
- [ ] Set up the no-code submission form + automation pipeline
- [ ] First Zenodo-archived data release with an official DOI
- [ ] Outreach to university labs, PLOS One / F1000Research / PeerJ communities

## Supporting This Project

This project is maintained independently and is entirely free to use. If you'd
like to help keep it running, see [`FUNDING.md`](FUNDING.md) — though starring
the repo, contributing data, or simply sharing it with colleagues is just as
valuable and always free.

## License

Code: [MIT](LICENSE). Data: see individual entries (CC0-1.0 / CC-BY-4.0).
