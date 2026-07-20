# Curation Guide (for Maintainers/Reviewers)

This guide is the checklist a curator applies before merging any Pull Request
into `data/`. Its purpose is to keep the registry trustworthy without creating
a bottleneck that discourages contributors.

## Review Checklist

For every incoming submission:

- [ ] **Schema validation passes.** The CI check
      (`validate-submissions.yml`) must be green. If it's red, request changes
      before doing a manual review.
- [ ] **No patient-identifiable information.** Reject immediately (and
      contact the submitter privately) if any field contains names, dates of
      birth, MRNs, or other identifiers.
- [ ] **Outcome is actually negative/null.** Confirm the `outcome` field
      genuinely describes a failed hypothesis, non-significant result, or
      terminated/futile trial — not a positive result submitted by mistake.
- [ ] **Domain classification is correct.** Move the file to the right
      `data/<domain>/` folder if misclassified.
- [ ] **No duplicate entry.** Search existing entries for the same
      `target_disease` + `tested_intervention.name` combination. If a likely
      duplicate exists, ask the submitter to clarify or reference the
      existing entry instead.
- [ ] **Source is checkable, where claimed.** If `source_type` is
      `public_database_extraction` or `literature_mining`, the `source_url`
      should resolve to a real, matching record.
- [ ] **License field is set.** Default to `CC0-1.0` if the submitter didn't
      specify one and didn't object to public domain release.

## Handling Disagreements

If a submission is scientifically contested (e.g. a contributor disputes
whether a result was truly "negative"), don't unilaterally reject — open a
discussion thread on the PR and, where useful, tag a second reviewer with
relevant domain expertise before deciding.

## Batch Imports (e.g. ClinicalTrials.gov extractions)

Entries produced by `scripts/clinicaltrials_seed_extractor.py` are **drafts
only** and must go through the same checklist above, one at a time — no
bulk-merging unreviewed drafts. Mass-imported entries should be flagged with
`"source_type": "public_database_extraction"` so readers know they weren't
independently reviewed by the original researcher.

## Response Time Expectations

Aim to leave an initial response (approve, request changes, or ask a
question) on any data-submission PR within 7 days. If the project grows
beyond what one curator can handle, recruit domain-specific co-reviewers
(see `docs/GOVERNANCE.md`).
