# Dark Data Medicine — Platform Architecture Series

## Chapter 4: Component Architecture

*Document status: Normative. Governed by Chapter 2 (Architectural Vision) and Chapter 3 (High-Level System Architecture). Each service specified here inherits the layering discipline of Ch.3 §3.2, the event vocabulary of Ch.3 §3.7, and the storage technologies of Ch.3 §3.8.*

*Version 0.1 — Draft for governance review*

---

### 4.0  How This Chapter Is Organized

Chapter 3 named nineteen services and described how they fit together. This chapter specifies each one individually, to a single uniform template, so that any two services can be compared on equal terms and so that a new engineer assigned to any one service can find everything they need in one place without reading the whole chapter.

**The template, applied to every service below:**

| Field | Answers |
|---|---|
| **Purpose** | One sentence: why this service exists |
| **Responsibilities** | The specific things it does (and, implicitly, does not) |
| **Inputs** | What triggers it, and through which channel |
| **Outputs** | What it produces |
| **Internal Workflow** | The step-by-step path a request takes through the service |
| **Dependencies** | Which other services and infrastructure it requires |
| **Security** | Authentication, authorization, and validation posture |
| **Database** | Which tables/collections it owns or reads |
| **API** | Its externally callable surface |
| **Events** | What it emits onto the Event Bus (Ch.3 §3.7) |
| **Metrics** | What is measured to know it is healthy |
| **Scaling** | How it grows under load |
| **Implementation Status** | `OPERATIONAL` / `PLANNED` / `FUTURE`, per Ch.3 §3.0 |

**A note on ownership boundaries.** Per Chapter 3 §3.2's layering rule, a service **owns** the tables it writes to and **may read** tables owned by services it legitimately depends on, but never writes to a table owned by another service — cross-service writes always happen by emitting an event and letting the owning service act on it. This single rule is what keeps nineteen services from silently becoming one tangled service over time, and it is worth stating once, here, rather than repeating in every section below.

---

### 4.1  Submission Service

**Purpose.** Serve as the sole entry point through which a candidate negative-result finding enters the platform, in any form — structured form, raw JSON, or automated registry extraction — and determine its structural admissibility before anything downstream ever sees it.

**Responsibilities.**
- Accept a candidate entry from any input channel (§Inputs below).
- Enforce Zero Trust (Ch.2 §2.3.7): validate every field against the current schema version regardless of the submitter's authenticated identity or role.
- Create an immutable, versioned submission record — never mutate a prior version in place.
- Route validated submissions into the human curation queue (Review Service, §4.8).
- Emit lifecycle events at every state transition.

**Inputs.**
| Channel | Description | Status |
|---|---|---|
| REST `POST /submissions` | Structured JSON submission | `PLANNED` |
| GraphQL mutation `createSubmission` | Same, for clients already using GraphQL for reads | `PLANNED` |
| CLI (`ddm submit entry.json`) | Local file submission by a technical contributor | `PLANNED` |
| Git pull request | Current production path: a JSON file added under `data/<domain>/` | `OPERATIONAL` |
| Automated import | Draft entries from the Import Service (§4.15), sourced via `clinicaltrials_seed_extractor.py` | `OPERATIONAL` (extraction) / `PLANNED` (as a routed service call) |

**Outputs.** A submission identifier (globally unique, per Ch.2 §2.6 principle 1); a structural validation verdict; a routed curation-queue entry.

**Internal Workflow.**
```
Request received
      |
      v
Authentication check           (who is submitting — may be anonymous, no-Git path)
      |
      v
Authorization check            (is this submitter permitted to submit to this domain)
      |
      v
Rate-limit check                (per-submitter throttle, prevents automated flooding)
      |
      v
Schema validation                (Draft-07 JSON Schema — OPERATIONAL today via
      |                           validate_submission.py)
      v
Duplicate pre-check               (fast heuristic match against existing entries;
      |                           full duplicate judgment remains a Review Service /
      |                           human curator decision, never automated alone)
      v
Persist versioned submission record
      |
      v
Emit SubmissionCreated / SubmissionValidated / SubmissionRejected
      |
      v
Route to curation queue (Review Service)
```

**Dependencies.** Authentication Service (§4.6, identity of submitter where not anonymous); Storage Layer (submission records); Audit Service (§4.16, immutable log of every submission event); Notification Service (§4.7, submitter acknowledgment).

**Security.**
- JWT-based session tokens for authenticated submission channels; anonymous submission permitted only through the no-Git path, consistent with Ch.2 §2.3.6's accessibility commitment, but always subject to the identical validation and rate-limit gates.
- RBAC distinguishes `Contributor` (may submit) from `Curator`/`Curation Lead` (may act on the curation queue) — the Submission Service enforces the former only; the latter is the Review Service's concern.
- Every field is re-validated server-side regardless of any client-side validation already performed — client validation is a UX convenience, never a trust boundary.

**Database.** Owns: `submissions`, `submission_versions`. Reads: `schema_versions` (Metadata Service-owned, §4.2), `users` (Authentication Service-owned, §4.6).

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/submissions` | `POST` | Create a submission |
| `/submissions/{id}` | `GET` | Retrieve a submission and its version history |
| `/submissions/{id}/versions` | `GET` | List all versions of a submission |
| `/submissions/{id}/status` | `GET` | Current curation-queue status |

**Events.** `SubmissionCreated`, `SubmissionValidated`, `SubmissionRejected` (structural failure only — curatorial rejection is emitted by the Review Service, §4.8, not here).

**Metrics.** Submission latency (p50/p95/p99); validation failure rate by field (surfaces schema fields that are frequently misunderstood, informing documentation improvements); throughput (submissions/hour); rejection rate by channel (flags whether a specific input channel, e.g. automated import, produces disproportionately low-quality drafts).

**Scaling.** Stateless — horizontally scaled behind the API Gateway (Ch.3 §3.1) with no service-local state; validation is CPU-bound and embarrassingly parallel across concurrent submissions; no caching required at this service (validation must always run against the current schema, never a cached prior result).

**Implementation Status.** `OPERATIONAL` as a CI-triggered script pipeline; `PLANNED` as a standalone networked service exposing the API above.

---

### 4.2  Metadata Service

**Purpose.** Generate, validate, and export FAIR-compliant metadata (Ch.2 §2.3.1–§2.3.2) for every entity in the system.

**Responsibilities.** Enrich a validated submission with standards-conformant metadata (controlled-vocabulary tagging, persistent-identifier assignment); validate metadata completeness against the current schema version; produce exports in open formats (JSON-LD, CSV, DataCite XML).

**Inputs.** `SubmissionValidated` and `SubmissionApproved` events; direct export requests via the API.

**Outputs.** Structured metadata records; export artifacts.

**Internal Workflow.**
```
SubmissionApproved event received
      |
      v
