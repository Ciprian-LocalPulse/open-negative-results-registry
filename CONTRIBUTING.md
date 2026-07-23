# Contributing (Developer Guide)

This document is for developers contributing **code, tooling, or infrastructure**.
If you want to contribute a **negative result/data entry** as a clinician or
researcher, see [`docs/HOW_TO_CONTRIBUTE.md`](docs/HOW_TO_CONTRIBUTE.md) instead
— it doesn't require any of the steps below.

## Development Setup

```bash
git clone https://github.com/REPLACE_WITH_ORG/DarkData-Medicine.git
cd DarkData-Medicine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Running the Test Suite

```bash
pytest tests/ -v
```

All Pull Requests must pass the test suite and the schema-validation GitHub
Action (`.github/workflows/validate-submissions.yml`) before being merged.

## Project Conventions

- **Python:** follow PEP 8. Keep scripts dependency-light and runnable
  standalone (`python scripts/<name>.py --help` should always work).
- **Data entries:** must validate against `data/templates/submission_schema.json`.
  Never hand-edit an entry to bypass validation — fix the schema or the data,
  not the check.
- **Commit messages:** use a short imperative summary line
  (`Add validator for ORCID checksum`, not `fixed stuff`).
- **No PII:** never commit patient-identifiable information anywhere in the
  repository, including in test fixtures or example data.

## Areas Where Help Is Wanted

- **Search interface** (`site/`) — currently a static, client-side JSON search.
  Contributions to improve filtering, faceting, or performance are welcome.
- **Literature mining** — tooling to help extract candidate negative results
  from PubMed Central abstracts (see `scripts/clinicaltrials_seed_extractor.py`
  for the equivalent ClinicalTrials.gov pattern).
- **Deduplication** — detecting when two submissions describe the same
  underlying trial.
- **i18n** — translating `docs/HOW_TO_CONTRIBUTE.md` for non-English-speaking
  contributors.

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Make your changes, following the conventions above.
3. Run `pytest tests/` and `python scripts/validate_submission.py data/` locally.
4. Open a Pull Request using the template — describe *what* changed and *why*.
5. A maintainer will review; for data-only PRs, see
   [`docs/CURATION_GUIDE.md`](docs/CURATION_GUIDE.md) for the review checklist
   we apply.

## Versioning

The submission schema is versioned. Breaking changes to
`submission_schema.json` require a version bump and a migration note in
`CHANGELOG.md`, since existing data entries must remain valid or be migrated.
