# Dark Data Medicine — Platform Architecture Series

## Chapter 10: Developer Guide

*Document status: Practical / Operational. Assumes familiarity with Chapters 2–9 at a reference level, not a read-through requirement — this chapter is written so a new engineer can be productive in their first week and consult the earlier chapters as specific questions arise, rather than needing to read the full series before writing a line of code.*

*Version 0.1 — Draft for governance review*

---

### 10.0  Who This Chapter Is For

This chapter is for an engineer joining the project to write code — implementing a `PLANNED` service from Chapter 4, extending the `OPERATIONAL` validation tooling, or building toward the target architecture specified in Chapters 3, 7, 8, and 9. It is not for a researcher wanting to contribute a negative-result entry (that path is `docs/HOW_TO_CONTRIBUTE.md`, referenced in §10.3.1) and not for an operator running the platform day to day (that is the Operations Manual, the next document in this series).

**A promise this chapter makes and keeps.** Every command below has actually been run against the live repository as this chapter was written. Nothing in this chapter describes a workflow for infrastructure that does not yet exist — where a `PLANNED` or `FUTURE` component from earlier chapters is relevant, this chapter says so explicitly and describes today's real substitute instead.

---

### 10.1  Prerequisites and Environment Setup

**Today's actual stack (`OPERATIONAL`).**

| Requirement | Version / Notes |
|---|---|
| Python | 3.10+ |
| Git | Any recent version |
| `pip` | For installing `jsonschema`, `pytest`, and the other tooling dependencies |
| GitHub account | For opening pull requests; no special permissions needed to contribute |

**First-time setup.**
```bash
git clone https://github.com/Ciprian-LocalPulse/DarkData-Medicine.git
cd DarkData-Medicine
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # jsonschema, pytest, and current tooling deps
pytest tests/                    # confirm a clean baseline before making changes
```

**Target-state setup (`PLANNED`, once containerized services from Chapter 9 §9.2.2 exist).** A `docker-compose up` bringing up a local API Gateway, PostgreSQL, and the containerized services under active development, with hot-reload for local iteration. Until that exists, local development is script-and-CLI based, exactly as shown above.

---

### 10.2  Repository Structure Tour

```
DarkData-Medicine/
├── data/                        # The dataset itself (Ch.5's Experiment/Outcome
│   ├── oncology/                #   records), one domain folder per Ch.6 §6.3.1
│   ├── neurology/                #   controlled vocabulary term
│   ├── ...
│   └── templates/                # submission_schema.json (Ch.5, Ch.6 §6.3),
│                                  # submission_template.json
├── scripts/                     # The five OPERATIONAL/PLANNED tools specified
│   ├── validate_submission.py    #   in Chapter 4 §4.1 (Submission Service today)
│   ├── analyze_trends.py         #   §4.11 (Analytics Service today)
│   ├── export_to_excel.py        #   §4.2 (Metadata Service export path today)
│   ├── generate_search_index.py  #   §4.3 (Search Service today)
│   └── clinicaltrials_seed_extractor.py  # §4.15 (Import Service today)
├── tests/                       # pytest suite — see §10.5
├── site/                        # The static search interface (Ch.3 §3.4.3)
├── docs/                        # GOVERNANCE.md, CURATION_GUIDE.md,
│                                  # DATA_DICTIONARY.md, HOW_TO_CONTRIBUTE.md
├── .github/
│   ├── workflows/                # validate-submissions.yml, test-suite.yml,
│   │                              # deploy-site.yml (Ch.3 §3.2, Ch.9 §9.4)
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── CONTRIBUTING.md               # This chapter's short-form companion
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
└── FUNDING.md
```

**Mapping to the architecture series.** Every file above corresponds to a specific chapter/section reference in this series — that correspondence is deliberate and load-bearing, not a coincidence: the Domain Model (Chapter 5) is not an abstract diagram, it is `data/templates/submission_schema.json`; the Submission Service (Chapter 4 §4.1) is not a hypothetical microservice, it is `scripts/validate_submission.py` plus `.github/workflows/validate-submissions.yml`. A developer confused about how a Chapter 4 service concept maps to real code should start by finding the corresponding file in this tour before assuming a gap exists.

---

### 10.3  Your First Contribution

#### 10.3.1  If You're Contributing Data (Not Code)

Stop here and use `docs/HOW_TO_CONTRIBUTE.md` instead — the no-Git path described in Chapter 3 §3.8 and Chapter 4 §4.1's Inputs table. This chapter is for code contributions specifically.

#### 10.3.2  If You're Contributing Code