Load current schema + controlled vocabularies (Ontology Service, §4.13)
      |
      v
Generate metadata record  (Dublin Core / DataCite-mappable fields)
      |
      v
Validate completeness
      |
      v
Persist metadata record
      |
      v
Emit MetadataGenerated
```

**Dependencies.** Ontology Service (controlled vocabularies); Storage Layer; DOI Service (§4.9, for identifier assignment at release time).

**Security.** Read access to metadata is public by default (Ch.2 §2.3.5, Open Science First); write access restricted to the service itself, acting only in response to legitimate upstream events — no direct external write path to metadata records.

**Database.** Owns: `metadata_records`, `controlled_vocabulary_mappings`. Reads: `submissions` (Submission Service-owned), `ontology_terms` (Ontology Service-owned).

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/entries/{id}/metadata` | `GET` | Retrieve an entry's structured metadata |
| `/entries/{id}/export` | `GET` | Export in a requested open format (`?format=json-ld\|csv\|datacite-xml`) |

**Events.** `MetadataGenerated`.

**Metrics.** Metadata-generation latency; export request volume by format (informs which format to prioritize for further tooling investment); vocabulary-mapping miss rate (a free-text field that fails to map onto a controlled term flags an Ontology Service gap).

**Scaling.** Stateless; horizontally scaled; export-format rendering is cacheable per entry version, since a published entry's metadata does not change until a new version is released (Ch.2 §2.9, Immutable Releases).

**Implementation Status.** `PLANNED`. Current partial equivalent: `export_to_excel.py`, a manual, single-format export script.

---

### 4.3  Search Service

**Purpose.** Make every published entry discoverable through full-text, faceted, and (once the AI Service is live) semantic search.

**Responsibilities.** Index published entries; serve query requests with ranking and faceted filtering; maintain index freshness as entries are published or updated.

**Inputs.** `MetadataGenerated` and `KnowledgeGraphUpdated` events; direct search queries via the API and the web portal.

**Outputs.** Ranked, faceted result sets.

**Internal Workflow.**
```
MetadataGenerated event received
      |
      v
Transform entry into index document
      |
      v
Write to index  (OpenSearch, once live; static JSON index today)
      |
      v
Emit SearchIndexed

--- separately, on each query ---

Query received
      |
      v
Parse facets + full-text terms
      |
      v
Execute index query
      |
      v
(If AI Service live) blend semantic ranking with lexical ranking
      |
      v
Return ranked results
```

**Dependencies.** Metadata Service; Knowledge Graph Service (for entity-neighbor context in results, `FUTURE`); AI Service (semantic ranking, `FUTURE`).

**Security.** Read-only public endpoint by default (Ch.2 §2.3.5); no authentication required for search, consistent with the platform's open-by-default posture; query rate-limited to prevent scraping abuse of the underlying dataset in bulk outside the documented export path (§4.2).

**Database.** Owns: the search index itself (OpenSearch, `PLANNED`) or the static JSON index (`OPERATIONAL`). Reads: `metadata_records`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/search` | `GET` | Full-text + faceted query |
| `/search/facets` | `GET` | Available facet values and counts |

**Events.** `SearchIndexed`.

**Metrics.** Query latency; zero-result-query rate (surfaces vocabulary or coverage gaps); index staleness (time between `MetadataGenerated` and the entry becoming queryable).

**Scaling.** Stateless query layer, horizontally scaled; index itself sharded once entry volume passes the Stage 2→3 threshold defined in Ch.3 §3.10; heavily cached at the CDN edge for the current static-index implementation, which is — as noted in Ch.3 §3.12 — a deliberate resilience property worth retaining even after the OpenSearch migration.

**Implementation Status.** `OPERATIONAL` as a static index (`generate_search_index.py`); `PLANNED` as a dedicated OpenSearch-backed service.

---

### 4.4  Knowledge Graph Service

**Purpose.** Maintain the entity-relationship graph connecting experiments to diseases, interventions, institutions, funding, publications, and replications, enabling multi-hop queries no relational store expresses naturally.

**Responsibilities.** Resolve entity references in a metadata record onto graph nodes (entity linking); create and maintain graph edges; serve graph-traversal queries; detect and surface potential duplicate or related entries via graph proximity.

**Inputs.** `MetadataGenerated` events; direct graph queries via the API.

**Outputs.** Graph query results; candidate-duplicate signals passed to the Review Service (§4.8) as a decision aid, never as an automatic merge or rejection.

**Internal Workflow.**
```
MetadataGenerated event received
      |
      v
Entity linking  (map free-text fields to Ontology-controlled entity nodes)
      |
      v
Create/update graph nodes and edges
      |
      v
Run duplicate-proximity check  (graph-distance heuristic)
      |
      v
Emit KnowledgeGraphUpdated
      |
      v
(If proximity above threshold) flag for curator review — advisory only
```

**Dependencies.** Ontology Service (entity vocabulary); Metadata Service; AI Service (entity-linking assistance, `FUTURE`).

**Security.** Read access public by default; write access restricted to the service acting on legitimate upstream events; any AI-assisted entity-linking suggestion is logged with its confidence score and is always subject to human confirmation before a graph edge is treated as curator-verified — a direct application of Ch.2 §2.9's Human Accountability principle.

**Database.** Owns: the graph store (Neo4j or equivalent). Reads: `ontology_terms`, `metadata_records`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/graph/entity/{id}/neighbors` | `GET` | Entities connected to a given node |
| `/graph/query` | `POST` | Arbitrary graph-traversal query (Cypher-equivalent, exposed via a documented, sandboxed query language) |

