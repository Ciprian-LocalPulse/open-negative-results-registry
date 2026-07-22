# Dark Data Medicine — Platform Architecture Series

## Chapter 15: Testing Architecture

*Document status: Normative. Governed by Chapter 3 (§3.12, Failure Scenarios), Chapter 7 (§7.2, Compatibility Policy), Chapter 8 (§8.14, Security Quality Scenarios), Chapter 9 (§9.4, CI/CD Pipeline), Chapter 10 (§10.5, Testing Requirements), and Chapter 12 (§12.9, AI Evaluation). This chapter is where every quality attribute, quality scenario, and compatibility guarantee promised across the preceding fourteen documents becomes a specific, automated, CI-gating test.*

*Version 0.1 — Draft for governance review*

---

### 15.0  Purpose and Scope

A recurring pattern across this series is the quality scenario — Chapter 3 §3.15's ATAM-style availability/scalability/security scenarios, Chapter 8 §8.14's confidentiality/integrity/non-repudiation scenarios. A quality scenario that is never executed as an actual test is a documented intention, not a verified property. This chapter's entire purpose is to close that gap: every scenario named in this series has a corresponding entry in this chapter's testing taxonomy, and every entry states, concretely, what kind of test verifies it and where in the CI/CD pipeline (Chapter 9 §9.4) that test runs.

**Relationship to Chapters 12 and 14.** This chapter does not duplicate Chapter 12 §12.9's AI evaluation metrics or Chapter 14 §14.6's security-scanning pipeline — it integrates them as two of the taxonomy's levels (§15.8, §15.10), because "testing" for this platform is one coherent discipline, not three separately governed ones that happen to share a CI system.

---

### 15.1  Testing Philosophy

1. **An untested rejection path is a rule that might silently fail open.** Restated from Chapter 10 §10.5 as this chapter's foundational principle: every validation rule, every access-control check, every governance constraint specified anywhere in this series is untrustworthy until a test demonstrates it actually rejects the case it claims to reject, not merely that it accepts the case it claims to accept.
2. **Test the specification, not the implementation.** A test suite that merely encodes whatever the current code happens to do provides no protection against a regression that changes both the code and, silently, the behavior. Tests in this architecture are written against the Chapter 4 service specifications, the Chapter 5 domain model, and the Chapter 7 API contract — a test failing because the specification changed is expected and correct; a test failing because an implementation accidentally drifted from a specification that did not change is exactly the failure mode this principle exists to catch.
3. **A quality scenario without a test is an unverified claim.** Applied specifically to close the gap named in §15.0.
4. **Data-quality testing is a first-class testing category for this platform, not an operational afterthought.** Most software systems do not need a distinct testing discipline for the *correctness of the data itself*, as opposed to the correctness of the code that handles it — this platform does, because its entire value proposition (Chapter 2 §2.1) rests on dataset trustworthiness, and §15.7 is built specifically around that platform-specific need.

---

### 15.2  Test Pyramid and Taxonomy

```
                    /\
                   /  \      E2E & Chaos (§15.6, §15.9)
                  /----\     — fewest, slowest, highest-fidelity
                 /      \
                /--------\   Integration & Contract (§15.4, §15.5)
               /          \
              /------------\  Unit (§15.3)
             /              \ — most numerous, fastest, run on every commit
            /----------------\

     Cross-cutting, not layered in the pyramid:
        Data Quality (§15.7)  |  AI Evaluation (§15.8)  |  Security (§15.10)
        — applied at whichever pyramid level is appropriate per test case
```

| Level | What It Verifies | Current Status |
|---|---|---|
| Unit | A single function/module's logic in isolation | `OPERATIONAL` (existing pytest suite) |
| Integration | Two or more services/components interacting correctly | `PLANNED` |
| Contract | A service's actual behavior matches its Chapter 7 API contract | `PLANNED` |
| End-to-End (E2E) | A full user-facing workflow, start to finish | `PLANNED` |
| Chaos/Resilience | The system behaves as Chapter 3 §3.12 and Chapter 8 §8.14 claim under injected failure | `FUTURE` |
| Data Quality | The published dataset itself meets the accuracy/consistency bar the platform's funding case commits to | `PLANNED` |
| AI Evaluation | AI Service outputs meet Chapter 12 §12.9's metric thresholds | `FUTURE` (depends on AI Service, Ch.12) |
| Security | No newly introduced vulnerability, per Chapter 14 §14.6 | `PLANNED` |

---

### 15.3  Unit Testing Standards

