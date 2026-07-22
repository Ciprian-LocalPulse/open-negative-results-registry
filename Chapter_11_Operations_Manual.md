# Dark Data Medicine — Platform Architecture Series

## Chapter 11: Operations Manual

*Document status: Practical / Operational. The final document in this series. Governed by Chapter 3 (§3.11–§3.12, Availability and Failure Scenarios), Chapter 4 (Monitoring §4.17, Backup §4.18, Administration §4.19), Chapter 8 (§8.11, Incident Response), and Chapter 9 (§9.8, Disaster Recovery deployment). Where those chapters specified *what the system should do* under failure, this chapter specifies *what a human being actually does*, checklist by checklist.*

*Version 0.1 — Draft for governance review*

---

### 11.0  Who This Chapter Is For

This is the document open in a second window when something is wrong, or when a routine task is due. It is written for whoever is currently accountable for keeping the platform running — today, that is the founding maintainer directly; per the governance transition referenced throughout this series (Chapter 2 §2.2, Chapter 4 §4.6), it is designed to remain usable once that accountability is distributed across a curator and technical-maintainer team, without requiring institutional memory no document captures.

**This chapter's honesty commitment, stated once and applied throughout.** Today's actual operations are simple, because today's actual system (Chapter 9 §9.2.1) is simple: a static site, a Git repository, and three CI workflows. Every runbook and procedure below states plainly whether it describes today's real operational reality or the target-state operations for a `PLANNED`/`FUTURE` component — an on-call engineer following a runbook for infrastructure that does not exist yet is worse off than one told clearly "this component isn't live; here is what actually happens instead."

---

### 11.1  Operational Philosophy