**Events.** `KnowledgeGraphUpdated`.

**Metrics.** Entity-linking confidence distribution; graph query latency; unresolved-entity rate (free-text values that fail to link to any known node — an Ontology Service growth signal).

**Scaling.** Read replicas for query-heavy workloads; graph writes batched per metadata-update event rather than per individual edge to avoid write amplification at scale.

**Implementation Status.** `FUTURE`.

---

### 4.5  AI Service

**Purpose.** Provide embedding generation, semantic search support, retrieval-augmented generation (RAG), summarization, classification, and entity-linking assistance across the corpus.

**Responsibilities.** Generate and maintain vector embeddings for every published entry; support semantic query expansion for the Search Service; produce entry summaries; propose (never finalize) classification and entity-linking suggestions.

**Inputs.** `MetadataGenerated` events; direct inference requests via the API.

**Outputs.** Vector embeddings; summaries; classification and linking suggestions with confidence scores.

**Internal Workflow.**
```
MetadataGenerated event received
      |
      v
Generate embedding  (entry text + structured fields)
      |
      v
Write to Vector Database
      |
      v
Emit EmbeddingGenerated
      |
      v
(On demand) generate summary / classification suggestion
      |
      v
Return to caller with confidence score — advisory only, per Zero Trust (Ch.2 §2.3.7)
```

**Dependencies.** Search Service (consumes embeddings for semantic ranking); Knowledge Graph Service (consumes entity-linking suggestions); Vector Database.

**Security.** Every AI-generated output is labeled as such and carries a confidence score; no AI output is permitted to alter the canonical dataset without passing through the same human curation gate as any other change (Ch.2 §2.9); model inference requests are rate-limited and logged for cost and abuse monitoring.

**Database.** Owns: vector embeddings store. Reads: `metadata_records`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/ai/summarize/{entryId}` | `GET` | Retrieve a generated summary |
| `/ai/similar/{entryId}` | `GET` | Semantically similar entries |
| `/ai/classify` | `POST` | Suggest domain/classification for draft text (curation aid) |

**Events.** `EmbeddingGenerated`.

**Metrics.** Inference latency; embedding coverage (% of published entries with a current embedding); suggestion-acceptance rate by curators (the single most important quality signal for this service, since it measures whether AI assistance is actually useful to the humans who remain accountable for every decision).

**Scaling.** GPU-backed inference workers, horizontally scaled and queued; embedding generation is batchable and does not need to block the publication path (§3.5, event-driven decoupling).

**Implementation Status.** `FUTURE`.

---

### 4.6  Authentication Service

**Purpose.** Authenticate every actor interacting with the platform and authorize their actions by role.

**Responsibilities.** Issue and validate session tokens; integrate ORCID as the primary researcher-identity provider; enforce multi-factor authentication for curator and administrative roles; maintain the role-permission matrix.

**Inputs.** Login requests (ORCID OIDC, or platform-local credentials for administrative roles); token-validation requests from every other service.

**Outputs.** Signed JWTs; token-validation verdicts; role/permission lookups.

**Internal Workflow.**
```
Login request  (ORCID OIDC redirect)
      |
      v
Identity provider callback verified
      |
      v
User record created/matched  (keyed on ORCID iD where present)
      |
      v
Role assigned/loaded  (default: Contributor)
      |
      v
JWT issued  (short-lived access token + refresh token)
      |
      v
Every subsequent service call: JWT validated + role checked against required permission
```

**Dependencies.** External ORCID OIDC provider; Storage Layer (user/role records); Audit Service (every authentication event logged).

**Security.** OIDC/OAuth2 for all researcher-facing authentication; MFA mandatory for `Curator`, `Curation Lead`, and `Administrator` roles; RBAC permission matrix versioned and auditable, per Ch.2 §2.6 principle 7 (every governance-relevant decision recorded); no service is permitted to bypass token validation, including internal services (Ch.2 §2.3.7, Zero Trust applied uniformly).

**Database.** Owns: `users`, `roles`, `role_permissions`, `sessions`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/auth/login` | `GET` | Initiate ORCID OIDC flow |
| `/auth/callback` | `GET` | OIDC callback handler |
| `/auth/token/refresh` | `POST` | Refresh an access token |
| `/auth/me` | `GET` | Current authenticated identity and role |

**Events.** `UserAuthenticated`, `UserRoleChanged` (extending the Ch.3 §3.7 vocabulary).

**Metrics.** Login success/failure rate; token-validation latency (this service is on the hot path of every authenticated request, so its latency budget is stricter than most); MFA adoption rate among curator/admin roles.

**Scaling.** Stateless token validation (JWT signature verification requires no database round-trip); session/refresh-token storage horizontally partitioned by user ID.

**Implementation Status.** `PLANNED`. Current equivalent: GitHub's native authentication and repository-permission model, for the technical PR-based contribution path only.

---

### 4.7  Notification Service

**Purpose.** Inform contributors, curators, and partner institutions of status changes relevant to them.

**Responsibilities.** Subscribe to lifecycle events across the platform; render and deliver notifications across configured channels (email, in-app, webhook); respect per-user notification preferences.

**Inputs.** `SubmissionCreated`, `SubmissionApproved`, `SubmissionRejected`, `CommentAdded`, `ReviewCompleted`, `DatasetUpdated`, `DOIAssigned`.

**Outputs.** Delivered notifications; delivery receipts.

**Internal Workflow.**
```
Event received from Event Bus
      |
      v
Look up subscribers for this event type + entity
      |
      v
Filter by user notification preferences
      |
      v
Render notification  (channel-specific template)
      |
      v
Deliver  (email / in-app / webhook)
      |
      v
Record delivery receipt (Audit Service)
```

