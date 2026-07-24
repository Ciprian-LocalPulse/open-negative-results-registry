# Data Ingestion Pipeline (Level 1)

This document describes the automated pipeline that sources candidate negative-result entries at scale, so the dataset can grow beyond the seven illustrative seed entries in `data/` today. It has two components, covering two different, complementary sources of dark data.

## 1. ClinicalTrials.gov structured ingestion

**What it does:** `scripts/clinicaltrials_ingest.py` queries the public ClinicalTrials.gov API v2 (`https://clinicaltrials.gov/api/v2/studies`, no key required), scores each returned trial for how likely its status represents a genuine negative or null result, auto-classifies it into this registry's domain vocabulary where the mapping is confident, and writes a schema-valid draft file.

**Confidence scoring:** trial status is not, on its own, proof of a negative result. A `TERMINATED` or `WITHDRAWN` trial with a scientific reason given (e.g., "Sponsor Hold" pending unfavorable interim data) is a strong signal; the same status with an administrative reason (funding lapse, slow recruitment) is not a scientific finding at all, and the script downgrades its confidence accordingly rather than treating every non-completed trial as equally informative. `COMPLETED` trials are included but always flagged `confidence_low`, because most completed trials are positive — a curator still has to open the actual results section to check.

**Automated scheduling:** `.github/workflows/scheduled-ingestion.yml` runs the pipeline weekly (Sunday 03:00 UTC, an off-peak window) across one seed condition per registry domain, and opens a Pull Request with the results — it never pushes to `main` and never auto-merges. This is a direct, mechanical enforcement of the rule already stated in `docs/CURATION_GUIDE.md`: batch imports are drafts, not verified data, full stop.

**What was and wasn't tested before this was written:**

- The field-parsing, confidence-scoring, and domain-classification logic was tested against a **real** ClinicalTrials.gov v2 API response, captured live and included as a test fixture (`tests/fixtures/real_ctgov_sample.json`), and every entry it produces was validated against the repository's actual `data/templates/submission_schema.json` — 11/11 tests pass (`tests/test_clinicaltrials_ingest.py`).
- The **live, filtered, scheduled query itself** (i.e., the weekly cron job actually running against the API with `query.cond` filters applied) could not be end-to-end tested in the environment this was built in, because that environment's tooling stripped URL query parameters before requests were sent — a limitation of the *build* environment, not of the delivered code, which uses the standard `requests` library and will send query parameters normally when it actually runs in GitHub Actions. This should still be watched on its first live run.

## 2. PubMed negative-language screening

**What it does:** `scripts/pubmed_negative_language_classifier.py` is a pattern-based screening tool for abstract conclusion text, designed to catch a different and complementary category of dark data: results that **were** published, but whose negative finding is a secondary or tertiary outcome buried in the text of an otherwise positive-sounding abstract — exactly the kind of finding a registry status field (Section 1, above) can never surface, because the trial itself shows as `COMPLETED` with no hint that anything in it was negative.

**Why it's a screening tool, not a classifier making final calls:** the pattern set was built from established conventions in how RCT conclusion sentences are phrased in the evidence-based-medicine literature, not fitted to a labeled corpus of real abstracts, because live PubMed/E-utilities access was unavailable when this was built (same tooling limitation as above). It is deliberately tuned for high recall over high precision — it is designed to over-flag rather than risk silently missing a real negative finding, on the theory that a curator spending thirty extra seconds dismissing a false positive is a much smaller cost than a true negative result never being seen by anyone.

**Known, documented limitation:** the classifier cannot currently distinguish a null *outcome* result ("the treatment groups did not differ on the primary endpoint") from a null *baseline-balance* statement ("the treatment groups did not differ on baseline characteristics, confirming successful randomization") — both are extremely common, near-identical sentence structures in RCT abstracts, and telling them apart requires knowing which part of the abstract a sentence comes from, which this tool does not currently track. This is captured directly in the test suite (`test_does_not_false_trigger_on_unrelated_negation`) rather than hidden. A curator using this tool's output should expect this specific false-positive pattern and check for it.

**Test suite:** 10/10 tests pass (`tests/test_pubmed_negative_language_classifier.py`), using hand-written synthetic sentences styled on real abstract conventions rather than reproductions of actual copyrighted text.

## What Level 1 does not yet include

Consistent with the roadmap discussion in `MANIFEST.md` and the white paper's Part IV sequencing logic: a bulk institutional submission API, an EU CTIS / WHO ICTRP connector, and a trained (rather than rule-based) NLP classifier are all reasonable next steps beyond this initial ingestion layer, but are not included here. Building them against a dataset of seven illustrative entries would risk over-fitting their design to examples that were never meant to be representative — the same sequencing argument the white paper already makes about the knowledge-graph and ontology proposals in Part IV.
