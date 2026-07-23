# Dark Data Medicine — Platform Architecture Series

## Chapter 16: Performance Architecture

*Document status: Normative. Governed by Chapter 3 (§3.10 Scalability Strategy, §3.15 Quality Scenarios), Chapter 4 (per-service Metrics/Scaling sections), Chapter 9 (§9.5, Scaling and Resource Management), Chapter 11 (§11.2, SLOs; §11.8, Capacity Planning), and Chapter 15 (§15.11, which deferred full performance-testing specification to this chapter). This is the final normative document in the extended series.*

*Version 0.1 — Draft for governance review*

---

### 16.0  Purpose and Scope

Chapter 11 §11.2 stated SLO targets in a single row per service. Chapter 4 gave each service a one-line Scaling note. Chapter 9 §9.5 sketched a scaling approach per infrastructure stage. This chapter is where those scattered performance commitments become one coherent latency budget, one caching architecture, one capacity-planning model with actual math behind the stage-transition thresholds Chapter 3 §3.10 named but did not quantify, and one load-testing methodology concrete enough to actually run.

**This chapter's honesty commitment.** There is no production traffic today — Stage 1 (Chapter 9 §9.2.1) is a static site with no meaningful load profile to measure. Every latency target and capacity threshold in this chapter is therefore a **design target**, stated as such, to be validated against real measurement once each corresponding component reaches `OPERATIONAL` status — not a claim about current, measured performance.

---

### 16.1  Performance Philosophy

1. **Measure before optimizing, but budget before building.** These are not in tension: a performance *budget* (§16.2) is a design constraint set before implementation, informing architectural choices (e.g., static-first search, §16.4); performance *optimization* is something done only in response to actual measurement against that budget, never speculatively, per Chapter 2 §2.11's principle that a change must be justifiable on both scientific and technical grounds — an unmeasured "optimization" is not technically justified.
2. **The static-first architecture is already this platform's single largest performance decision, made before this chapter existed.** Chapter 3 §3.4.3's choice to serve search from a CDN-cached static index rather than a live query service is not merely a resilience decision (Chapter 3 §3.12) — it is also, definitionally, a performance decision: a CDN-edge-cached response has a latency floor no live backend query can beat. This chapter's job for Stage 2+ is to preserve that property as new capability is added, not to discard it in the name of "real" infrastructure.
3. **Latency budgets are allocated, not discovered.** Chapter 16 §16.3's request-chain budget is set deliberately, top-down, before any component is built — a component whose implementation cannot fit its allocated budget is a signal to revisit the component's design, not to silently blow the budget and call it acceptable.

---

### 16.2  Performance Requirements and Budgets

Extending Chapter 11 §11.2's SLO table with full percentile targets, per service:

| Service (Ch.4 ref) | p50 Target | p95 Target | p99 Target | Throughput Target |
|---|---|---|---|---|
| Search (§4.3) — public query | 50ms (CDN-cached) / 150ms (live query) | 100ms / 400ms | 200ms / 800ms | 500 req/s at Stage 3 |
| Submission (§4.1) — create | 200ms | 600ms | 1200ms | 50 req/s |
| Review (§4.8) — decision write | 150ms | 400ms | 800ms | Bound by curator concurrency, not infra |
| Metadata (§4.2) — retrieve | 50ms | 150ms | 300ms | 300 req/s |
| Knowledge Graph (§4.4) — neighbor query | 100ms | 500ms | 1500ms | 100 req/s (higher variance expected — graph traversal cost scales with result fan-out) |
| AI (§4.5) — summarize (real-time) | 800ms | 2000ms | 4000ms | Bound by GPU pool capacity (Ch.9 §9.5), not a fixed req/s target |
| AI (§4.5) — embedding (batch) | N/A (batch, not latency-sensitive per-request) | N/A | N/A | 1,000 entries/hour minimum batch throughput |
| Authentication (§4.6) — token validate | 5ms (stateless JWT check) | 15ms | 30ms | 2,000 req/s — hot path for every authenticated request |
| Federation (§4.12) — sync message | 500ms per message | 2000ms | 5000ms | Bound by peer count, not a single fixed target |

**Why Authentication's budget is the tightest.** Restated from Chapter 4 §4.6's own note: this service sits on the hot path of every authenticated request across all eighteen other services, so its latency compounds into every other service's own budget — a 30ms p99 here is a deliberately conservative target specifically because it is a shared cost, not an isolated one.

---

### 16.3  End-to-End Latency Budget: Worked Example

