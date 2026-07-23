# 🧬 Dark Data Medicine — The Open Negative Results Registry

![Dark Data Medicine](assets/dark-data-medicine-banner.png)

> **A free, open, and permanent home for medical "negative results" — the failed
> hypotheses, terminated trials, and null findings that never get published,
> but that could save other researchers years of repeated effort.**

[![License: MIT](https://img.shields.io/badge/code%20license-MIT-blue.svg)](LICENSE)
[![Data License: CC0](https://img.shields.io/badge/data%20license-CC0--1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/HOW_TO_CONTRIBUTE.md)
[![Test Suite](https://img.shields.io/badge/tests-pytest-blue.svg)](tests/)
[![DOI](https://img.shields.io/badge/DOI-pending%20first%20release-lightgrey.svg)](.zenodo.json)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

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
│   ├── immunology/
│   ├── infectious_disease/
│   └── templates/              # Submission template + versioned JSON Schema
│       ├── submission_template.json
│       └── submission_schema.json
│
├── scripts/                    # Free tooling for anyone to use
│   ├── analyze_trends.py             # Which interventions/targets fail most often
│   ├── validate_submission.py        # Validates submissions against the schema
│   ├── export_to_excel.py            # Exports the whole DB to a formatted .xlsx
│   ├── generate_search_index.py      # Builds the JSON index behind site/
│   └── clinicaltrials_seed_extractor.py  # Pulls draft candidates from ClinicalTrials.gov
│
├── tests/                       # pytest suite covering schema + tooling logic
│   ├── test_schema_and_validation.py
│   └── test_analyze_trends.py
│
├── site/                        # Static, client-side search interface (GitHub Pages)
│   ├── index.html
│   └── data_index.json           # Auto-generated — do not hand-edit
│
├── docs/                        # Documentation written for clinicians, not programmers
│   ├── HOW_TO_CONTRIBUTE.md      # No-Git submission path
│   ├── DATA_DICTIONARY.md        # Field-by-field explanation of the schema
│   ├── CURATION_GUIDE.md         # Maintainer/reviewer checklist for merging data
│   └── GOVERNANCE.md             # Decision-making, roles, conflict-of-interest policy
│
├── .github/
│   ├── workflows/
│   │   ├── validate-submissions.yml  # Schema-validates every data PR
│   │   ├── test-suite.yml            # Runs pytest on every PR
│   │   └── deploy-site.yml           # Rebuilds search index + publishes GitHub Pages
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── data_submission.md    # No-code data submission via Issues
│   └── PULL_REQUEST_TEMPLATE.md
│
├── assets/                      # Images used in this README
├── LICENSE                      # MIT (code) — data entries are CC0-1.0 / CC-BY-4.0
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md              # Developer-facing setup, conventions, PR process
├── CHANGELOG.md
├── CITATION.cff                 # Machine-readable citation metadata
├── .zenodo.json                 # DOI metadata for GitHub → Zenodo archiving
├── requirements.txt / requirements-dev.txt
├── FUNDING.md                   # Optional ways to support the maintainer
└── README.md
```

## How to Contribute

**You do not need to know how to use GitHub.**

1. **Non-technical (recommended):** fill out a short form, or open a GitHub
   Issue using the `data_submission.md` template, describing your negative
   result — see [`docs/HOW_TO_CONTRIBUTE.md`](docs/HOW_TO_CONTRIBUTE.md).
   It gets automatically converted and queued for review.
2. **Technical (data):** copy the template at
   [`data/templates/submission_template.json`](data/templates/submission_template.json),
   fill it in, validate it locally with `scripts/validate_submission.py`, and
   open a Pull Request.
3. **Technical (code/tooling):** see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
   dev environment setup, conventions, and the PR process.

Every submission is reviewed by a human curator before being merged into the
public dataset — this keeps the data trustworthy and spam-free.

> **Note on current seed data:** the entries currently in `data/` are
> illustrative placeholder examples (clearly labeled `"illustrative example"`
> in their `keywords`) demonstrating the schema and tooling end-to-end. The
> planned bulk import from ClinicalTrials.gov, the EU Clinical Trials
> Register, and PubMed Central (tracked below) will replace these with real,
> reviewed entries.

## Quickstart

```bash
git clone https://github.com/REPLACE_WITH_ORG/DarkData-Medicine.git
cd DarkData-Medicine
pip install -r requirements.txt -r requirements-dev.txt

# Validate every entry currently in the database
python scripts/validate_submission.py data/

# Run the full test suite
pytest tests/ -v
```

## Using the Data

```bash
# See trends across the whole database
python scripts/analyze_trends.py --top 20

# Export everything to a formatted Excel workbook
python scripts/export_to_excel.py --output DarkData_Export.xlsx

# Validate a submission before opening a PR
python scripts/validate_submission.py data/oncology/my_new_entry.json

# Rebuild the search index that powers site/index.html
python scripts/generate_search_index.py
```

## Searching the Registry

`site/index.html` is a static, dependency-free search interface over the
whole dataset — no backend, no database server. It reads `site/data_index.json`,
which is regenerated automatically on every push to `main` via
`.github/workflows/deploy-site.yml` and published through GitHub Pages.
To browse it locally: run `python scripts/generate_search_index.py`, then
open `site/index.html` in a browser.

## Quality Control

Every incoming submission goes through:

1. **Automated schema validation** (`validate-submissions.yml`) — blocks
   malformed entries before a human ever looks at them.
2. **Human curator review** — see [`docs/CURATION_GUIDE.md`](docs/CURATION_GUIDE.md)
   for the exact checklist applied (duplicate detection, PII screening,
   confirming the result is genuinely negative, source verification).
3. **A full test suite** (`tests/`) protecting the schema and tooling logic
   itself, run on every Pull Request via `test-suite.yml`.

## Governance

This project currently has one founding maintainer, with an explicit path
toward a multi-curator model as it grows. See
[`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) for decision-making process,
conflict-of-interest policy, and how to become a domain curator. See
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) for community standards.

## Citing This Project

Machine-readable citation metadata is provided in
[`CITATION.cff`](CITATION.cff) — GitHub will surface a "Cite this repository"
button automatically. Tagged releases are configured (via
[`.zenodo.json`](.zenodo.json)) to be archived on Zenodo with a permanent DOI
once the repository is connected to a Zenodo account.

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