- **Boring is a design goal, not a compromise.** Chapter 3 §3.12 identified that several of the platform's failure modes degrade gracefully specifically because Stage 1's architecture is simple and static. Operations should actively resist adding complexity ahead of the scale that justifies it (Chapter 3 §3.10's staged-adoption discipline applies to operational practice, not only to infrastructure).
- **Every alert should point to a runbook.** An alert with no corresponding procedure in §11.6 is an operational gap, not merely a monitoring gap — flag it at the next governance review (§11.10) rather than leaving it as tribal knowledge.
- **The Audit Service is the operator's memory.** Per Chapter 4 §4.16 and Chapter 8 §8.11, incident investigation starts with the audit trail, not with asking around — this is true today via Git commit history and GitHub Actions logs, and will remain true, in a richer form, once the dedicated Audit Service is live.

---

### 11.2  Service Level Objectives (SLOs)

| Service | SLO | Status |
|---|---|---|
| Public search availability | 99.9% monthly, measured against the static site's CDN-backed uptime | `OPERATIONAL` — currently inherits GitHub Pages' own SLA, not independently measured yet |
| Submission validation turnaround | Automated validation result within 5 minutes of PR open (CI runtime) | `OPERATIONAL` |
| Curator time-to-decision | Median under 5 business days per the platform's funding case KPI targets | `PLANNED` — not yet tracked as a formal SLO, only informally |
| API p95 latency (once live) | Under 500ms for read endpoints, under 2s for write endpoints | `PLANNED` |
| Backup restoration RTO | Under 4 hours (Chapter 9 §9.8) | `PLANNED` |

**Action item flagged by this chapter.** Formal SLO tracking against these targets — as opposed to the target values simply being stated — is itself a `PLANNED` operational capability, dependent on the Monitoring and Analytics services (Chapter 4 §4.17, §4.11) reaching `OPERATIONAL` status. Until then, this table is a stated commitment the team holds itself to informally, not a dashboard anyone can currently query.

---

### 11.3  On-Call and Escalation

**Today (`OPERATIONAL`, informal).** The founding maintainer is the de facto single point of on-call responsibility. GitHub's own notification system (email/mobile) surfaces CI failures and pull-request activity; there is no 24/7 paging system because there is no live, always-on service whose downtime would require one — the static site's availability is GitHub Pages' concern, not a page-worthy platform incident.

**Target state (`PLANNED`, from Stage 2 onward per Chapter 9 §9.2.2).**

```
Alert fires (Monitoring Service, Ch.4 §4.17)
      |
      v
Severity auto-classified (per Ch.8 §8.11's table, reproduced below)
      |
      v
Critical/High  --> Page on-call engineer immediately
Medium         --> Ticket created, next-business-day triage
Low            --> Logged, reviewed at next routine check (§11.5)
      |
      v
On-call engineer acknowledges, begins the matching runbook (§11.6)
      |
      v
If unresolved within the severity's response target (Ch.8 §8.11):
   escalate to Curation Lead / Administrator
      |
      v
If a governance-level decision is required (e.g., federation node
revocation, Ch.8 §8.10.5): escalate to Administrator, dual-authorization
applies per Ch.8 §8.4.4
```

| Severity | Response Target (from Ch.8 §8.11) | Who Is Paged |
|---|---|---|
| Critical | Immediate; public disclosure within 72 hrs of confirmation | Founding maintainer / on-call engineer, then Administrator |
| High | Containment within 24 hrs | On-call engineer |
| Medium | Investigation within 5 business days | Assigned during routine triage, no page |
| Low | Standard remediation cycle | Logged only |

---

### 11.4  Monitoring and Alerting

**Today (`OPERATIONAL`, indirect).** GitHub Actions workflow run status is the primary health signal: a red `validate-submissions.yml` or `test-suite.yml` run is the closest thing the current system has to an alert, and it is visible directly in the GitHub UI and via notification, not through a dedicated dashboard.

**Target state (`PLANNED`, Chapter 4 §4.17).** A dedicated monitoring stack with the following alert thresholds, to be configured as each underlying service reaches `OPERATIONAL` status:

| Metric | Warning Threshold | Critical Threshold |
|---|---|---|
| API error rate (5xx) | > 1% over 5 min | > 5% over 5 min |
| API p95 latency | > 2× SLO target | > 4× SLO target |
| Curation queue depth (per domain) | > 50 pending | > 150 pending |
| Backup job failure | Any single failure | Two consecutive failures |
| Federation node sync lag | > 1 hour | > 6 hours |
| Certificate expiry (TLS, Chapter 8 §8.6.1) | 30 days out | 7 days out |
| Disk/storage utilization | > 75% | > 90% |

---

### 11.5  Routine Operational Tasks

| Cadence | Task | Owner | Status |
|---|---|---|---|
| Daily | Review any failed CI run overnight | On-call / maintainer | `OPERATIONAL` |
| Daily | Scan curation queue for domains approaching Warning threshold (§11.4) | Curation Lead | `PLANNED` (informal today) |
| Weekly | Dependency vulnerability scan review (Chapter 8 §8.8) | Technical maintainer | `PLANNED` |
| Weekly | Spot-check a random sample of newly published entries against the curation checklist (Chapter 4 §4.8), as an independent quality signal distinct from the curator's own review | Curation Lead | `PLANNED` |
| Monthly | Backup restoration test (Chapter 4 §4.18 — "an untested backup is not counted as a backup") | Administrator | `PLANNED` (no live backup pipeline yet beyond GitHub's own repository redundancy) |
| Monthly | Review Ontology Service's unmapped-term rate (Chapter 6 §6.8) and prioritize enrichment work | Curation Lead | `PLANNED` |
| Quarterly | Funder progress report (per the platform's funding case, §5.5, and Appendix Y's template) | Program Lead | `OPERATIONAL` — already a standing commitment, produced from `analyze_trends.py` output today |
| Quarterly | Inter-curator agreement benchmark review (platform funding case KPI) | Curation Lead | `PLANNED` |
| Quarterly | Security posture review against Chapter 8's control checklist | Administrator | `PLANNED` |
| Annually | Full disaster-recovery drill (§11.11), not merely a backup restoration test but a full DR-environment activation | Administrator | `FUTURE` — depends on the DR environment (Chapter 9 §9.1) existing |
| Annually | Governance charter and this documentation series' own review for drift against actual practice | Steering Group (once seated) / founding maintainer | `PLANNED` |

---

### 11.6  Runbooks

#### 11.6.1  CI Pipeline Failure (`OPERATIONAL` — applies today)

```
1. Identify which workflow failed (validate-submissions.yml,
   test-suite.yml, or deploy-site.yml) via the GitHub Actions tab.
2. Read the failure log. Common causes:
   - A submission genuinely fails schema validation (expected behavior,
     not an incident — the contributor is notified via the PR check).
   - A dependency version bump broke compatibility (check requirements.txt
     pinning, Ch.8 §8.8).
   - A flaky test (rare; re-run once before investigating further).
3. If the failure is a genuine tooling bug: open an issue, fix via the
   standard PR process (Ch.10 §10.3.2) — do not bypass CI to force a merge.
4. If deploy-site.yml specifically fails: the static site remains live at
   its last successfully deployed state (Ch.3 §3.12 — no live deployment
   means no live-deployment failure mode); there is no user-facing urgency
   distinct from getting the fix merged through the normal process.
```

#### 11.6.2  Stale Search Index (`OPERATIONAL`)

```
1. Confirm: has a recent merge to main actually completed a
   deploy-site.yml run? (Check Actions tab.)
2. If deploy-site.yml succeeded but the index still looks stale:
   check CDN cache — GitHub Pages' own caching layer, not a platform-level
   cache, may be the cause; this typically self-resolves within minutes.
3. If deploy-site.yml has not run: re-trigger it manually or push an
   empty commit to main to trigger the workflow.
4. Target-state (Ch.4 §4.3, PLANNED): once OpenSearch is live, index
   staleness is a monitored metric (§11.4) with its own alert, not a
   manually-checked condition.
```

#### 11.6.3  Suspected Compromised Curator Account (`PLANNED` — depends on live Authentication Service, Ch.4 §4.6)

```
1. Immediately revoke the account's active sessions/tokens
   (Authentication Service, Ch.4 §4.6).
2. Pull the account's full action history from the Audit Service
   (Ch.4 §4.16) — every Review this account performed, with timestamps.
3. Flag every entry approved by this account during the suspected
   compromise window for governance re-review — do NOT auto-unpublish;
   unpublishing is itself a destructive action subject to Ch.8 §8.4.4's
   dual-authorization rule, and a flagged-for-review state is the
   correct interim response.
4. Classify severity per Ch.8 §8.11's table based on confirmed impact.
5. Follow the full Incident Response flow (Ch.8 §8.11) from Containment
   onward, including post-incident disclosure per Ch.8 §8.12's
   transparency commitment if any published data was affected.
```

#### 11.6.4  Compromised or Misbehaving Federation Node (`FUTURE` — depends on Federation Service, Ch.4 §4.12)

```
1. Revoke the node's signing key from the trust registry
   (Ch.8 §8.10.5) — this is a governance-reviewed action, not a
   unilateral technical one, but may be executed provisionally by
   an Administrator pending governance ratification if the node is
   actively propagating falsified data.
2. Reject all subsequent sync messages from the revoked key
   (automatic, once revoked).
3. Do NOT automatically purge already-synchronized data from the
   compromised node — flag for governance review (Ch.8 §8.10.5).
4. Notify other federation nodes of the revocation through the
   federation governance channel.
5. Follow full Incident Response (Ch.8 §8.11).
```

#### 11.6.5  Restoring from Backup (`PLANNED` — depends on Backup Service, Ch.4 §4.18)

```
1. Confirm the specific failure requiring restoration (data corruption,
   accidental deletion, infrastructure loss) and its scope.
2. Identify the most recent backup snapshot with a passing restoration
   test result (Ch.4 §4.18 — an untested backup is never the first
   choice even if it is the most recent one).
3. Trigger restoration via POST /v1/backup/restore (Ch.7 §7.5.14) —
   requires two independent Administrator approvals (Ch.8 §8.4.4).
4. Restore into the DR environment first (Ch.9 §9.1, §9.8), not
   directly into Production, and verify integrity before promoting.
5. Document the incident and restoration in the Audit Service and
   in the next governance review (§11.10).
```

---

### 11.7  Release Management Operations

Operationalizing Chapter 9 §9.4's CI/CD pipeline from a day-of-release, human perspective:

```
1. Confirm all automated checks (Ch.9 §9.4) are green on the target commit.
2. (From Stage 2 onward) Deploy to Staging; run smoke tests.
3. Obtain manual promotion approval (Curation Lead or Administrator,
   Ch.9 §9.4) — for any change touching the schema (Ch.5), ontology
   (Ch.6), or curation workflow (Ch.4 §4.8), this approval additionally
   requires confirming the governance-review process (Ch.2 §2.6,
   Ch.6 §6.5) was actually followed, not merely that CI passed.
4. Deploy to Production via rolling deployment (Ch.9 §9.4).
5. Monitor the post-deployment health check window (Ch.9 §9.4,
   Ch.4 §4.17) — the operator does not consider a release complete
   until this window passes clean.
6. If the health check fails: automatic rollback (Ch.9 §9.4);
   the operator's job is to confirm the rollback succeeded and to
   open an incident per §11.6 if the failure indicates anything
   beyond a simple bad deploy.
7. Update CHANGELOG.md and, for a dataset release specifically
   (Ch.4 §4.9), confirm the DOI was successfully minted before
   announcing the release publicly.
```

---

### 11.8  Capacity Planning

The operator's role in the staged scaling model (Chapter 3 §3.10) is to monitor the specific thresholds that trigger a stage transition and raise it for governance/architecture review well before the threshold is breached — a stage transition is an architectural decision (Chapter 2 §2.11), not an emergency reaction to an outage:

| Signal | Reviewed | Triggers Consideration Of |
|---|---|---|
| Entry count trend | Monthly (§11.5) | Stage 1 → 2 transition (live API/database needed) |
| Curation queue depth sustained above Warning threshold (§11.4) | Weekly | Curator headcount increase, independent of infrastructure stage |
| API query latency trend (once live) | Weekly, once `OPERATIONAL` | Stage 2 → 3 transition (orchestration/autoscaling needed) |
| Federation partner interest / signed partnerships | Quarterly, aligned with the platform's funding-case partnership KPIs | Stage 3 → 4 transition (federation infrastructure needed) |

---

### 11.9  Curator Operations

- **Onboarding a new curator.** Grant the `Curator` role scoped to their assigned domain(s) (Chapter 8 §8.4.1); require MFA enrollment before first queue access (Chapter 8 §8.4.1); walk through `docs/CURATION_GUIDE.md` and this series' Chapter 4 §4.8 specification together, since the guide and the specification are meant to describe the same process at different levels of formality.
- **Offboarding.** Revoke role and active sessions immediately (Chapter 4 §4.6); their historical Review records (Chapter 5 §5.3.2) remain permanently attributed to them per Chapter 2 §2.9 — offboarding removes access, never historical attribution.
- **Monitoring curator health, not just system health.** Time-to-decision and queue-depth metrics (§11.2, §11.4) exist partly to protect curators from unsustainable load, not only to protect the platform's throughput — a Curation Lead reviewing these numbers should be watching for both signals.

---

### 11.10  Governance Operational Cadence

| Cadence | Activity | Reference |
|---|---|---|
| Quarterly | Funder reporting | Platform funding case §5.5, Appendix Y |
| Quarterly | Ontology change-proposal review batch (non-urgent proposals accumulated and reviewed together, urgent ones per Ch.6 §6.5's process on their own timeline) | Chapter 6 §6.5 |
| Quarterly | Risk register review | Platform funding case Appendix S |
| As triggered | Steering-group transition milestones | Chapter 2 §2.5 constraint 4, Chapter 4 §4.6 governance transition |
| As needed | Audit log spot review for anomalous administrative-action patterns (Chapter 4 §4.19's metric) | Chapter 8 §8.14's Integrity quality scenario |

---

### 11.11  Disaster Recovery Execution

Operationalizing Chapter 9 §9.8:

```
1. Declare a DR event (Administrator decision, following Critical-severity
   Incident Response, Ch.8 §8.11).
2. Stand up the DR environment (Ch.9 §9.1) from the most recent verified
   backup (Ch.11 §11.6.5's restoration runbook).
3. Redirect traffic (DNS/load-balancer level) once DR environment health
   checks pass.
4. Communicate status via the platform's public status channel
   (Ch.4 §4.17's public aggregate status endpoint).
5. Once root cause is resolved in the primary environment, plan and
   execute failback during a low-traffic window, verified against the
   same health-check discipline as any other deployment (Ch.9 §9.9).
6. Full post-incident review (Ch.8 §8.11's final step), including
   whether the actual RTO/RPO achieved met the targets in Ch.9 §9.8 —
   and if not, why, feeding back into this chapter's own revision.
```

---

### 11.12  Implementation Status Summary

| Capability | Status |
|---|---|
| CI-based health signal (today's de facto monitoring) | `OPERATIONAL` |
| Formal SLO tracking | `PLANNED` |
| On-call paging system | `PLANNED` |
| Dedicated monitoring dashboard and alert thresholds | `PLANNED` |
| Routine task cadence (daily/weekly items) | `PLANNED`, mostly informal today |
| Quarterly funder reporting | `OPERATIONAL` |
| Backup restoration testing | `PLANNED` |
| Curator onboarding/offboarding formal process | `PLANNED` |
| Full disaster-recovery drill | `FUTURE` |

---

### 11.13  Closing Note: How This Series Fits Together

This is the eighth normative document in the Dark Data Medicine Platform Architecture Series, following the Architectural Vision (Ch.2), High-Level System Architecture (Ch.3), Component Architecture (Ch.4), Domain Model (Ch.5), Ontology Specification (Ch.6), API Specification (Ch.7), Security Architecture (Ch.8), Deployment Architecture (Ch.9), and Developer Guide (Ch.10). Read end to end, the series answers, in order: why the system exists and what it must never compromise on (Ch.2); how its pieces fit together at the highest level (Ch.3); exactly what each piece does (Ch.4); what the pieces are actually about, scientifically, independent of any technology (Ch.5); how that scientific vocabulary is formally governed (Ch.6); how anything outside the system talks to it (Ch.7); how it defends itself and what it must never leak (Ch.8); where it actually runs (Ch.9); how a new engineer joins and contributes (Ch.10); and, in this final chapter, how it is kept running once all of the above is real.

The `OPERATIONAL` / `PLANNED` / `FUTURE` discipline that runs through every one of these documents was not a stylistic choice — it is this entire series' central claim, restated nine times: that an infrastructure project asking researchers, curators, and funders to trust it with the specific problem of undisclosed, unverifiable claims (Chapter 2 §2.1) has no credible option but to hold its own documentation to that exact standard. Every chapter in this series can be checked against the live repository. That correspondence, more than any diagram, table, or design principle in the preceding pages, is the actual architecture this project is built on.