**Dependencies.** Event Bus (Ch.3 §3.7); Authentication Service (user preference lookup); Audit Service.

**Security.** No sensitive entry content included in notification payloads beyond what is already public, since notifications may traverse less-trusted channels (e.g., email) than the platform's own API.

**Database.** Owns: `notification_preferences`, `notification_deliveries`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/notifications/preferences` | `GET`/`PUT` | Manage a user's notification settings |
| `/notifications` | `GET` | List a user's in-app notification history |

**Events.** None emitted (a terminal consumer of other services' events); logs delivery outcomes to the Audit Service.

**Metrics.** Delivery latency; delivery failure rate by channel; opt-out rate (a signal of notification-fatigue risk).

**Scaling.** Queue-based, horizontally scaled workers consuming from the Event Bus; email delivery batched to respect third-party mail-provider rate limits.

**Implementation Status.** `FUTURE`. Current equivalent: GitHub's native pull-request notifications, for technical contributors only.

---

### 4.8  Review Service

**Purpose.** Formalize the human curation workflow described narratively in the project's curation guide (Ch.3's `docs/CURATION_GUIDE.md`) as an explicit, stateful service.

**Responsibilities.** Maintain the curation queue; assign submissions to domain curators; track the curation checklist's completion state per submission; record the accountable curator of record for every decision (Ch.2 §2.9); escalate disagreements to the Curation Lead.

**Inputs.** `SubmissionValidated` events; curator actions via the review UI/API.

**Outputs.** `SubmissionApproved` or `SubmissionRejected` events; a permanent review record.

**Internal Workflow.**
```
SubmissionValidated event received
      |
      v
Enqueue in the relevant domain curator's queue
      |
      v
Curator opens submission
      |
      v
Curator works through checklist:
   - genuine negative/null outcome confirmed
   - duplicate check against Knowledge Graph proximity signal
   - source verifiability confirmed (where a public source is claimed)
   - PII screen passed
   - domain classification confirmed
      |
      v
Curator decision: Approve / Reject / Request changes
      |
      v
Record decision with curator identity (never anonymous, per Ch.2 §2.9)
      |
      v
Emit SubmissionApproved / SubmissionRejected / ReviewCompleted
```

**Dependencies.** Submission Service; Knowledge Graph Service (duplicate-proximity signal); Authentication Service (curator identity and role check); Notification Service (submitter outcome notification).

**Security.** Only users holding the `Curator` role for the relevant domain, or `Curation Lead`, may act on a queue item; every decision is permanently attributed and cannot be edited after the fact without creating a new, separately attributed correction record.

**Database.** Owns: `curation_queue`, `review_decisions`, `curation_checklist_state`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/review/queue` | `GET` | A curator's assigned queue |
| `/review/{submissionId}/decision` | `POST` | Record an approve/reject/request-changes decision |
| `/review/{submissionId}/checklist` | `GET`/`PUT` | Checklist completion state |

**Events.** `SubmissionApproved`, `SubmissionRejected`, `ReviewCompleted`.