**Today (`OPERATIONAL`).** `tests/test_schema_and_validation.py` and `tests/test_analyze_trends.py`, run via `pytest` on every pull request (Chapter 3 §3.2, Chapter 9 §9.4).

**Coverage requirements, restated from Chapter 10 §10.5 with an explicit numeric target.** New code requires minimum 80% line coverage, with 100% coverage required specifically on validation and access-control logic (Chapter 8 §8.4, §8.5) — an uncovered line in a permission check is a materially different risk than an uncovered line in a logging statement, and the coverage requirement is weighted accordingly rather than applied as a single flat threshold across all code equally.

**Standard per-module test structure**, applied uniformly per Chapter 2 §2.11's interoperability-over-local-optimization principle:
```python
class TestSubmissionValidation:
    def test_valid_submission_accepted(self): ...
    def test_missing_required_field_rejected(self): ...
    def test_invalid_enum_value_rejected(self): ...
    def test_malformed_orcid_pattern_rejected(self): ...
    # Every negative test case traces to a specific schema constraint
    # (Ch.5, Ch.6 §6.3) — a new schema constraint without a matching
    # negative test is an incomplete implementation, not a passing one
```

---

### 15.4  Integration Testing

Verifies the Chapter 3 §3.5 component-interaction chain and the Chapter 3 §3.7 event vocabulary actually work across service boundaries, not merely within any one service in isolation.

```python
def test_submission_approval_triggers_metadata_generation():
    submission = create_test_submission(domain="Oncology")
    approve_submission(submission.id, curator=test_curator)
    # Verifies the SubmissionApproved -> MetadataGenerated event
    # chain (Ch.3 §3.7, Ch.4 §4.2) actually fires end-to-end,
    # not just that each service's internal logic is individually correct
    assert wait_for_event("MetadataGenerated", entity_id=submission.id)
    metadata = get_metadata_record(submission.id)
    assert metadata.domain_term.label == "Oncology"
```