```bash
git checkout -b fix/short-description-of-change
# make your change
pytest tests/                       # every change must pass the existing suite
python scripts/validate_submission.py --self-test   # if you touched validation logic
git add .
git commit -m "fix: short, imperative description (see §10.4 for message format)"
git push origin fix/short-description-of-change
# open a PR using the template in .github/PULL_REQUEST_TEMPLATE.md
```

**What happens next.** `validate-submissions.yml` and `test-suite.yml` (Chapter 3 §3.2, Chapter 9 §9.4) run automatically. A maintainer reviews the change — per Chapter 8 §8.8, there is no auto-merge path for code, regardless of how small the change is. This is not a bureaucratic default; it is a deliberate supply-chain-security control, and a new contributor should not expect (or request) an exception to it.

---

### 10.4  Coding Standards

- **Python style.** PEP 8, enforced by the lint step in CI (Chapter 9 §9.4). Type hints are required on all new function signatures — not yet universally present in the existing `scripts/` codebase, but required going forward, consistent with this project's practice of tightening standards prospectively rather than retroactively rewriting working code purely for style conformance.
- **Commit messages.** Conventional Commits format (`fix:`, `feat:`, `docs:`, `refactor:`, `test:`, `chore:`), enabling automated changelog generation as the project scales past manual `CHANGELOG.md` editing.
- **No secrets in code, ever.** Per Chapter 8 §8.6.2 — this is checked by an automated secret-scanning step in CI (Chapter 9 §9.4's SAST/dependency-scan stage) as well as by code review, in keeping with the defense-in-depth principle (Chapter 8 §8.1) applied to the development process itself.
- **Every new service follows the Chapter 4 §4.0 template.** If you are implementing a `PLANNED` or `FUTURE` service from Chapter 4, its Purpose, Responsibilities, Inputs, Outputs, Dependencies, Security, Database, API, Events, Metrics, and Scaling sections are not optional background reading — they are the specification you are implementing against. A pull request implementing a new service without visibly satisfying its Chapter 4 specification should not be expected to pass review.

---

### 10.5  Testing Requirements

**Today (`OPERATIONAL`).**
```bash
pytest tests/                          # full suite
pytest tests/test_schema_and_validation.py   # schema validation logic only
pytest tests/test_analyze_trends.py          # trend-analysis logic only
pytest --cov=scripts tests/                  # coverage report
```

**Test coverage expectations for new code.** Every new validation rule requires both a positive test (valid input accepted) and a negative test (invalid input correctly rejected with the expected error) — directly reflecting the Zero Trust principle's (Chapter 2 §2.3.7) practical consequence: an untested rejection path is a rule that might silently fail open.

**When implementing a `PLANNED` service (Chapter 4).** Test coverage should include the full Internal Workflow described in that service's Chapter 4 specification, not only its happy path — specifically the failure and edge-case branches (e.g., for the Submission Service, §4.1: rate-limit exceeded, duplicate pre-check triggered, malformed schema version reference), since these are exactly the branches a service specification calls out explicitly and a reviewer will check against.

---

### 10.6  Worked Example: Implementing a New `PLANNED` Service

This section walks through the concrete first steps of taking the Metadata Service from its Chapter 4 §4.2 specification to a real, testable implementation — chosen as the example because it is the most-depended-upon `PLANNED` service not yet started, and because walking through it here demonstrates the pattern any other `PLANNED` service implementation should follow.

**Step 1 — Re-read the Chapter 4 specification as a checklist**, not as prose: Purpose, Responsibilities, Inputs (`SubmissionValidated`/`SubmissionApproved` events), Outputs (metadata records, export artifacts), Dependencies (Ontology Service, Storage Layer, DOI Service), Security (public read, event-triggered write only), Database (owns `metadata_records`, `controlled_vocabulary_mappings`), API (two endpoints), Events (`MetadataGenerated`).

**Step 2 — Confirm the Domain Model entity shape (Chapter 5 §5.1, relevant Zone D entities)** the service will read from and write to — a Metadata Service implementation that invents its own field names instead of using `Experiment`, `Hypothesis`, and `Outcome` as specified in Chapter 5 has silently diverged from the domain model, which downstream consumers (Search, Knowledge Graph) will discover the hard way.

**Step 3 — Confirm the API contract (Chapter 7 §7.5.2)** before writing implementation code: `GET /v1/entries/{id}/metadata` and `GET /v1/entries/{id}/export`, matching Chapter 7's standard error format (§7.4) and pagination/filtering conventions where applicable.

**Step 4 — Write the event consumer first, the API second.** Because the service's primary trigger is `SubmissionApproved` (an event, per Chapter 3 §3.7), not a direct API call, the core logic should be implemented and tested as an event handler independent of any HTTP framework — this keeps the Domain Layer (Chapter 3 §3.2) free of API-layer concerns, exactly as the layering discipline requires.

**Step 5 — Apply the security posture from Chapter 8 before considering the implementation complete**: confirm write access is genuinely restricted to legitimate event-triggered calls (Chapter 8 §8.2.3's STRIDE analysis for the submission flow is the relevant threat model), and confirm no Restricted-classification field (Chapter 8 §8.3) is exposed through the public export endpoint.

**Step 6 — Write tests per §10.5**, covering the full Internal Workflow from Chapter 4 §4.2, including the "vocabulary-mapping miss" case explicitly called out in that section's Metrics field — a case worth testing precisely because Chapter 4 flagged it as a metric worth watching, which means it is expected to actually occur in production.

**Step 7 — Update this series.** If implementation reveals that the Chapter 4 specification was wrong or incomplete in some way — a dependency it missed, an event payload shape that does not actually work — the correction belongs in Chapter 4 itself, via the same governance-reviewed change process (Chapter 2 §2.6) as any other architectural change, not as an undocumented divergence between "what the docs say" and "what the code actually does." This series' entire value rests on that correspondence staying true.

---

### 10.7  Working with the Schema and Ontology

**Proposing a new controlled-vocabulary term (Chapter 6 §6.5).** Do not add a new enum value to `submission_schema.json` directly in a routine pull request — this is a governed change, not an ordinary code change. Open an issue using `.github/ISSUE_TEMPLATE/feature_request.md`, stating the rationale per Chapter 6 §6.5's governance-review requirement, and expect it to be reviewed by a `Curation Lead` before any schema change is merged.

**Proposing a new domain category.** Same process, higher bar — a new top-level `domain` value (Chapter 6 §6.3.1) affects every downstream service that facets or classifies by domain, so the migration-plan requirement in Chapter 2 §2.6 principle 6 applies in full: state what existing entries, if any, would need reclassification, and how.

---

### 10.8  Local Debugging and Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `validate_submission.py` rejects a submission with an unclear error | Missing required field or invalid enum value | Run with `--verbose` to get the specific `jsonschema` validation path; cross-check against `docs/DATA_DICTIONARY.md` |
| `pytest` fails only in CI, not locally | Python version mismatch, or a test relying on unpinned dependency behavior | Confirm your local Python version matches CI's (`.github/workflows/test-suite.yml`); check `requirements.txt` pinning |
| `generate_search_index.py` output doesn't reflect a recently merged entry | Static index requires regeneration — it is not a live database (Chapter 3 §3.4.3) | Re-run the script; in production this happens automatically via `deploy-site.yml` |
| A new service's event handler never fires | No live Event Bus exists yet (Chapter 3 §3.7 is `PLANNED`) | Confirm whether you're implementing against target-state architecture ahead of its dependencies — check the relevant Chapter 4 service's Implementation Status before assuming a local bug |

---

### 10.9  Documentation Standards

Every public function requires a docstring stating its purpose, parameters, and return value, sufficient to generate API reference documentation automatically once the OpenAPI-driven documentation pipeline (Chapter 7 §7.9) is live. Until then, docstrings are the primary reference documentation and are held to the same standard.

---

### 10.10  Where to Get Help

- **Architecture questions** ("why is X designed this way") — check Chapters 2–9 of this series first; the reasoning is almost always recorded there, cross-referenced by section.
- **Governance questions** (schema changes, new maintainers, funding) — `docs/GOVERNANCE.md`.
- **Security issues** — never a public GitHub issue; follow the responsible-disclosure process specified in Chapter 8 §8.12 once `SECURITY.md` is published.
- **Everything else** — open a GitHub issue using the appropriate template in `.github/ISSUE_TEMPLATE/`.

---

### 10.11  Quick Reference

```bash
# Setup
git clone https://github.com/Ciprian-LocalPulse/DarkData-Medicine.git && cd DarkData-Medicine
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Validate a submission
python scripts/validate_submission.py path/to/entry.json

# Run tests
pytest tests/                          # all
pytest --cov=scripts tests/            # with coverage

# Analyze trends
python scripts/analyze_trends.py --domain oncology

# Rebuild the search index
python scripts/generate_search_index.py

# Export to spreadsheet
python scripts/export_to_excel.py --output export.xlsx
```

---

### 10.12  Summary and Handoff

This chapter has given a new engineer everything needed to go from `git clone` to a merged, reviewed pull request — environment setup, the repository-to-architecture correspondence (§10.2), the worked example of implementing a `PLANNED` Chapter 4 service against its own specification (§10.6), and the governance boundary around schema and ontology changes specifically (§10.7). The Operations Manual, the final document in this series, picks up where this chapter leaves off: not how to build the platform, but how to keep it running, monitored, and recoverable once built — the day-two concerns this chapter deliberately left out of scope.