**Metrics.** Queue depth by domain; time-to-decision (median and p95); inter-curator agreement rate (the same quality benchmark referenced throughout the platform's funding case); rejection reasons distribution (informs contributor-facing documentation improvements).

**Scaling.** Primarily human-throughput-bound rather than compute-bound; the service itself is lightweight and stateless, scaled to match curator concurrency rather than submission volume directly.

**Implementation Status.** `PLANNED`. Current equivalent: manual PR review against the written curation guide, without a dedicated queue or checklist-state tracking system.

---

### 4.9  DOI Service

**Purpose.** Mint, version, and maintain persistent identifiers for dataset releases and, where warranted, individual high-value entries.

**Responsibilities.** Package a finalized dataset snapshot; register it with Zenodo/DataCite; track DOI-to-version mappings; ensure every issued DOI remains resolvable indefinitely (Ch.2 §2.6, principle 15).

**Inputs.** `DatasetUpdated` events (release-trigger); direct release requests from the Program Lead role.

**Outputs.** A registered, resolvable DOI; a permanent version-to-DOI mapping record.

**Internal Workflow.**
```
Release triggered  (DatasetUpdated, release-scoped)
      |
      v
Snapshot current approved dataset state
      |
      v
Generate release metadata package  (via Metadata Service)
      |
      v
Submit to Zenodo/DataCite registration API
      |
      v
Receive and persist DOI
      |
      v
Emit DOIAssigned
      |
      v
Publish release notes + changelog entry
```

**Dependencies.** Metadata Service; external Zenodo/DataCite integration (Ch.3 §3.6); Storage Layer (immutable release snapshots).

**Security.** Release-triggering restricted to `Curation Lead`/`Administrator` roles; the DOI registration credentials themselves are held only by this service, never exposed to any client.

**Database.** Owns: `dataset_releases`, `doi_mappings`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/releases` | `GET` | List all versioned releases and their DOIs |
| `/releases/{version}` | `GET` | Retrieve a specific frozen release |
| `/releases` | `POST` | Trigger a new release (privileged) |

**Events.** `DOIAssigned`.

**Metrics.** Time from release-trigger to DOI registration; registration failure/retry rate.

**Scaling.** Low-volume, low-frequency operation (releases are periodic, not continuous); no horizontal-scaling concern.

**Implementation Status.** `PLANNED`.

---

### 4.10  Replication Service

**Purpose.** Track and link independent replication attempts of a registered negative result — a capability with no equivalent anywhere in the existing trial-registry or journal landscape described in the platform's funding case.

**Responsibilities.** Accept a replication-attempt submission referencing an existing entry; link it in the Knowledge Graph; surface replication status (unreplicated / replicated / contradicted) on the original entry's record.

**Inputs.** Replication submissions (structurally, a specialized Submission Service input referencing a parent entry ID).

**Outputs.** A linked replication record; an updated replication-status facet on the original entry.

**Internal Workflow.**
```
Replication submission received  (via Submission Service, tagged as replication type)
      |
      v
Validate parent-entry reference exists
      |
      v
Route through standard curation (Review Service)
      |
      v
On approval: create Knowledge Graph edge  (Replication --replicates--> Experiment)
      |
      v
Emit ReplicationAdded
      |
      v
Update original entry's replication-status facet (Search Service reindex)
```

**Dependencies.** Submission Service; Review Service; Knowledge Graph Service; Search Service.

**Security.** Same submission and curation security posture as any entry (§4.1, §4.8); no special privilege granted to replication submissions.

**Database.** Owns: `replications`. Reads: `submissions`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/entries/{id}/replications` | `GET` | List replication attempts for an entry |

**Events.** `ReplicationAdded`.

**Metrics.** Replication-attempt volume over time (an impact signal: a registry entry that attracts a replication attempt is directly influencing another researcher's work, the clearest possible evidence of the platform achieving its mission).

**Scaling.** Low volume relative to primary submissions; no distinct scaling concern beyond the shared Submission/Review pipeline.

**Implementation Status.** `FUTURE`.

---

### 4.11  Analytics Service

**Purpose.** Produce dashboards, KPIs, and impact metrics for internal operations, curator management, and funder reporting.

**Responsibilities.** Aggregate cross-service metrics (§4.1–§4.19's individual Metrics sections) into unified dashboards; compute the specific KPIs defined in the platform's funding case; support ad hoc trend queries.

**Inputs.** Metrics streams from every other service; direct dashboard/report requests.

**Outputs.** Dashboards; scheduled and on-demand reports; the CSV trend exports already in production use.

**Internal Workflow.**
```
Metrics streamed continuously from all services
      |
      v
Aggregated into time-series store
      |
      v
Dashboard queries served on demand
      |
      v
Scheduled report generation  (e.g., quarterly funder report)
```

**Dependencies.** Every other service, as a metrics consumer only — a strict read-only relationship that keeps Analytics from becoming an accidental source of truth for any operational state.

**Security.** Dashboard access role-gated by audience (public dashboards vs. internal operational dashboards vs. funder-specific reports); no entry-level PII risk since analytics operate on aggregate metrics, not individual patient data (which never enters the system per Ch.2 §2.3.6).

**Database.** Owns: `metrics_timeseries`, `saved_reports`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/analytics/dashboard/{name}` | `GET` | Retrieve a named dashboard's current data |
| `/analytics/report` | `POST` | Generate an ad hoc report |

**Events.** None emitted; a pure consumer.

**Metrics.** Dashboard load latency; report-generation time; (meta) — this service's own metrics collection completeness, since a gap here silently degrades every other service's visibility.

**Scaling.** Read-heavy, time-series-optimized storage; horizontally scaled query layer; write path (metric ingestion) is high-volume and append-only, well suited to a purpose-built time-series store separate from the relational Storage Layer described in Ch.3 §3.8.

**Implementation Status.** `PLANNED`. Current equivalent: on-demand execution of `analyze_trends.py`, producing static CSV reports rather than continuously updated dashboards.

---

### 4.12  Federation Service

**Purpose.** Synchronize entries and metadata across independently operated mirror nodes, realizing the twenty-year distributed vision of Ch.2 §2.2 and §2.10.

**Responsibilities.** Maintain a registry of known federated nodes; synchronize new and updated entries bidirectionally; resolve conflicts by provenance; preserve unambiguous originating-node attribution on every synchronized record (Ch.2 §2.9).

**Inputs.** Local `DatasetUpdated`/`SubmissionApproved` events (to propagate outward); incoming synchronization messages from peer nodes.

**Outputs.** Synchronized entries across the federated network; conflict-resolution records where two nodes independently modify related data.

**Internal Workflow.**
```
Local entry approved/updated
      |
      v
Package as a federation sync message  (entry + provenance + originating-node ID)
      |
      v
Broadcast to registered peer nodes
      |
      v
--- on receiving peer's side ---
Verify message signature + provenance
      |
      v
Check for conflicts against local state
      |
      v
Apply (or queue for manual conflict resolution)
      |
      v
Emit local KnowledgeGraphUpdated / SearchIndexed as appropriate
```

**Dependencies.** Every other service, indirectly, since federated sync ultimately touches the same entry lifecycle any locally submitted entry does; a dedicated cryptographic signing infrastructure for message provenance (aligned with the quantum-safe signature direction flagged in Ch.2 §2.10).

**Security.** Every inbound sync message is treated as untrusted input subject to the same Zero Trust validation as any other submission channel (Ch.2 §2.3.7); peer-node identity is cryptographically verified before any sync message is applied; a compromised or malicious peer node can be revoked from the federation registry without affecting any other node's operation.

**Database.** Owns: `federation_nodes`, `sync_log`, `conflict_resolutions`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/federation/nodes` | `GET` | List known federated nodes and their sync status |
| `/federation/sync` | `POST` | Peer-to-peer sync message endpoint (node-authenticated only) |

**Events.** `DatasetUpdated` (federation-scoped variant), plus internally re-emitting standard events as synchronized entries are applied locally.

**Metrics.** Sync latency between nodes; conflict rate; node uptime/health.

**Scaling.** Peer-to-peer by design — scaling is a property of the network topology (Ch.3 §3.10, Stage 4–5) rather than of any single node's compute capacity.

**Implementation Status.** `FUTURE`.

---

### 4.13  Ontology Service

**Purpose.** Own and evolve the controlled vocabularies — disease terms, intervention types, institution types, and their relationships — that every other service depends on for consistent classification.

**Responsibilities.** Maintain versioned controlled-vocabulary term sets; support term lookup, synonym resolution, and cross-vocabulary mapping (e.g., mapping a free-text disease name onto a standard ontology such as MeSH or SNOMED CT, a `FUTURE` integration); manage the deprecation and migration process for vocabulary changes (Ch.2 §2.6 principle 6).

**Inputs.** Vocabulary-change proposals (a governance-reviewed process, not a purely technical one); term-lookup requests from every other service.

**Outputs.** Resolved terms; vocabulary version history; migration mappings for deprecated terms.

**Internal Workflow.**
```
Vocabulary change proposed  (e.g., new domain category, new intervention type)
      |
      v
Governance review  (per Ch.2 §2.6, schema/vocabulary changes require documented rationale)
      |
      v
New vocabulary version published
      |
      v
Migration mapping generated for any deprecated term
      |
      v
Dependent services (Metadata, Knowledge Graph, Search) notified of the new version
```

**Dependencies.** None upstream (this is a foundational service); consumed by nearly every other service.

**Security.** Read access public and unauthenticated; write access (proposing or approving a vocabulary change) restricted to `Curation Lead`/`Administrator` roles and always subject to governance review, never a unilateral technical change.

**Database.** Owns: `ontology_terms`, `ontology_versions`, `term_mappings`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/ontology/terms` | `GET` | List/search controlled terms |
| `/ontology/terms/{id}/mappings` | `GET` | External-ontology cross-mappings (MeSH, SNOMED CT, etc.) |

**Events.** `OntologyVersionPublished` (extending the Ch.3 §3.7 vocabulary).

**Metrics.** Term-lookup latency (this service is on the hot path of Metadata and Knowledge Graph processing); unmapped-term rate (the primary signal that the vocabulary needs to grow).

**Scaling.** Small, read-heavy dataset relative to entry volume; aggressively cacheable, since vocabulary changes are infrequent and governance-reviewed rather than continuous.

**Implementation Status.** `PLANNED`. Current equivalent: the fixed enum lists embedded directly in the JSON Schema (`domain`, `institution_type`, intervention `type`), which is sufficient at the current scale but does not yet support synonym resolution or external-ontology mapping.

---

### 4.14  Export Service

**Purpose.** Provide bulk, programmatic, and format-flexible extraction of the dataset for reuse outside the platform, directly serving the Reusable half of FAIR (Ch.2 §2.3.1).

**Responsibilities.** Generate full-dataset and filtered-subset exports in multiple open formats; support scheduled/recurring exports for institutional partners with their own ingestion pipelines.

**Inputs.** Export requests via the API; scheduled export configurations.

**Outputs.** Downloadable or streamed export artifacts (JSON, CSV, JSON-LD, DataCite XML).

**Internal Workflow.**
```
Export request received  (full dataset or filtered query)
      |
      v
Query Storage Layer for matching, published entries only
      |
      v
Transform to requested format  (delegates rendering to Metadata Service, §4.2)
      |
      v
Stream/deliver artifact
      |
      v
Log export event  (Audit Service — who exported what, when)
```

**Dependencies.** Metadata Service (format rendering); Storage Layer.

**Security.** Exports never include unpublished or rejected submissions, regardless of the requester's role — the Export Service's read scope is hard-limited to the public, curator-approved dataset; large or scheduled exports are rate-limited and logged.

**Database.** No owned tables; reads `metadata_records` and published `submissions` only.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/export` | `GET` | One-off export (`?format=`, optional filters) |
| `/export/scheduled` | `POST`/`GET` | Manage a recurring export configuration |

**Events.** `ExportCompleted` (extending the Ch.3 §3.7 vocabulary, for audit purposes).

**Metrics.** Export volume by format and requester type; large-export completion time.

**Scaling.** Streaming response generation to avoid memory pressure on full-dataset exports as entry volume grows; scheduled exports executed by background workers decoupled from the request path.

**Implementation Status.** `PLANNED`. Current equivalent: `export_to_excel.py`, single-format and manually invoked.

---

### 4.15  Import Service

**Purpose.** Bring candidate entries into the platform from external sources at scale, always as unreviewed drafts (Ch.2 §2.9, Machine Validation is never a substitute for Human Accountability).

**Responsibilities.** Query external registries (ClinicalTrials.gov today; EU CTR, PubMed, and OpenAlex as `FUTURE` sources) for candidate terminated or negative-outcome studies; transform external records into draft submissions; explicitly flag every imported draft as machine-generated and unreviewed.

**Inputs.** Scheduled or on-demand import jobs targeting a configured external source.

**Outputs.** Draft submissions, routed through the identical Submission Service and Review Service pipeline as any other entry — never auto-merged (Ch.3 §3.4.1, §3.4.10 design constraint restated here as a hard rule).

**Internal Workflow.**
```
Import job triggered  (scheduled or manual)
      |
      v
Query external source API  (e.g., ClinicalTrials.gov)
      |
      v
Filter candidates  (terminated status, negative-outcome indicators)
      |
      v
Transform to draft submission JSON  (source_type: public_database_extraction)
      |
      v
Submit via standard Submission Service path  (§4.1)
      |
      v
Enters standard curation queue — no privileged fast path
```

**Dependencies.** Submission Service; external source APIs.

**Security.** Import jobs run under a dedicated, clearly identified system account — never impersonating a human contributor — so that every draft's origin is unambiguous to curators and auditors alike; external API credentials are held only by this service.

**Database.** Owns: `import_jobs`, `import_source_config`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/import/jobs` | `POST`/`GET` | Trigger and monitor import jobs |
| `/import/sources` | `GET` | List configured external sources |

**Events.** `ImportJobCompleted` (extending the Ch.3 §3.7 vocabulary).

**Metrics.** Candidates found per job; draft-to-approval conversion rate per source (the key quality signal distinguishing a high-value source from a noisy one).

**Scaling.** Batch/background-worker execution; naturally rate-limited by external-source API quotas rather than by the platform's own capacity.

**Implementation Status.** `OPERATIONAL` as a standalone script (`clinicaltrials_seed_extractor.py`); `PLANNED` as a scheduled, multi-source service integrated with the Submission Service API.

---

### 4.16  Audit Service

**Purpose.** Maintain an immutable, comprehensive log of every consequential action across the platform — the technical backbone of the Auditability quality attribute (Ch.2 §2.7) and the Transparency principle (Ch.2 §2.9).

**Responsibilities.** Record every state-changing action with actor, timestamp, and before/after state; guarantee log immutability (append-only, cryptographically chained where the future signature infrastructure in §4.12 is available); serve audit queries for governance review, funder reporting, and security investigation.

**Inputs.** Every event on the Event Bus (Ch.3 §3.7); direct administrative actions not otherwise captured as domain events (e.g., role changes).

**Outputs.** Immutable audit records; audit query results.

**Internal Workflow.**
```
Event received from Event Bus (any type)
      |
      v
Enrich with actor identity + timestamp
      |
      v
Append to immutable log  (never updated or deleted, per Ch.2 §2.9)
      |
      v
(If cryptographic chaining live) compute and store hash link to prior entry
```

**Dependencies.** Every other service, as a universal event subscriber.

**Security.** Write-only from every other service's perspective — no service, including administrative tooling, can delete or modify an existing audit record; read access to audit logs is itself role-gated and logged (an audit log's own access is audited).

**Database.** Owns: `audit_log` (append-only table, or a purpose-built immutable log store).

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/audit/entries/{id}` | `GET` | Full audit history for a specific entry |
| `/audit/query` | `POST` | Governance/administrative audit query (privileged) |

**Events.** None emitted; a universal terminal subscriber.

**Metrics.** Log write latency (must never become a bottleneck for the services generating events); log integrity-check pass rate (once cryptographic chaining is live).

**Scaling.** Append-only write pattern scales well on nearly any storage engine; historical query performance addressed through time-partitioned storage as log volume grows.

**Implementation Status.** `PLANNED`. Current equivalent: Git commit history and GitHub Actions run logs, which provide a partial, GitHub-dependent audit trail rather than a platform-owned, vendor-independent one.

---

### 4.17  Monitoring Service

**Purpose.** Provide real-time visibility into the health of every other service, satisfying the Observability quality attribute (Ch.2 §2.7).

**Responsibilities.** Collect health checks, latency, and error-rate telemetry from every service; alert on threshold breaches; provide the operational dashboards that inform the High Availability and Failure Scenario responses defined in Ch.3 §3.11–§3.12.

**Inputs.** Health-check and telemetry streams from every service.

**Outputs.** Operational dashboards; alerts.

**Internal Workflow.**
```
Each service exposes a /health endpoint + emits telemetry
      |
      v
Monitoring Service polls/collects continuously
      |
      v
Aggregate into service-health dashboard
      |
      v
Compare against alert thresholds
      |
      v
Trigger alert (on-call notification) on breach
```

**Dependencies.** Every other service, as a telemetry source.

**Security.** Monitoring dashboards containing operational detail (error rates, internal latencies) are restricted to `Administrator`/technical-maintainer roles; public-facing status pages expose only aggregate uptime, not internal diagnostic detail.

**Database.** Owns: `service_health_snapshots`, `alert_history`.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/monitoring/status` | `GET` | Public aggregate system status |
| `/monitoring/health/{service}` | `GET` | Detailed service health (privileged) |

**Events.** `AlertTriggered`, `AlertResolved` (extending the Ch.3 §3.7 vocabulary).

**Metrics.** (Meta) — this service's own uptime is treated with special seriousness, since a monitoring blind spot is a systemic risk to every other service's failure-detection capability.

**Scaling.** Lightweight, high-frequency polling load; typically implemented atop existing open-source observability tooling (Prometheus/Grafana-class systems) rather than built from scratch, consistent with Ch.2 §2.11's "standards before invention" principle.

**Implementation Status.** `PLANNED`. Current equivalent: GitHub Actions workflow run status as a proxy for CI/CD pipeline health; no dedicated runtime service-health monitoring exists yet, because no long-running runtime service exists yet either.

---

### 4.18  Backup Service

**Purpose.** Guarantee the durability of the canonical dataset and all supporting records against data loss, independent of any single storage technology's own redundancy.

**Responsibilities.** Schedule and execute backups across every owned data store (§4.1–§4.17's Database sections); verify backup integrity through periodic test restoration; maintain a documented, tested recovery procedure.

**Inputs.** Scheduled backup jobs; on-demand backup/restore requests (privileged).

**Outputs.** Verified backup artifacts; restoration test reports.

**Internal Workflow.**
```
Scheduled backup job triggered
      |
      v
Snapshot each owned data store  (PostgreSQL, object storage, graph store, vector DB)
      |
      v
Encrypt and store off-primary-infrastructure  (Cloud Agnostic, Ch.2 §2.3.9 —
      |                                          backup storage is itself
      |                                          vendor-independent)
      v
Periodic (not merely scheduled) test restoration into an isolated environment
      |
      v
Record restoration-test result — an untested backup is not counted as a backup
      |                            (per Ch.3 §3.11)
      v
Alert on any backup or restoration-test failure
```

**Dependencies.** Every service owning persisted state.

**Security.** Backup artifacts are encrypted at rest and in transit; restoration privileges are among the most tightly restricted in the entire platform, requiring dual authorization (two `Administrator` approvals) given the destructive potential of a mishandled restore.

**Database.** Owns: `backup_jobs`, `restoration_test_log`. No domain data of its own — it operates over every other service's data.

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/backup/status` | `GET` | Backup job history and current status |
| `/backup/restore` | `POST` | Trigger a restoration (dual-authorization, privileged) |

**Events.** `BackupCompleted`, `RestorationTestCompleted` (extending the Ch.3 §3.7 vocabulary).

**Metrics.** Backup success rate; restoration-test success rate (the more important of the two, per the principle stated in the workflow above); recovery time objective (RTO) and recovery point objective (RPO) achieved in the most recent test.

**Scaling.** Backup volume grows with dataset size but remains a periodic, background workload with no user-facing latency requirement.

**Implementation Status.** `PLANNED`. Current equivalent: GitHub's own repository redundancy for the Git-based object store, which provides real but platform-vendor-dependent durability rather than the vendor-independent, tested backup regime this service is designed to provide.

---

### 4.19  Administration Service

**Purpose.** Provide the privileged operational surface through which `Curation Lead` and `Administrator` roles manage the platform itself — users, roles, domains, schema versions, and system configuration.

**Responsibilities.** User and role management; domain/vocabulary administration (in coordination with the Ontology Service, §4.13, and its governance-review requirement); system-configuration management; the governance-transition tooling supporting the steering-group model described in the platform's governance charter.

**Inputs.** Privileged administrative requests via a dedicated admin UI/API.

**Outputs.** Applied configuration changes; administrative audit records.

**Internal Workflow.**
```
Administrative request received  (e.g., promote a curator to co-maintainer)
      |
      v
Authorization check  (requires Administrator role; certain actions require
      |                dual authorization, mirroring the Backup Service's
      |                restoration-privilege model)
      v
Apply change
      |
      v
Emit relevant domain event  (e.g., UserRoleChanged)
      |
      v
Log to Audit Service  (every administrative action, without exception)
```

**Dependencies.** Authentication Service; Audit Service; every other service, as the ultimate configuration authority for role permissions and system-wide settings.

**Security.** The single most tightly access-controlled service in the platform; every action is dual-authorized where it affects governance-sensitive state (role grants, vocabulary changes, dataset-release triggers); every action is logged without exception, and administrative log access is itself restricted and audited (mirroring the Audit Service's own self-referential access control, §4.16).

**Database.** Owns: `system_configuration`. Reads/writes across `users`, `roles` (jointly owned with Authentication Service under a documented shared-ownership exception, the one deliberate departure from the strict single-owner rule in §4.0, justified because role administration is inherently cross-cutting).

**API.**
| Endpoint | Method | Purpose |
|---|---|---|
| `/admin/users` | `GET`/`PUT` | User and role management |
| `/admin/config` | `GET`/`PUT` | System configuration |
| `/admin/domains` | `POST` | Propose a new domain/vocabulary category (routes to Ontology Service governance review) |

**Events.** `UserRoleChanged`, `SystemConfigurationChanged` (extending the Ch.3 §3.7 vocabulary).

**Metrics.** Administrative action volume and type distribution (a governance-health signal — a healthy multi-maintainer project shows administrative actions distributed across several accountable individuals, not concentrated in one).

**Scaling.** Low-volume, low-frequency by nature; no meaningful scaling concern.

**Implementation Status.** `PLANNED`. Current equivalent: direct repository-owner privileges on GitHub, held by the founding maintainer — precisely the single-point-of-administration condition the governance charter's steering-group transition, and this service's future dual-authorization model, are designed to move the project away from.

---

### 4.20  Cross-Service Consistency Matrix

A summary view, allowing a reviewer to audit the whole chapter for internal consistency at a glance rather than re-reading all nineteen sections in full.

| # | Service | Status | Owns (DB) | Emits | Primary Dependency |
|---|---|---|---|---|---|
| 4.1 | Submission | `OPERATIONAL`→`PLANNED` | submissions, submission_versions | SubmissionCreated/Validated/Rejected | Authentication |
| 4.2 | Metadata | `PLANNED` | metadata_records | MetadataGenerated | Ontology |
| 4.3 | Search | `OPERATIONAL`→`PLANNED` | search index | SearchIndexed | Metadata |
| 4.4 | Knowledge Graph | `FUTURE` | graph store | KnowledgeGraphUpdated | Ontology, Metadata |
| 4.5 | AI | `FUTURE` | vector store | EmbeddingGenerated | Search, Knowledge Graph |
| 4.6 | Authentication | `PLANNED` | users, roles, sessions | UserAuthenticated | External ORCID |
| 4.7 | Notification | `FUTURE` | notification_* | (consumer only) | Event Bus |
| 4.8 | Review | `PLANNED` | curation_queue, review_decisions | SubmissionApproved/Rejected | Submission, Knowledge Graph |
| 4.9 | DOI | `PLANNED` | dataset_releases, doi_mappings | DOIAssigned | Metadata, Zenodo |
| 4.10 | Replication | `FUTURE` | replications | ReplicationAdded | Submission, Review |
| 4.11 | Analytics | `PLANNED` | metrics_timeseries | (consumer only) | All services |
| 4.12 | Federation | `FUTURE` | federation_nodes, sync_log | DatasetUpdated (sync) | All services |
| 4.13 | Ontology | `PLANNED` | ontology_terms | OntologyVersionPublished | (foundational — none) |
| 4.14 | Export | `PLANNED` | (none owned) | ExportCompleted | Metadata |
| 4.15 | Import | `OPERATIONAL`→`PLANNED` | import_jobs | ImportJobCompleted | Submission |
| 4.16 | Audit | `PLANNED` | audit_log | (consumer only) | All services |
| 4.17 | Monitoring | `PLANNED` | service_health_snapshots | AlertTriggered/Resolved | All services |
| 4.18 | Backup | `PLANNED` | backup_jobs | BackupCompleted | All persisted stores |
| 4.19 | Administration | `PLANNED` | system_configuration | UserRoleChanged | Authentication, Audit |

**How to use this table.** Any proposed new service, or any proposed change to an existing one, should be checkable against this matrix in one pass: does it introduce a table-ownership conflict (a violation of §4.0's single-owner rule, other than the one documented exception in §4.19)? Does it emit an event already claimed by another service? Does it introduce a dependency cycle inconsistent with the layering discipline in Ch.3 §3.2? A "no" to all three is a necessary, though not sufficient, condition for the change to be architecturally sound.

---

### 4.21  Summary

Nineteen services, one template, one consistent status vocabulary. The pattern that should be visible across this entire chapter, read end to end, is deliberate: `OPERATIONAL` components are the ones already carrying real curatorial and scientific weight today — Submission validation, Search indexing, and registry Import — while `PLANNED` and `FUTURE` components extend that same core discipline (schema validation first, human accountability always, event-driven decoupling throughout) rather than introducing a different set of rules once the system grows. A service reaching `OPERATIONAL` status in the future should be recognizable, in its behavior, as the same architecture described here — not a different system that happens to share a name.
