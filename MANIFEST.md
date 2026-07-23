# MANIFEST

## Dark Data Medicine — `open-negative-results-registry`

*A Founding Charter*

Version 1.0 — July 2026
Repository: `github.com/Ciprian-LocalPulse/open-negative-results-registry`
Current release: `v1.0.0` — "Initial Academic Release & Core Infrastructure"
License: MIT (code) · CC0-1.0 / CC-BY-4.0 (data)

---

## Preamble

This repository exists to do one specific thing: give a negative or null biomedical result a permanent, structured, freely citable home, at a submission cost measured in minutes rather than months. Everything in this codebase — the schema in `data/templates/`, the validation and curation pipeline described in `docs/CURATION_GUIDE.md`, the ten architecture chapters (`Chapter_2` through `Chapter_10`), the container image published under this repo's Packages tab, the static search site under `site/` — exists in service of that one thing.

This charter is not the technical specification. `DarkData-Medicine_WhitePaper.md` and the numbered Chapter documents already in this repository carry that weight in full — the empirical case for the problem, the architecture, the roadmap, the evidence-quality model. This document states, briefly, what the project is *for* and what it holds itself to, so that a reader arriving at the repository root has something shorter than a hundred-page white paper to orient by before going further.

---

## I. What This Repository Is

`open-negative-results-registry` is a structured, machine-readable database of negative and null findings across seven medical domains — oncology, neurology, pharmacology, cardiology, psychiatry, immunology, and infectious disease — validated against a versioned JSON Schema, curated by a named human reviewer before merge, and released under CC0-1.0 or CC-BY-4.0 at the contributor's choice.

As of this release, the repository ships:

- A working validation, analysis, export, and search-index pipeline (`scripts/`), each independently exercised by the test suite in `tests/` and by continuous integration on every pull request (`.github/workflows/`).
- A no-code contribution pathway for clinicians and researchers who have never used Git, documented in `docs/HOW_TO_CONTRIBUTE.md` and `.github/ISSUE_TEMPLATE/data_submission.md`.
- A containerized build of the toolkit, published to this repository's Packages registry, so the CLI can be run without a local Python environment.
- Ten architecture chapters (`Chapter_2_Architectural_Vision.md` through `Chapter_10_Developer_Guide.md`) and a full academic white paper, documenting the system end to end at a level of detail this charter deliberately does not repeat.
- Seven seed entries, one per domain, explicitly labeled as illustrative examples rather than reviewed real-world submissions — the honest current state of the dataset, pending the bulk import from ClinicalTrials.gov, the EU Clinical Trials Register, and PubMed Central tracked in the Roadmap section of the README.

---

## II. First Principles

**1. Free by default.** No paywall stands between a reader and the data. No account is required to browse it. Code is MIT licensed without exception; data is CC0-1.0 or CC-BY-4.0, chosen per entry by the contributor.

**2. Structured, not narrative.** An entry that cannot be filtered by intervention, disease target, or institution type is functionally still dark, no matter how honestly it was written down. Every entry in `data/` conforms to `data/templates/submission_schema.json`, checked automatically before any human ever reviews it.

**3. Radically low contribution cost.** The registry is built around the assumption that the deciding factor in whether a negative result gets disclosed is not its importance but the effort required to disclose it. A non-technical contributor uses a form; a technical contributor copies a template and opens a pull request. Neither writes a manuscript.

**4. Human curation, not unmoderated crowdsourcing.** Every entry — plain-language form or direct submission alike — passes automated schema validation and then a named curator, per the checklist in `docs/CURATION_GUIDE.md`, before it reaches the public dataset.

**5. Independence, as a hard rule.** `docs/GOVERNANCE.md` states plainly that no funder, sponsor, or donor has any influence over which entries are accepted, rejected, or featured. `FUNDING.md` accepts optional support for the maintainer on exactly that condition and no other.

---

## III. What This Repository Is Not

It is not a substitute for ClinicalTrials.gov, the EU Clinical Trials Register, or any statutory results-reporting regime — those systems have legal authority this project does not seek. It is not a systematic-review protocol registry in the manner of PROSPERO. It does not host full manuscripts or raw datasets in the manner of the Open Science Framework. And an entry here is not peer-reviewed evidence; it is a curated, sourced lead, and the project's own documentation says so without hedging.

---

## IV. Current State and Governance

This project is presently maintained by a single founding maintainer, with an explicit, documented path toward a multi-curator model as the dataset grows past what one reviewer can hold to the seven-day response target described in `docs/GOVERNANCE.md`. Schema changes require a written rationale and a migration plan. New domain categories are added on demonstrated need. Curators disclose conflicts of interest in the review thread rather than recusing silently. None of this is aspirational language — it is the literal process this repository's pull-request history is built to make auditable.

---

## V. A Note on the Esoteric-Language Artifacts

This repository, like others in this account, includes small companion artifacts written in deliberately obscure programming languages alongside this charter: `MANIFEST.mb` (Malbolge) and `DARKDATA.bf` (Brainfuck). `MALBOLGE_ARTIFACT.md` and `BRAINFUCK_ARTIFACT.md` document exactly what each one is, why it is here, and how it was independently verified — in full, so that nothing about either has to be taken on faith. Neither is a translation of this manifest; no classical Malbolge program can be, and encoding this document's actual prose in Brainfuck would produce a program too large to be a meaningful artifact rather than a curiosity. Both are symbolic gestures, not technical claims, and this document does not dwell on them further than that.

---

## VI. Ratification

This charter binds the maintainer and curators of `open-negative-results-registry` to the five principles in Part II for as long as the project operates under this name. Amendments to this charter follow the same public, auditable process as any other change to this repository — a proposal, a rationale, a review visible in the commit history. No signature closes a document meant to keep being read; its authority rests on being followed.

---

*Dark Data Medicine — an open registry for the evidence that would otherwise disappear.*
*Code: MIT. Data: CC0-1.0 / CC-BY-4.0. Release: v1.0.0.*
