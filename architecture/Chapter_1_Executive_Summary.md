# Chapter 1: Executive Summary

*Part of the Dark Data Medicine architecture documentation series (Chapters 1–10).*
*Companion to `DarkData-Medicine_WhitePaper.md`, `MANIFEST.md`, and `Chapter_2_Architectural_Vision.md` through `Chapter_10_Developer_Guide.md`.*

---

## 1.1 What This System Is

Dark Data Medicine (`open-negative-results-registry`) is an open-source, freely licensed registry for negative and null results in biomedical research — findings where a tested intervention did not outperform its comparator, or where a study found no measurable effect in either direction. It exists to give this class of finding a permanent, structured, citable home outside the traditional journal-publication pathway, at a contribution cost measured in minutes rather than months.

The system consists of five parts, each documented in depth in a later chapter:

| Component | Purpose | Documented in |
|---|---|---|
| Data schema | Versioned JSON Schema defining what a valid entry contains | Chapter 5, Chapter 6 |
| Contribution pathways | No-code form and Git-based template for submitting entries | Chapter 4, `docs/HOW_TO_CONTRIBUTE.md` |
| Curation pipeline | Automated validation + human review before publication | Chapter 4, `docs/CURATION_GUIDE.md` |
| Search & analysis tooling | Static search site, trend analysis, Excel export | Chapter 3, Chapter 4 |
| Governance & sustainability | Decision rights, conflict-of-interest policy, funding independence | `docs/GOVERNANCE.md`, `FUNDING.md` |

## 1.2 The Problem in One Paragraph

A substantial share of biomedical research — commonly estimated between one quarter and one half of completed clinical trials, and over half of preclinical work — is never published, largely because negative and null results are systematically less likely to be written up, accepted, or found than positive ones. This is not primarily a story of misconduct; it is a structural property of a publication system built around a single unit of output; the positive, novel, statistically significant paper. The consequence is measurable: redundant experiments repeated by researchers with no way of knowing the question had already been answered, trial participants enrolled in studies whose outcome was already known elsewhere, and, by independent economic analysis, tens of billions of dollars a year in the United States alone attributable to irreproducible or unreported preclinical work. The full empirical case, with citations, is developed in `DarkData-Medicine_WhitePaper.md` Part I; this chapter assumes it and moves directly to the system built in response.

## 1.3 Design Philosophy in One Paragraph

Every architectural decision in this repository follows from a single premise: the deciding factor in whether a negative result gets disclosed is not its scientific importance but the effort required to disclose it. Existing infrastructure — clinical trial registries, statutory reporting mandates, systematic-review protocol registries — either requires formal trial-registry status as a precondition for inclusion, or requires something close to full manuscript preparation. This system is deliberately scoped to the layer those systems do not reach: preclinical, translational, and small-laboratory findings, submitted through a pathway a non-technical contributor can complete in the time it takes to fill out a form.

## 1.4 Current State (v1.0.0)

As of the `v1.0.0` release:

- The validation, curation, analysis, export, and search-index pipeline is fully built and covered by automated tests (`tests/`), run on every pull request via GitHub Actions (`.github/workflows/`).
- The dataset contains seven seed entries, one per populated domain (oncology, neurology, pharmacology, cardiology, psychiatry, immunology, infectious disease), explicitly labeled as illustrative examples rather than reviewed real-world submissions — see Chapter 5 for the full data model and the Roadmap section of `README.md` for the path to the first bulk import.
- The toolkit is published as a container image under this repository's Packages registry (see `Dockerfile`, `docker-entrypoint.sh`), so the CLI can be run without a local Python environment.
- Governance currently rests with a single founding maintainer, with an explicit, documented path toward a multi-curator model described in `docs/GOVERNANCE.md`.

## 1.5 How to Use This Documentation Set

Read in the order that matches what you need:

- **I want the evidence for why this matters** → `DarkData-Medicine_WhitePaper.md`, Part I.
- **I want the five-minute version of what this project stands for** → `MANIFEST.md`.
- **I want to understand the system design** → this chapter, then Chapter 2 through Chapter 10 in order.
- **I want to contribute a negative result** → `docs/HOW_TO_CONTRIBUTE.md`.
- **I want to run the code** → `README.md` Quickstart section, or `examples/` for worked analysis code.
- **I want to know who decides what gets published here** → `docs/GOVERNANCE.md`.

## 1.6 Scope of This Chapter

This chapter is deliberately short. It exists to close the gap between `README.md` — necessarily terse — and Chapter 2's architectural detail, and to make sure a first-time reader lands somewhere before being asked to absorb ten chapters of specification. Everything asserted here is expanded, with detail and citations, in the chapters and documents it links to.
