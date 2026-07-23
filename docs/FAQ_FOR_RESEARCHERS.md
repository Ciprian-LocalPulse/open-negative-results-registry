# Frequently Asked Questions

## For researchers using the data

**Is this peer-reviewed?**
No. Entries pass automated schema validation and human curator review (`docs/CURATION_GUIDE.md`) for completeness, plausibility, and absence of identifiable patient information — not methodological peer review. Treat an entry as a curated, sourced lead worth following up against its original source, not as citation-equivalent to a reviewed publication.

**Can I use this data in a systematic review or meta-analysis?**
Yes, subject to the point above. Check the `source_type` field on each entry: `original_submission` entries have been directly reviewed by a curator against the submitter's own account; `public_database_extraction` entries are drafts mined from a public registry and flagged as such (`docs/CURATION_GUIDE.md`, "Batch imports"); `literature_mining` entries derive from published text. Weight accordingly.

**How current is the dataset?**
As of `v1.0.0`, the dataset contains seven seed entries — one per populated domain — explicitly labeled `"illustrative example"` in their `keywords` field. They demonstrate the schema and tooling, not a populated evidence base. See the Roadmap section of `README.md` for the planned bulk import from ClinicalTrials.gov, the EU Clinical Trials Register, and PubMed Central.

**How do I query the data programmatically?**
The dataset is plain JSON files under `data/<domain>/`, one file per entry, conforming to `data/templates/submission_schema.json`. No API or database is required — see `examples/analyze_with_pandas.py` for a worked example, or `scripts/analyze_trends.py --top 20` for aggregate statistics from the command line.

**Does this replace ClinicalTrials.gov or PROSPERO?**
No. See `MANIFEST.md` §III for what this project explicitly does and does not attempt to replace.

## For contributors

**I don't use Git. Can I still contribute?**
Yes — that pathway is the primary intended one. See `docs/HOW_TO_CONTRIBUTE.md` for the plain-language form / GitHub Issue template pathway. You never need to touch a command line.

**How long does review take?**
Curators aim to leave an initial response — approval, requested changes, or a clarifying question — within seven days of submission (`docs/GOVERNANCE.md`).

**Will submitting here stop me from publishing the same result in a journal later?**
This depends on the specific journal's policy on prior data-repository deposition, and we cannot make a blanket guarantee. Because entries are brief, structured, factual records rather than full manuscripts, many journals treat this differently from full-text prior publication — similar to how preprints and trial-registry result postings are commonly treated — but check your target journal's policy before submitting if this matters to you.

**Can I submit a positive result?**
No — the schema and curation checklist are built specifically for negative and null findings. A curator receiving a positive-outcome submission will redirect you toward conventional publication or a preprint server instead.

**What happens if my result is disputed as not genuinely negative?**
The curator opens a discussion thread on the pull request or issue rather than unilaterally rejecting it, and may bring in a second reviewer with relevant domain expertise (`docs/CURATION_GUIDE.md`, "Handling contested submissions").

## For developers

**How do I run the full pipeline locally?**
See the Quickstart section of `README.md`, or run `make help` for a summary of available commands (`make install`, `make test`, `make validate`, `make analyze`, `make export`, `make docker-build`).

**How do I add a new domain (e.g. Endocrinology)?**
Per `docs/GOVERNANCE.md`, new domain categories are added on demonstrated need — operationalized as five or more pending submissions that don't fit an existing category. Propose it via issue or pull request with that justification.

**Is there an API?**
Not yet in this release; the current interface is the static search site (`site/index.html`) and direct file/tooling access. See `Chapter_7_API_Specification.md` for the planned interface design.

**How is data licensed, exactly?**
Code (scripts, tooling, site) is MIT licensed throughout. Each data entry carries its own `license` field, set to either `CC0-1.0` (public domain) or `CC-BY-4.0` (attribution required) by the contributor at submission time — see `data/templates/submission_schema.json`.

## Still have a question?

Open a GitHub Issue using the appropriate template under `.github/ISSUE_TEMPLATE/`, or see `CONTRIBUTING.md` for the developer-facing contact path.
