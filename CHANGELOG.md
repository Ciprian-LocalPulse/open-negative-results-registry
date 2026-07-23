# Changelog

All notable changes to this project are documented in this file.
This project follows [Semantic Versioning](https://semver.org/) for its
submission schema (`data/templates/submission_schema.json`).

## [0.1.0] — Initial Release

### Added
- Core repository structure: `data/`, `scripts/`, `docs/`, `site/`, `tests/`
- Submission schema v1 (`submission_schema.json`) covering domain, disease
  target, intervention, hypothesis, outcome, methodology, ORCID, institution
  type, license, and provenance fields
- Validation tooling (`validate_submission.py`) with CI integration via
  GitHub Actions
- Trend analysis tooling (`analyze_trends.py`)
- Excel export tooling (`export_to_excel.py`)
- ClinicalTrials.gov draft-seeding tool (`clinicaltrials_seed_extractor.py`)
- Static client-side search interface (`site/`) for GitHub Pages
- Full test suite (`tests/`) covering schema validity and summarization logic
- Governance, Code of Conduct, Contributing, and Curation Guide documents
- CITATION.cff and .zenodo.json for DOI-backed academic citation
- Illustrative seed entries across Oncology, Neurology, Pharmacology,
  Cardiology, Psychiatry, Immunology, and Infectious Disease domains

### Notes
- Illustrative seed entries included in this release are placeholders
  demonstrating the schema and are marked as such — they are not a
  substitute for the planned bulk import from public trial registries
  (tracked in the README roadmap).