Event-driven architectures (Chapter 3 §3.5's deliberate choice) carry a specific integration-testing obligation: because services are decoupled and communicate asynchronously, a broken event contract can pass every individual service's unit tests while the system as a whole silently stops working — integration tests are this architecture's primary defense against exactly that failure mode.

---

### 15.5  Contract Testing

Verifies Chapter 7's compatibility policy (§7.2) is actually upheld, not merely documented:

- **Provider-side contract tests.** Every REST endpoint's actual response is validated against the canonical `openapi.yaml` (Chapter 7 §7.9) on every deploy — a response that technically "works" but has silently drifted from its documented schema fails this test even if no consumer has yet noticed.
- **Consumer-driven contract tests, specifically for federation nodes.** Because Stage 4 (Chapter 3 §3.10, Chapter 9 §9.2.4) involves independently-operated mirror nodes running their own deployment cadence, a primary-node API or sync-protocol change that breaks an older node's expectations is a real operational risk distinct from a single-deployment system's concerns — consumer-driven contract tests, where each supported node version's actual expectations are captured and re-verified against every primary-node change, are the specific testing mechanism that catches this before it reaches production, extending Chapter 9 §9.9's cross-node deployment-consistency scenario into an automated check rather than a documented expectation.
- **Breaking-change detection.** Automated diffing of the API specification between versions, failing CI if a change matches Chapter 7 §7.2's definition of "breaking" without a corresponding major-version bump.

---

### 15.6  End-to-End Testing

Verifies the full Chapter 3 §3.3 user interaction flow, from a contributor's first action through search indexing:

```
E2E scenario: "A negative oncology trial result becomes discoverable"
  1. Submit via API (Ch.7 §7.5.1) with valid schema-conformant data
  2. Verify submission enters curation queue (Ch.4 §4.8)
  3. Curator approves via Review Service API
  4. Verify entry becomes retrievable via GET /v1/entries/{id}
  5. Verify entry appears in search results for a relevant query
  6. Verify entry's metadata export (Ch.4 §4.2) is well-formed
```

E2E tests run against the Staging environment (Chapter 9 §9.1) as part of the standard release-promotion gate (Chapter 9 §9.4), using synthetic data (§15.12) rather than production data, so that a failing E2E test never has data-privacy implications regardless of what it happens to touch.

**Curator UAT (user acceptance testing).** Distinct from automated E2E tests: before a Review Service (Chapter 4 §4.8) UI change reaches production, at least one actual `Curator`-role user validates the workflow change against a realistic curation scenario — an automated E2E test verifies the system *works*; UAT verifies it is actually *usable* by the humans Chapter 2 §2.9's Human Accountability principle depends on remaining willing and able to do their job.

---

### 15.7  Data Quality Testing

The platform-specific testing category named in §15.1's fourth principle, operationalizing the audited quality metrics the funding case commits to:

| Check | Method | Threshold |
|---|---|---|
| Schema conformance of the full published dataset | Automated, run against every entry on every release (Chapter 4 §4.9) | 100% — a non-conformant entry in a Dataset Release is a release-blocking defect |
| Audited false-positive/misclassification rate | Manual audit of a random sample (funding case §5.6, Chapter 8 §8.14 Integrity scenario) | ≤5% (funding case commitment) |
| Duplicate-detection accuracy | Precision/recall against a labeled test set of known duplicate and known-distinct entry pairs | Tracked as a trend, reviewed at the cadence in Chapter 11 §11.5 |
| Ontology mapping consistency | Every `skos:exactMatch` re-verified against the external source's current version (Chapter 6 §6.8) | No unflagged stale mappings at release time |
| Referential integrity | Every Domain Model relationship (Chapter 5) resolves to an existing target entity — no dangling references | 100%, automated |
| Fuzz testing the submission schema | Property-based testing (e.g., Hypothesis-style generators) throwing malformed, boundary, and adversarial input at `validate_submission.py` | No crash, no silent acceptance of invalid data, on any generated input |

**Why this is distinct from ordinary software QA.** A bug in `validate_submission.py` is a code-quality problem with a known fix (patch the code); a false-positive negative-result entry that passed every automated check is a *data*-quality problem that requires the audit sampling process above specifically because no automated check, however well-designed, can currently verify that a claimed negative result genuinely reflects what happened in the underlying experiment — that judgment remains, correctly, a human curatorial one (Chapter 4 §4.8), and this testing category exists to measure how reliably that human process is working, not to replace it.

---

### 15.8  AI Evaluation Testing

Integrated from Chapter 12 §12.9 as this taxonomy's AI-specific level: the full metric set (suggestion-acceptance rate, retrieval precision@k, grounding pass rate, confidence calibration, false-positive duplicate-flag rate, curator override rate) runs as an automated evaluation suite against a held-out, curator-verified test set, gating any model/prompt promotion from Staging to Production per Chapter 12 §12.10's shadow-deployment and governance-review process. This chapter adds one integration point Chapter 12 did not specify: the AI evaluation suite runs in the *same* CI/CD pipeline (Chapter 9 §9.4) as every other test category, reported on the same pass/fail dashboard, rather than as a separate, easily-overlooked process — an AI-quality regression should be exactly as visible to the team as a broken unit test, not siloed into a specialist's separate workflow.

---

### 15.9  Chaos and Resilience Testing

Operationalizes Chapter 3 §3.12's Failure Scenarios and Chapter 8 §8.14's Security Quality Scenarios as executed, not merely documented, tests:

```
Chaos scenario: "Knowledge Graph Service becomes unavailable"
   (Directly testing Ch.3 §3.15's Reliability quality scenario)
  1. In a staging/chaos-testing environment, forcibly degrade or
     kill the Knowledge Graph Service.
  2. Verify: Submission and Search services continue operating
     (per Ch.3 §3.5's event-driven decoupling claim).
  3. Verify: only cross-entity graph queries fail, not core
     publication or discovery.
  4. Verify: Monitoring Service (Ch.4 §4.17) correctly alerts on
     the degradation within the target detection window.
  5. Restore the service; verify: the Knowledge Graph backlog
     drains without manual intervention (event replay from the
     Event Bus, Ch.3 §3.7).

Chaos scenario: "Volumetric DDoS against public search"
   (Directly testing Ch.8 §8.14's Availability-under-attack scenario)
  1. Simulate high-volume traffic against /v1/search.
  2. Verify: static-index CDN fallback (Ch.3 §3.12) continues
     serving cached results.
  3. Verify: rate limiting (Ch.7 §7.8) engages as configured.
  4. Verify: legitimate authenticated traffic is not starved by
     the attack traffic (isolation between rate-limit buckets,
     Ch.7 §7.8's client-category tiers).
```

**Cadence.** Chaos testing runs against Staging on a scheduled basis (not only pre-release), because resilience properties can regress silently as the system evolves even absent a specific triggering code change — a service that was resilient to its dependency's failure six months ago may no longer be, if an intervening change quietly introduced a synchronous call where an asynchronous event previously existed.

---

### 15.10  Security Testing

Integrated from Chapter 14 §14.6's automated scanning pipeline (dependency, SAST, secret, container-image scanning) as this taxonomy's security level, with one addition Chapter 14 did not specify: **scheduled, non-CI-triggered penetration testing**, conducted at least annually (aligned with Chapter 11 §11.5's annual review cadence) by a party independent of the core development team — automated scanning catches known vulnerability patterns; periodic manual penetration testing is this architecture's control for the vulnerability classes automated scanning structurally cannot find, including logic flaws in the RBAC policy (Chapter 14 §14.2) and the dual-authorization workflow (Chapter 14 §14.5) that a scanner has no way to reason about.

---

### 15.11  Performance and Load Testing

Load and performance testing is scoped in outline here and specified to full depth in Chapter 16 (Performance Architecture), consistent with this series' practice of a dedicated chapter for any concern substantial enough to warrant one (Chapter 2 §2.11). This chapter's role is limited to establishing that performance tests are a CI-gating category on the same footing as every other level in this taxonomy (§15.13), not a separately-scheduled, easily-deprioritized activity.

---

### 15.12  Test Environments and Data Management

- **Synthetic test data**, generated to match the Domain Model's entity shapes (Chapter 5) and schema constraints (Chapter 6), used across unit, integration, and E2E testing — never real, unpublished submission data, which per Chapter 8 §8.3's data classification may contain Restricted-classification content inappropriate for a lower-security-tier test environment.
- **Staging data refresh policy.** Staging's dataset (Chapter 9 §9.1) is either fully synthetic or a sanitized snapshot of already-published (hence already-public) production data — never a snapshot including unpublished submissions or curator-only notes.
- **Test data versioning.** Synthetic test fixtures are version-controlled alongside the code that consumes them, subject to the same review process (Chapter 10 §10.3.2) as any other change, so that a fixture update is reviewable and its effect on existing tests is visible in the same pull request.

---

### 15.13  CI Gating Summary

Consolidated view of what blocks a merge or a production promotion, across every testing level defined in this chapter, integrated into the Chapter 9 §9.4 pipeline:

| Gate | Blocks | Stage in Ch.9 §9.4 Pipeline |
|---|---|---|
| Unit tests (§15.3) | Merge to main | "Automated checks" |
| SAST/dependency/secret scan (§15.10, Ch.14 §14.6) | Merge to main | "Automated checks" |
| Integration tests (§15.4) | Deploy to Staging | Post-merge, pre-staging-deploy |
| Contract tests (§15.5) | Deploy to Staging (API changes only) | Post-merge, pre-staging-deploy |
| E2E tests (§15.6) | Production promotion | "Staging validation" |
| DAST scan (Ch.8 §8.5) | Production promotion | "Staging validation" |
| Data quality checks (§15.7) | Dataset Release publication specifically | Release pipeline (Ch.4 §4.9), not every deploy |
| AI evaluation suite (§15.8) | AI model/prompt promotion specifically | Ch.12 §12.10's shadow-deployment gate |
| Curator UAT (§15.6) | Review Service UI changes specifically | Manual promotion gate |
| Chaos testing (§15.9) | Not merge-blocking — scheduled, findings feed into backlog | Independent of the release pipeline |
| Penetration testing (§15.10) | Not merge-blocking — annual, findings feed into Ch.8 revision | Independent of the release pipeline |

---

### 15.14  Implementation Status Summary

| Category | Status |
|---|---|
| Unit testing (existing suite) | `OPERATIONAL` |
| Integration testing | `PLANNED` |
| Contract testing | `PLANNED` |
| E2E testing | `PLANNED` |
| Data quality testing (schema conformance) | `OPERATIONAL` (via `validate_submission.py`, applied per-entry today) / `PLANNED` (full audited program per §15.7) |
| AI evaluation testing | `FUTURE` (depends on Ch.12) |
| Chaos/resilience testing | `FUTURE` |
| Security testing (automated) | `PLANNED` (Ch.14 §14.6) |
| Penetration testing (manual, scheduled) | `PLANNED` |

---

### 15.15  Summary and Handoff

This chapter has ensured that every quality claim made across the preceding fourteen documents — an availability guarantee, a security control, a compatibility promise, an AI-quality threshold, a data-integrity commitment — has a named, CI-integrated test category responsible for verifying it, consolidated in §15.13's gating table. Chapter 16's task is to take the Performance level named but deferred in §15.11 and specify it to the same depth: concrete load-testing scenarios, capacity thresholds, and the specific latency/throughput targets every service in Chapter 4 must be verified against before this series can claim, rather than merely design toward, the scalability story told in Chapter 3 §3.10.