Decomposing the Search query path (Chapter 3 §3.1's request flow) into an allocated budget, illustrating §16.1 principle 3's "allocated, not discovered" approach:

```
Total budget (p95, live query path): 400ms
  ├─ API Gateway (TLS termination, rate-limit check, routing): 10ms
  ├─ Authentication (token validation, if authenticated request): 15ms
  ├─ Search Service query construction + facet parsing: 15ms
  ├─ OpenSearch query execution: 150ms
  ├─ (If semantic search enabled) AI Service embedding lookup: 100ms
  ├─ Result assembly + Knowledge Graph neighbor enrichment: 80ms
  └─ Response serialization + network: 30ms
                                              Total: 400ms ✓ (at budget)
```

A component that cannot fit its allocated slice — for instance, if OpenSearch query execution measures at 250ms in practice — triggers one of three responses, in priority order: (1) query/index optimization (§16.5) to bring the component back within budget; (2) budget reallocation from a component currently running under its own allocation, if the total remains within the 400ms ceiling; or (3), only if neither suffices, a revision of the total budget itself, which — per §16.1 principle 3 — is a design decision requiring the same governance visibility (Chapter 2 §2.6) as any other architectural change, not a quiet SLO downgrade.

---

### 16.4  Caching Strategy

| Layer | What's Cached | TTL / Invalidation | Status |
|---|---|---|---|
| CDN edge (search index) | The full static search index | Invalidated on every `deploy-site.yml` run (Chapter 3 §3.4.3) | `OPERATIONAL` |
| CDN edge (published entries, Stage 2+) | Individual entry API responses | Invalidated on `MetadataGenerated` for that entry (Chapter 3 §3.7) — event-driven invalidation, not a blind TTL, since a stale published entry is a data-integrity concern (Chapter 2 §2.9), not merely a UX one | `PLANNED` |
| API Gateway response cache | Common, unauthenticated GET requests (ontology term lookups, Chapter 6 §6.3) | Short TTL (5 min) + event-driven invalidation on `OntologyVersionPublished` (Chapter 4 §4.13) | `PLANNED` |
| Application-level query cache | Expensive Knowledge Graph traversal results (Chapter 4 §4.4) | Event-driven invalidation on `KnowledgeGraphUpdated` | `FUTURE` |
| Embedding cache | Generated embeddings, keyed by entry version (Chapter 12 §12.4) | Never expires by TTL — invalidated only by entry re-versioning, since a given entry-version's embedding is deterministic and immutable per Chapter 2 §2.9 | `FUTURE` |
| Ontology term cache (Chapter 6 §6.13) | The full, small, read-heavy controlled-vocabulary set | Long TTL, event-driven invalidation on vocabulary version change | `PLANNED` |

**Cache-invalidation philosophy, stated once because it recurs across every row above.** Every cache in this architecture is invalidated by an explicit domain event (Chapter 3 §3.7), never by a blind TTL alone where an event exists to trigger correctly — a stale cache entry in a scientific registry is not a minor UX defect, it is a specific instance of the dataset-integrity risk Chapter 8 §8.2.1 named as this platform's highest-value asset, and TTL-only invalidation would silently reintroduce that risk for the sake of implementation simplicity.

---

### 16.5  Database Performance

- **Indexing strategy.** Every field used in a Chapter 7 §7.4 filter or sort parameter is indexed by design, not added reactively after a slow-query report — `domain`, `institution_type`, `date_concluded`, and the Knowledge Graph's entity-reference foreign keys are indexed from the first PostgreSQL migration that introduces them (Chapter 3 §3.8), because retrofitting an index onto a large table is a far more disruptive operation than including it in the original schema migration.
- **Connection pooling**, `PLANNED` from Stage 2 onward, sized to the concurrent-service count from Chapter 4's nineteen services, preventing the specific, well-known failure mode of connection-limit exhaustion under load that Chapter 9 §9.5 flags as something to address "ahead of, not reactively after," an incident.
- **Read-replica routing** (Chapter 3 §3.11): read-heavy services (Search, Analytics, Export — Chapter 4 §4.3, §4.11, §4.14) route to replicas by default; only services requiring read-after-write consistency within the same request (Review Service confirming its own just-written decision, Chapter 4 §4.8) route to the primary.
- **Query performance regression testing** (Chapter 15 §15.13's gating table, extended here): every migration that could plausibly affect a query plan for an indexed, budget-governed query (§16.2) runs against a representative-scale dataset in CI before merge, not only a small local development dataset where a missing-index regression would not be visible.

---

### 16.6  Load Testing Methodology

| Test Type | Purpose | Scenario |
|---|---|---|
| **Baseline** | Establish current performance under expected normal load | Steady traffic at the projected current-stage volume (Chapter 11 §11.8's capacity-planning signals) |
| **Stress** | Find the actual breaking point, not just the target threshold | Traffic ramped until a defined SLO (§16.2) is breached; the breaking point, not the target, informs the next stage-transition threshold (§16.7) |
| **Soak** | Detect slow degradation invisible to short tests (memory leaks, connection-pool exhaustion, cache-eviction thrash) | Sustained moderate load over an extended window (24+ hours), run at least ahead of every major version release (Chapter 7 §7.2) |
| **Spike** | Verify graceful handling of sudden traffic surges (e.g., a registry entry going viral in research-community discussion) | Sudden 10× traffic increase over a short window, sustained briefly, verifying rate limiting (Chapter 7 §7.8) and autoscaling (Chapter 9 §9.5) respond correctly rather than cascading into failure |

**Tooling** is specified as a capability (scriptable, repeatable, CI-integrable HTTP/GraphQL load generation) rather than tied to a specific product, per Chapter 2 §2.8's Technology Independence principle — any tool satisfying that capability (k6, Locust, or an equivalent) is conformant.

**Cadence.** Baseline and stress tests run against Staging before every major release (Chapter 9 §9.4); soak tests run on the schedule in Chapter 11 §11.5; spike tests run at least quarterly, aligned with the platform's own governance review cadence (Chapter 11 §11.10).

---

### 16.7  Capacity Planning Model

Extending Chapter 11 §11.8's signal table with the actual projection logic behind each stage-transition trigger:

```
Stage 1 → 2 trigger:
   Sustained curator-facing need for live API submission (Ch.7 §7.5.1)
   rather than Git PR-based submission — a workflow threshold, not a
   pure volume threshold, reached when curator time-to-decision (Ch.11
   §11.2) begins measurably suffering from PR-based friction rather
   than curation-capacity limits.

Stage 2 → 3 trigger (quantified):
   Projected API p95 latency, extrapolated from Stage 2's own load-test
   results (§16.6) against projected entry-count and query-volume growth
   (Ch.4's funding-case KPI targets), crossing 150% of the Stage 2
   budget (§16.2) at projected 12-month volume — reviewed quarterly
   (§16.6's cadence) against updated growth projections, not set once
   and forgotten.

Stage 3 → 4 trigger:
   Not a performance threshold at all, but a partnership-readiness
   threshold (Ch.11 §11.8) — federation exists to serve signed
   institutional partnerships, and its trigger is organizational,
   not a load figure this chapter can quantify.

Stage 4 → 5 trigger:
   Federated node count and cross-node query volume reaching a scale
   where the Knowledge Graph Service's cross-network reasoning
   (Ch.3 §3.14) becomes the binding constraint rather than any single
   node's own capacity — a threshold that, honestly, cannot be
   precisely quantified until Stage 4 itself provides real federated-
   network measurement to model against.
```

**Why Stage 3's trigger is the only one given a precise number.** It is the only transition in this list whose driver is a measurable technical quantity (latency under projected load) rather than an organizational, partnership, or genuinely-not-yet-measurable network-scale condition — this chapter resists the temptation to assign false numeric precision to triggers that are not, in fact, precisely quantifiable yet, consistent with the honesty standard this series has held throughout.

---

### 16.8  Performance Regression Testing

Integrated into Chapter 15 §15.13's CI gating table as an additional row: every pull request affecting a budget-governed code path (§16.2, §16.3) runs a lightweight automated benchmark against the previous commit's baseline, failing CI if p95 latency regresses by more than 20% without an explicit, reviewed justification in the pull request — a deliberate threshold chosen to catch real regressions without generating false-positive noise from ordinary measurement variance. Historical benchmark trends are retained and visualized (via the Analytics Service, Chapter 4 §4.11, once `OPERATIONAL`) so that a slow, cumulative regression across many individually-small, individually-justified changes remains visible even when no single change trips the 20% gate.

---

### 16.9  AI and Inference Performance

Extending Chapter 12 §12.11's cost/resource split with concrete performance targets:

- **Real-time inference** (curator-facing classification suggestions, on-demand summarization, Chapter 12 §12.2): governed by the AI row in §16.2's budget table — an 800ms p50 target chosen specifically to remain within the range a curator experiences as "responsive" during active review work, per the Curator Operations concern named in Chapter 11 §11.9.
- **Batch inference** (embedding generation for newly published entries): governed by throughput, not latency — the 1,000 entries/hour minimum in §16.2 is sized against the platform's own funding-case entry-volume projections (roughly 500 entries/month at Phase 1 scale), giving substantial headroom rather than a tightly-fit target, deliberately, since batch inference cost scales with GPU-hour spend (Chapter 9 §9.5) and overprovisioning batch throughput is cheaper than underprovisioning it during a curation-volume surge.
- **GPU utilization target**, `FUTURE`: 60–80% average utilization on the dedicated GPU node pool (Chapter 13 §13.3.2) — high enough to justify the dedicated pool's cost, low enough to retain headroom for real-time request bursts without queueing delay.

---

### 16.10  Federation Performance

Extending Chapter 4 §4.12's sync-latency metric with a concrete target: sync message propagation from origin node to all currently-connected peer nodes within the 5,000ms p99 target stated in §16.2's Federation row, monitored per-node (Chapter 4 §4.12's per-node sync-lag metric, alerting at the 1-hour/6-hour thresholds set in Chapter 11 §11.4). Cross-node federated query performance (a query spanning the primary node and multiple mirrors simultaneously, per Chapter 3 §3.14's semantic-reasoning-across-the-federation direction) is explicitly out of scope for a firm numeric target in this chapter, for the same honesty reason given in §16.7: it cannot be meaningfully budgeted before Stage 4 exists to measure against.

---

### 16.11  Performance Quality Scenarios (ATAM-style, extending Ch.3 §3.15, Ch.8 §8.14)

**Graceful degradation under load.** *Stimulus:* traffic exceeds the Stage's provisioned capacity during a spike test (§16.6). *Response:* rate limiting (Chapter 7 §7.8) sheds excess load at the Gateway before it reaches backing services; the static-index CDN fallback (§16.4, Chapter 3 §3.12) continues serving search regardless of backend Search Service load. *Response Measure:* p95 latency for accepted requests remains within budget (§16.2) even while some requests are rejected by rate limiting, rather than every request slowing down uniformly.

**Cache-invalidation correctness under concurrent updates.** *Stimulus:* an entry is corrected (new version, Chapter 2 §2.9) while under moderate read traffic. *Response:* the event-driven cache invalidation (§16.4) ensures no reader receives a mixed or stale state — either the pre-correction or post-correction version, never a partially-updated hybrid. *Response Measure:* zero observed inconsistent-read incidents in a targeted concurrency test exercising this exact race condition.

**Cost-performance efficiency at scale.** *Stimulus:* entry count grows 10× within a single infrastructure stage, before the next stage transition (§16.7) is triggered. *Response:* horizontal autoscaling (Chapter 9 §9.5) and read-replica routing (§16.5) absorb the growth within the current stage's architecture, without requiring an emergency, unplanned stage transition. *Response Measure:* the platform completes at least one full order-of-magnitude of entry-count growth within each stage before that stage's own capacity-planning trigger (§16.7) fires, validating that the staged model (Chapter 3 §3.10) is sized with reasonable headroom rather than requiring transitions more frequently than planned.

---

### 16.12  Implementation Status Summary

| Component | Status |
|---|---|
| Latency budgets (§16.2–§16.3) | `PLANNED` (design targets; no live traffic to measure against yet) |
| CDN-edge caching (static index) | `OPERATIONAL` |
| Event-driven cache invalidation (Stage 2+) | `PLANNED` |
| Database indexing strategy | `PLANNED` (no live PostgreSQL deployment yet) |
| Load testing (baseline/stress/soak/spike) | `PLANNED` |
| Capacity-planning model (§16.7) | `PLANNED` — logic specified; requires Stage 2 real measurement to calibrate |
| Performance regression testing in CI | `PLANNED` |
| AI inference performance targets | `FUTURE` (depends on Ch.12) |
| Federation sync performance monitoring | `FUTURE` (depends on Ch.4 §4.12) |

---

### 16.13  Closing Note: The Extended Series

This is the fifteenth normative or reference document in the Dark Data Medicine Platform Architecture Series: Architectural Vision (Ch.2), High-Level System Architecture (Ch.3), Component Architecture (Ch.4), Domain Model (Ch.5), Ontology Specification (Ch.6), API Specification (Ch.7), Security Architecture (Ch.8), Deployment Architecture (Ch.9), Developer Guide (Ch.10), Operations Manual (Ch.11), AI Services Architecture (Ch.12), Deployment Implementation Reference (Ch.13), Security Implementation Reference (Ch.14), Testing Architecture (Ch.15), and this chapter.

Chapter 11 §11.13 already stated this series' central claim once; it is worth restating here, now that the series is materially larger, because the risk of the claim quietly becoming false grows with every added chapter: every `OPERATIONAL` tag in these fifteen documents can be checked against the live repository, and every `PLANNED` or `FUTURE` tag is an honest statement of intent, not a description of something already built. A 40,000-word or a 400,000-word architecture series is not, by itself, evidence of a serious infrastructure project — plenty of unbuilt vaporware has thick documentation. What makes this series worth the pages it occupies is narrower and more falsifiable than its length: that a reader can pick any claim in it, go look at the actual code, and find that the claim was true.
