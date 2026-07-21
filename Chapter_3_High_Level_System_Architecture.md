# Dark Data Medicine — Platform Architecture Series

## Chapter 3: High-Level System Architecture

*Document status: Normative. This chapter is governed by Chapter 2 (Architectural Vision) and, in turn, governs the Domain Model, Database Schema, Ontology, API Specification, Backend Architecture, Frontend Architecture, and AI Services Architecture chapters.*

*Version 0.1 — Draft for governance review*

---

### 3.0  How to Read This Chapter

This chapter describes the **target-state** system architecture — the shape the platform is designed to grow into, consistent with the twenty-year federation vision stated in Chapter 2, §2.2. It does not describe the system as a single, already-deployed monolith. Consistent with the honesty standard this project holds itself to throughout its documentation, every major component in this chapter carries an explicit **Implementation Status** tag:

| Tag | Meaning |
|---|---|
| **`OPERATIONAL`** | Running in production today, in the form described (possibly simplified relative to the target-state description). |
| **`PLANNED`** | Not yet built; scoped and prioritized in the near-term technical roadmap. |
| **`FUTURE`** | A target-state capability consistent with Chapter 2's principles, not yet scoped for near-term implementation. |

Today's production system is deliberately simple: a static-first search interface, a Git-versioned JSON file store validated by a Python schema validator, and three GitHub Actions pipelines for validation, testing, and deployment. This simplicity is not a limitation the architecture apologizes for — it is a direct, correct application of the Technology Independence and Cloud Agnostic principles (Chapter 2, §2.8–§2.9) at the platform's current scale. The architecture described below is the **superset** this simple system is designed to grow into without a rewrite, one `OPERATIONAL`-tagged component at a time, as population and usage scale justify each additional layer. A reader should come away from this chapter understanding both where the system is today and the complete shape it is engineered to become.

---

### 3.1  System Overview

The question this section answers: *at the highest level, what are the moving parts, and how does a request flow through them?*

```
                          +----------------------------------+
                          |            Researchers            |
                          |   (contributors, curators,        |
                          |    systematic reviewers, AI        |
                          |    agents, partner institutions)  |
                          +-----------------+------------------+
                                            |
                                            v
                          +----------------------------------+
                          |       Web / Mobile Portal          |   [OPERATIONAL: static
                          |   (search UI, submission forms)    |    search site only;
                          +-----------------+------------------+    submission portal
                                            |                       is PLANNED]
                                HTTPS / REST / GraphQL
                                            |
                          +-----------------v------------------+
                          |            API Gateway              |   [PLANNED]
                          |  auth, rate limiting, routing        |
                          +-----------------+------------------+
                                            |
        +--------+--------+--------+-------+-------+---------+----------+----------+
        |        |        |        |       |       |         |          |          |
        v        v        v        v       v       v         v          v          v
   Submission Metadata  Search  Knowledge   AI    Auth   Notification Analytics Federation
    Service    Service  Service   Graph   Service Service   Service    Service    Service
   [OPERATIONAL [PLANNED] [PLANNED [PLANNED [FUTURE][PLANNED] [FUTURE]  [PLANNED]  [FUTURE]
    as CLI/CI                       ]                                  ]
    scripts]
        |        |        |        |       |       |         |          |          |
        +--------+--------+--------+-------+-------+---------+----------+----------+
                                            |
                                            v
                          +----------------------------------+
                          |             Event Bus              |   [PLANNED]
                          +-----------------+------------------+
                                            |
                          +-----------------v------------------+
                          |          Storage Layer              |
                          |  ---------------------------------  |
                          |  Object Storage (JSON entries)       [OPERATIONAL — Git repo]
                          |  Relational Store (PostgreSQL)        [PLANNED]
                          |  Knowledge Graph (Neo4j)               [FUTURE]
                          |  Search Index (OpenSearch)              [PLANNED]
                          |  Vector Database (embeddings)            [FUTURE]
                          +-----------------+------------------+
                                            |
                                            v
                          +----------------------------------+
                          |          External Systems          |
                          |  ORCID · Zenodo · DataCite ·        |   [ORCID field: OPERATIONAL
                          |  Crossref · PubMed · OpenAlex ·      |    (schema field only)
                          |  ClinicalTrials.gov · GitHub          |   Zenodo/DOI: PLANNED
                          +----------------------------------+   All others: FUTURE]
```

**Reading this diagram.** A request today — a researcher searching the registry — traverses only the leftmost path: Web Portal → static search index (pre-built by `generate_search_index.py`) → JSON entries in the Git-versioned object store. Every other box exists to describe where that single path is designed to grow, not to claim it exists yet. This distinction is the single most important thing a new architect joining this project should take from this section.

---

### 3.2  Architectural Layers

The system is organized into six layers. Each layer may only depend on the layer directly beneath it — a dependency from the Domain Layer directly into the Storage Layer, skipping the Infrastructure Layer's abstraction, is an architectural violation regardless of how convenient it may seem locally.

| Layer | Responsibility | Contains | Must NOT Do |
|---|---|---|---|
| **Presentation** | Render content to humans (and, per Ch. 2 §2.3.4, to AI agents) | Web portal, mobile clients, CLI output formatting | Contain business rules; validate data beyond input-format hints; talk directly to the Storage Layer |
| **API** | Expose every platform capability as a documented, versioned contract | REST/GraphQL endpoints, OpenAPI specification, authentication middleware | Contain domain logic itself — the API layer translates and routes, it does not decide |
| **Application** | Orchestrate use cases across services (e.g., "publish a submission" spans Submission, Metadata, Search, and DOI services) | Use-case orchestration, workflow/event coordination | Contain low-level storage or infrastructure detail; make domain-modeling decisions that belong to the Domain Layer |
| **Domain** | Encode the platform's actual scientific and governance rules | Schema validation logic, curation-state machine, entity relationships (Domain Model chapter) | Depend on any specific database, cloud provider, or framework (Ch. 2 §2.8) |
| **Infrastructure** | Provide technical capabilities the Domain Layer needs without exposing vendor specifics | Event bus abstraction, storage-driver interfaces, external-system adapters | Leak vendor-specific types or APIs upward into the Domain Layer |
| **Storage** | Durably persist data | PostgreSQL, object storage, Neo4j, OpenSearch, vector database | Contain business logic of any kind — a stored procedure encoding a curation rule is a layering violation |

This layering is what makes Chapter 2's Technology Independence principle (§2.8) enforceable rather than aspirational: because the Domain Layer never imports a database driver directly, replacing PostgreSQL with a different relational store, or replacing Neo4j with an alternative graph engine, is confined to the Infrastructure and Storage layers and never requires touching validation or curation logic.

---

### 3.3  User Interaction Flow

The canonical path a single negative-result finding takes through the system, from a researcher's first action to full discoverability:

```
Researcher
   |
   v
Authenticate  (ORCID OIDC login, or anonymous for the no-Git path — Ch.2 §2.3.6)
   |
   v
Create Submission  (structured form, or raw JSON via API/CLI)
   |
   v
Automated Schema Validation  (Draft-07 JSON Schema — OPERATIONAL today, via CI)
   |
   v
Human Curator Review  (duplicate check, provenance check, PII screen — OPERATIONAL)
   |
   v
Approval  (merge to canonical dataset)
   |
   v
Metadata Generation  (FAIR-compliant metadata record — PLANNED)
   |
   v
Publication  (entry visible in the live dataset)
   |
   v
DOI Assignment  (at dataset-release granularity — PLANNED, Ch.6 of the funding case)
   |
   v
Search Indexing  (OPERATIONAL today via generate_search_index.py; OpenSearch — PLANNED)
   |
   v
Knowledge Graph Integration  (entity linking to disease/intervention/institution nodes — FUTURE)
   |
   v
AI Index  (embedding generation for semantic search — FUTURE)
```

Every arrow in this flow corresponds to an event in the Event Architecture (§3.7); no transition happens silently. This is a direct application of the Auditability quality attribute defined in Chapter 2, §2.7.

---

### 3.4  Core Services

Each service is described using a uniform template — **Responsibility**, **Input**, **Output**, **Events Emitted**, **Dependencies**, **Implementation Status** — so that a new engineer can evaluate any two services by the same criteria.

#### 3.4.1  Submission Service — `OPERATIONAL` *(as validation scripts + CI pipeline; not yet a standalone networked service)*

- **Responsibility.** Receive a candidate negative-result entry and determine whether it is structurally admissible.
- **Input.** Experiment JSON conforming, or attempting to conform, to the submission schema.
- **Output.** A submission identifier and a structural validation verdict.
- **Events emitted.** `SubmissionCreated`, `SubmissionValidated` (or `SubmissionRejected`).
- **Dependencies.** Metadata Service (for enrichment), Storage Layer, Authentication Service.
- **Current implementation.** `validate_submission.py`, invoked both locally by contributors and automatically by the `validate-submissions.yml` CI workflow on every pull request.
- **Planned evolution.** Extraction into a standalone API-first service (Ch. 2 §2.3.3) accepting submissions over HTTPS directly, removing the current requirement to open a pull request for programmatic submission.

#### 3.4.2  Metadata Service — `PLANNED`

- **Responsibility.** Generate and validate FAIR-compliant metadata for every entity; produce standards-conformant exports.
- **Input.** A validated submission or dataset object.
- **Output.** A structured metadata record (Dublin Core / DataCite-compatible where applicable) and export artifacts (CSV, JSON-LD).
- **Events emitted.** `MetadataGenerated`.
- **Dependencies.** Submission Service, controlled vocabularies (Domain Model chapter).
- **Current partial equivalent.** `export_to_excel.py` provides a narrow, manual version of the export capability this service will formalize and automate.

#### 3.4.3  Search Service — `PLANNED` *(a static-index equivalent is `OPERATIONAL`)*

- **Responsibility.** Index published entries and serve faceted, full-text, and — once the AI Service (§3.4.5) is live — semantic search.
- **Input.** Published entries from the Storage Layer.
- **Output.** Ranked search results; faceted filter counts.
- **Events emitted.** `SearchIndexed`.
- **Dependencies.** Storage Layer, AI Service (for semantic ranking, `FUTURE`).
- **Current implementation.** `generate_search_index.py` builds a static JSON index consumed directly by the client-side search interface — a deliberately zero-infrastructure implementation of faceted keyword search, consistent with the Cloud Agnostic principle (Ch. 2 §2.3.9), sufficient at current dataset scale.
- **Planned evolution.** Migration to OpenSearch once entry volume or query complexity (faceted combinations, relevance ranking) exceeds what a static index can serve responsively — the specific scale threshold is defined in §3.10.

#### 3.4.4  Knowledge Graph Service — `FUTURE`

- **Responsibility.** Maintain the graph connecting `Experiment → Disease → Drug/Intervention → Institution → Funding → Publication → Replication` described in the outline, enabling queries no relational or document store expresses naturally (e.g., "show every negative result for any intervention in the same drug class as X, across every institution type").
- **Input.** Published entries with resolved entity references.
- **Output.** Graph query results; entity-relationship exports.
- **Events emitted.** `KnowledgeGraphUpdated`.
- **Dependencies.** Metadata Service, Ontology chapter's controlled entity model.
- **Current implementation.** None; the current flat JSON schema captures entity relationships as string fields (e.g., `target_disease`) rather than resolved graph edges, which is sufficient for the current curation and search use cases but insufficient for the cross-entity reasoning this service is designed to provide.

#### 3.4.5  AI Service — `FUTURE`

- **Responsibility.** Generate embeddings for semantic search, support retrieval-augmented generation (RAG) over the corpus, produce entry summaries, perform classification and entity linking, and map free-text submissions onto the controlled Ontology.
- **Input.** Published entry text and metadata.
- **Output.** Vector embeddings, summaries, classification labels, linked entity references.
- **Events emitted.** `EmbeddingGenerated`.
- **Dependencies.** Search Service, Knowledge Graph Service, Vector Database.
- **Design constraint.** Per Chapter 2 §2.3.7 (Zero Trust) and §2.9 (Human Accountability), AI-generated classification or entity-linking suggestions are never auto-merged into the canonical dataset without the same human curator review applied to every other submission path — AI assists curation; it does not replace the accountable curator.

#### 3.4.6  DOI Service — `PLANNED`

- **Responsibility.** Mint, version, and synchronize persistent identifiers for dataset releases.
- **Input.** A finalized, versioned dataset snapshot.
- **Output.** A DataCite/Crossref-compatible DOI, registered and resolvable.
- **Events emitted.** `DOIAssigned`.
- **Dependencies.** Metadata Service, external Zenodo/DataCite integration (§3.6).
- **Current status.** Not yet implemented; scoped for the first versioned release described in the platform's funding case (Chapter on Budget and Sustainability, §3.6/6.6 of that document).

#### 3.4.7  Authentication Service — `PLANNED`

- **Responsibility.** Authenticate contributors and curators; authorize actions by role.
- **Mechanisms.** OIDC, OAuth2, ORCID-based identity for researchers specifically (matching the schema's existing `researcher_orcid` field), multi-factor authentication for curator and administrative roles, and role-based access control (RBAC) distinguishing Contributor, Curator, Curation Lead, and Administrator roles.
- **Current equivalent.** GitHub's own authentication and repository-permission model, for the current PR-based contribution path — a reasonable interim substitute, but one that ties identity to a GitHub account rather than to a researcher's ORCID, which the dedicated Authentication Service is designed to correct.

#### 3.4.8  Notification Service — `FUTURE`

- **Responsibility.** Inform contributors and curators of submission status changes, review comments, and dataset release events.
- **Current equivalent.** GitHub's native pull-request notification system, for technical contributors only — non-technical contributors using the no-Git path currently rely on direct curator email follow-up rather than an automated notification system.

#### 3.4.9  Analytics Service — `PLANNED`

- **Responsibility.** Produce dashboards, KPIs, usage statistics, and impact metrics — the same underlying capability that already powers the funder-reporting KPIs described in the project's funding case.
- **Current implementation.** `analyze_trends.py`, run on demand rather than continuously, producing flattened CSV trend reports.

#### 3.4.10  Federation Service — `FUTURE`

- **Responsibility.** Synchronize entries and metadata across mirror nodes operated by partner institutions or national registries, resolving conflicts by provenance (Ch. 2 §2.3.8).
- **Design constraint.** Every synchronized entry retains an unambiguous originating-node attribution, consistent with the Human Accountability and Conflict-of-Interest Disclosure principles in Ch. 2 §2.9 — federation must never obscure which node, curator, or institution is accountable for a given entry's content.

---

### 3.5  Component Interaction

The canonical publish-path interaction sequence, corresponding to the flow in §3.3:

```
Submission Service
      |  emits SubmissionValidated
      v
Metadata Service
      |  emits MetadataGenerated
      v
Knowledge Graph Service
      |  emits KnowledgeGraphUpdated
      v
Search Service
      |  emits SearchIndexed
      v
AI Service
      |  emits EmbeddingGenerated
      v
API Layer
      |  serves updated state
      v
Frontend
```

This chain is deliberately expressed as an **event-driven pipeline** rather than a synchronous call chain: the Submission Service does not block waiting for the Knowledge Graph Service to finish before returning a response to the contributor. This decouples the latency of any one downstream service from the contributor-facing submission experience, and — more importantly for a `FUTURE`-tagged service like the Knowledge Graph — allows that service to be introduced later without changing the Submission Service's contract at all. It only needs to subscribe to an event that already exists.

---

### 3.6  External Systems

| System | Integration Purpose | Status |
|---|---|---|
| **ORCID** | Researcher identity verification; already a validated schema field | `OPERATIONAL` (schema field) / `PLANNED` (OIDC login) |
| **Zenodo** | Archival hosting and DOI minting for versioned dataset releases (Ch. 2 §2.3.1, §2.9) | `PLANNED` |
| **DataCite / Crossref** | DOI registration infrastructure underlying Zenodo and direct dataset citation | `PLANNED` |
| **PubMed** | Cross-referencing published literature related to a registered negative result, and identifying candidate negative findings buried in supplementary materials | `FUTURE` |
| **OpenAlex** | Open bibliographic graph, used for citation-network context and institution disambiguation | `FUTURE` |
| **ClinicalTrials.gov** | Primary source for the registry-mining draft-extraction pipeline (`clinicaltrials_seed_extractor.py`) | `OPERATIONAL` |
| **GitHub** | Current hosting for the codebase, CI/CD, and the technical contribution path itself | `OPERATIONAL` |
| **Dataverse / Dryad** | Potential interoperability targets for cross-posting structured entries to general-purpose research-data repositories | `FUTURE` |

Every integration in this table is designed as a client of the platform's own API (Ch. 2 §2.3.3) or as a well-documented adapter in the Infrastructure Layer (§3.2) — no external system is permitted special, undocumented access to the Storage Layer.

---

### 3.7  Event Architecture

The platform's internal state changes are modeled as an explicit, versioned event vocabulary. This vocabulary is authoritative — a capability that changes system state without emitting a corresponding event is, by definition, not yet fully integrated into the architecture described in this chapter.

| Event | Emitted By | Consumed By |
|---|---|---|
| `SubmissionCreated` | Submission Service | Metadata Service, Notification Service |
| `SubmissionValidated` | Submission Service | Application Layer orchestrator |
| `SubmissionApproved` | Application Layer (curator action) | Metadata Service |
| `SubmissionRejected` | Application Layer (curator action) | Notification Service |
| `MetadataGenerated` | Metadata Service | Knowledge Graph Service, Search Service |
| `DOIAssigned` | DOI Service | Metadata Service, Notification Service |
| `KnowledgeGraphUpdated` | Knowledge Graph Service | AI Service, Analytics Service |
| `SearchIndexed` | Search Service | API Layer (cache invalidation) |
| `EmbeddingGenerated` | AI Service | Search Service (semantic ranking) |
| `ReplicationAdded` | Application Layer | Knowledge Graph Service, Analytics Service |
| `CommentAdded` | Application Layer | Notification Service |
| `ReviewCompleted` | Application Layer (curator action) | Submission Service, Analytics Service |
| `DatasetUpdated` | Application Layer (release process) | Federation Service, DOI Service |

**Current implementation note.** Today's system implements the substance of `SubmissionCreated`, `SubmissionValidated`, `SubmissionApproved`, and `SubmissionRejected` implicitly, through the GitHub pull-request lifecycle (PR opened, CI check result, PR merged, PR closed) rather than through an explicit, standalone event bus. Formalizing these as first-class platform events — independent of GitHub's specific PR model — is a `PLANNED` step that decouples the event vocabulary from any single Git-hosting vendor, consistent with Chapter 2's Cloud Agnostic and Technology Independence principles (§2.8–§2.9).

---

### 3.8  Storage Architecture

The system deliberately does not use a single storage technology for every kind of data — a direct consequence of the "storage without metadata has little value" framing in Chapter 2 §2.3.2, and of the recognition that structured records, documents, graph relationships, embeddings, and logs each have a natural storage shape that a one-size-fits-all database distorts.

| Data Category | Storage Technology | Status | Rationale |
|---|---|---|---|
| Structured entry metadata, curation-workflow state, user/role records | **PostgreSQL** | `PLANNED` | Mature, open-source, standards-compliant relational engine; strong transactional guarantees for curation-state transitions where consistency (an entry cannot be simultaneously "approved" and "rejected") matters more than horizontal write scale. |
| Raw entry content (JSON) | **Object Storage** | `OPERATIONAL` *(as a Git repository)* | Git provides exactly the append-only, fully versioned, diff-able history this data category needs (Ch. 2 §2.6, principle 3) at zero additional infrastructure cost; migration to a dedicated object store (e.g., S3-compatible storage) is `PLANNED` once write volume exceeds what a Git-based workflow comfortably serves. |
| Knowledge graph (entity relationships) | **Neo4j** (or an equivalent open-source graph engine) | `FUTURE` | Graph-native traversal queries (multi-hop "same drug class" or "same institution type" queries) are the natural query shape for this data; forcing them into relational joins at scale degrades both query clarity and performance. |
| Vector embeddings | **Vector Database** | `FUTURE` | Purpose-built approximate-nearest-neighbor indexing is required for semantic search (§3.4.5) at any meaningful scale; a relational database's native indexing is not designed for this access pattern. |
| Logs and operational telemetry | **OpenSearch** | `PLANNED` | Purpose-built for high-volume, append-heavy, full-text-searchable log data; also reused as the eventual engine behind the Search Service (§3.4.3) itself. |

**Explicit non-goal.** This architecture does not treat "fewer storage technologies" as inherently virtuous. A polyglot-persistence model, correctly bounded by the layering discipline in §3.2 (no business logic in any storage layer, no direct cross-store queries bypassing the Application Layer), is judged here to serve the FAIR and Metadata First principles better than forcing every data shape into a single database chosen for its familiarity rather than its fit.

---

### 3.9  Communication Architecture

| Mechanism | Use Case | Status |
|---|---|---|
| **REST** | Primary synchronous API surface; CRUD-shaped operations (submit, retrieve, update status) | `PLANNED` |
| **GraphQL** | Complex, client-shaped queries spanning multiple entities (e.g., "all negative oncology results with a specified intervention type, including linked knowledge-graph neighbors") | `PLANNED` |
| **Asynchronous Events** | Internal service-to-service communication (§3.7) | `PLANNED` |
| **Webhooks** | Outbound notification to partner-institution systems on dataset release or entry publication relevant to a partnership agreement | `FUTURE` |
| **Message Queue** | Durable delivery guarantee for the Event Bus, ensuring a service outage does not silently drop events (§3.12) | `PLANNED` |
| **Streaming** | Real-time dashboard updates for Analytics Service consumers (e.g., a live funder-facing KPI dashboard) | `FUTURE` |

---

### 3.10  Scalability Strategy

The platform's scaling path is deliberately staged, so that infrastructure complexity is added only when the current stage's limits are actually reached, not preemptively:

```
Stage 1: Single Static Deployment        [OPERATIONAL — current stage]
   Static site + Git-versioned JSON store + GitHub Actions CI
   Sufficient through:  low thousands of entries, keyword-only search

Stage 2: Containerized Services           [PLANNED]
   Docker-packaged Submission/Metadata/Search services behind an API Gateway;
   PostgreSQL and OpenSearch introduced
   Sufficient through:  tens of thousands of entries, faceted search, RBAC

Stage 3: Orchestrated Cluster              [PLANNED, longer horizon]
   Kubernetes-orchestrated service deployment; Knowledge Graph and Vector DB
   introduced; horizontal autoscaling of Search and AI services
   Sufficient through:  hundreds of thousands of entries, semantic search,
   AI-assisted curation support

Stage 4: Federation                         [FUTURE]
   Multiple independently-operated nodes (institutional mirrors, national
   registries) synchronized via the Federation Service (§3.4.10)
   Sufficient through:  the twenty-year, globally-distributed vision
   stated in Chapter 2, §2.2

Stage 5: Global Node Network                 [FUTURE]
   Full realization of Chapter 2 §2.10 — semantic reasoning and knowledge-graph
   queries executed across the federated network as a single logical dataset
```

Each stage transition is triggered by a measured threshold (entry count, query latency, curator queue depth) rather than a calendar date, and — because of the layering discipline in §3.2 — each transition is additive: Stage 2 does not require rewriting Stage 1's validation logic, only relocating it behind an API Gateway and adding services around it.

---

### 3.11  High Availability

`PLANNED`, targeted from Stage 2 onward (§3.10):

- **Load balancing** across redundant instances of stateless services (API Gateway, Submission, Search).
- **Database replication** for PostgreSQL (primary/replica), ensuring read availability survives a primary-node failure and providing the durability guarantee the Immutable Releases principle (Ch. 2 §2.9) depends on.
- **Backup** of the canonical object store (both the current Git-based store and its `PLANNED` object-storage successor) on a documented, tested restoration schedule — an untested backup is not, for this project's risk purposes, considered a backup.
- **Monitoring** of every `OPERATIONAL` and `PLANNED` service against the Observability quality attribute (Ch. 2 §2.7).
- **Automatic recovery** for stateless services via container orchestration health checks (Stage 3, §3.10); the current Stage 1 static deployment's high availability is a direct, low-cost benefit of its static-hosting model, which has no live application server to fail.

---

### 3.12  Failure Scenarios

Each row states the failure, the user-visible consequence at the platform's **current** implementation stage, and the mitigation the target architecture in this chapter provides once the relevant `PLANNED`/`FUTURE` components are live.

| Failure | Consequence Today (Stage 1) | Target-State Mitigation |
|---|---|---|
| Database (PostgreSQL, once introduced) unavailable | N/A — no live database in Stage 1 | Read traffic served from replica; writes queued and retried; curation UI degrades to read-only rather than failing entirely |
| API Gateway unavailable | N/A — no gateway in Stage 1 | Load-balanced redundant instances; static search interface remains available independent of API health (a direct benefit of keeping the search surface static-first even after the API layer is introduced) |
| Search Service unavailable | Static index continues to serve search unaffected (a single JSON file, cached at the CDN edge) | Same static-fallback principle preserved by design even after OpenSearch migration — the static index generation step (§3.4.3) is retained as a resilience fallback, not discarded |
| Knowledge Graph unavailable | N/A — not yet built | Search and Submission services continue operating on flat metadata; only cross-entity graph queries degrade, not core publication or discovery |
| ORCID unavailable | Optional field; submission proceeds without it | Submission and curation proceed without identity verification; entry flagged for later ORCID backfill once ORCID recovers |
| Zenodo unavailable | N/A — no DOI pipeline yet | Dataset release queued; DOI minting retried; already-published entries remain fully accessible via the platform's own persistent identifiers regardless of Zenodo's availability |
| Internet connectivity lost (client-side) | Static site, once loaded, continues to serve already-cached search results from local browser cache | Same behavior preserved; a service-worker-based offline mode is a documented `FUTURE` enhancement building on the static-first design |

The recurring pattern across this table — several failure modes degrading gracefully specifically *because* the current Stage 1 architecture is simple and static — is presented here as a genuine architectural strength worth preserving deliberately as complexity is added in later stages, not merely as an artifact of the current system being small.

---

### 3.13  Architecture Decisions

Full formal records are maintained as individual ADRs per Chapter 2 §2.11; this section summarizes the reasoning behind the headline technology choices referenced throughout this chapter.

**Why PostgreSQL?** Mature, open-source (satisfying Ch. 2 §2.5's licensing constraint), strong transactional consistency for curation-workflow state, and broad operational familiarity across the university and institutional partners this project's funding case targets — minimizing the operational burden on any future institutional mirror operator (§3.4.10).

**Why Neo4j (or an equivalent open-source graph engine)?** The knowledge-graph access pattern described in §3.4.4 — multi-hop traversal across intervention, disease, institution, and outcome relationships — is a poor fit for relational joins at scale; a native graph engine expresses and executes these queries far more directly. The specific engine choice remains subordinate to Chapter 2's Technology Independence principle (§2.8): any open-source graph database satisfying the same query and export contract is an acceptable substitute.

**Why GraphQL alongside REST, rather than one or the other?** REST's resource-oriented model fits the platform's CRUD-shaped operations (submit an entry, fetch an entry) well and is the lower-friction choice for the widest range of API consumers, including the CLI and SDK clients described in Ch. 2 §2.3.3. GraphQL is added specifically for the cross-entity query shapes systematic-review and AI tooling consumers are expected to need (§3.4.5), where requiring several sequential REST calls to assemble one logical query would be both inefficient and awkward for those consumers to express.

**Why JSON Schema (rather than, e.g., XML Schema or a proprietary validation DSL)?** JSON Schema is an open, widely adopted standard (Ch. 2 §2.11, principle 1: standards before invention) with mature tooling across every major programming language, keeping the Submission Service's validation contract technology-independent (§2.8) and directly satisfying the Metadata First and FAIR First principles (§2.3.1–§2.3.2) without inventing a project-specific format.

**Why OpenAPI for the API specification?** The de facto open standard for REST API documentation, enabling automatic client-SDK generation across languages — a direct, low-cost way to satisfy the API First principle's requirement that every capability be consumable by an external client, not only the first-party frontend (Ch. 2 §2.3.3).

**Why Docker (and, at Stage 3, Kubernetes)?** Containerization is the most broadly portable way to satisfy Cloud Agnostic deployment (Ch. 2 §2.3.9) — the same container image runs unmodified on AWS, Azure, Google Cloud, a self-hosted server, or a university cluster, directly serving the federation vision in §3.4.10 and Chapter 2 §2.10.

---

### 3.14  Future Evolution

Consistent with Chapter 2 §2.10, this chapter's architecture is designed to accommodate, without requiring a rewrite:

- **Fully distributed operation** across the staged path in §3.10, culminating in the Stage 5 global node network.
- **AI-native operation**, where the AI Service (§3.4.5) moves from an assistive layer to a deeply integrated discovery and curation-support capability, always bounded by the Zero Trust and Human Accountability constraints stated in Chapter 2 §2.9.
- **Full federation**, realized through the Federation Service (§3.4.10) and the conflict-resolution and provenance model it depends on.
- **Institution-hosted mirror nodes**, operated by university or national research-infrastructure partners using the same containerized deployment artifacts as the platform's own primary node, per the Cloud Agnostic principle.

---

### 3.15  Architecture Quality Scenarios (ISO/IEC 25010 · ATAM-style)

Each scenario follows the standard ATAM structure: **Stimulus** (what happens) → **Environment** (under what conditions) → **Response** (how the architecture reacts) → **Response Measure** (how success is verified).

**Availability.** *Stimulus:* a primary database node fails. *Environment:* normal production load, Stage 2+ deployment. *Response:* traffic fails over to a replica within the standard PostgreSQL replication failover window; the static search fallback (§3.12) remains available throughout regardless of database state. *Response Measure:* read availability maintained with no user-visible downtime; write availability restored within the documented failover target once defined in the Backend Architecture chapter.

**Scalability.** *Stimulus:* entry volume grows from 100,000 to 10,000,000 across the federated network. *Environment:* Stage 4/5 federated deployment. *Response:* indexing and search remain distributed across federated nodes (§3.4.10) rather than requiring a single node to index the full global dataset; query routing directs a search to the relevant subset of nodes based on domain and institution-type facets. *Response Measure:* query latency at 10,000,000 entries remains within the same order of magnitude as at 100,000 entries, verified by load testing at each Stage transition.

**Security.** *Stimulus:* a user attempts to upload a malicious file disguised as a data submission. *Environment:* any stage with live file upload (Stage 2+). *Response:* schema validation (§3.4.1) rejects any object not conforming to the expected JSON structure before it reaches storage; file-type and content-sandbox validation is applied to any binary attachment path introduced in a future schema version; Zero Trust (Ch. 2 §2.3.7) treats the upload as untrusted regardless of the uploader's authenticated identity. *Response Measure:* no malformed or non-conformant object ever reaches the canonical Storage Layer, verified by the automated test suite's negative-path coverage.

**Maintainability.** *Stimulus:* a new contributor needs to modify the Search Service's ranking logic. *Environment:* any stage. *Response:* the layering discipline in §3.2 confines the change to the Application and Domain layers for that service; the contributor does not need to understand the Knowledge Graph or AI Service internals to make the change safely. *Response Measure:* the change can be made and tested without modifying any other service's code, verified by the absence of cross-service edits in the corresponding change record.

**Interoperability.** *Stimulus:* a partner institution's own data pipeline needs to pull newly published entries automatically. *Environment:* Stage 2+, API Gateway live. *Response:* the partner consumes the same versioned REST/GraphQL API (§3.9) any other client uses — no bespoke integration is built for any single partner, per Ch. 2 §2.3.3. *Response Measure:* a new partner integration requires zero platform-side code changes, only client-side API consumption.

**Reliability.** *Stimulus:* the Knowledge Graph Service (§3.4.4) experiences a processing backlog. *Environment:* Stage 3+. *Response:* because publication (§3.3) does not block on Knowledge Graph indexing — the event-driven pipeline in §3.5 decouples them — entries remain published and searchable via the Search Service even while graph indexing lags behind. *Response Measure:* Knowledge Graph backlog never causes a Submission or Search Service outage, verified by chaos-testing the Knowledge Graph Service's artificial unavailability against the rest of the pipeline.

**Portability.** *Stimulus:* a national research-infrastructure operator wants to deploy a fully self-hosted mirror with no dependency on any commercial cloud provider. *Environment:* Stage 4 federation. *Response:* the same Docker/Kubernetes deployment artifacts (§3.13) run unmodified on the operator's own infrastructure, per Cloud Agnostic (Ch. 2 §2.3.9). *Response Measure:* a documented self-hosted deployment guide is sufficient, without platform-team involvement, for a technically competent institutional operator to stand up a conformant mirror node.

---

### 3.16  Summary

A new architect who has read only this chapter should now be able to answer every question posed in the governance recommendation that motivated it: what components the platform has (§3.1, §3.4), how they communicate (§3.5, §3.9), where data is stored (§3.8), how external systems are integrated (§3.6), how the system scales (§3.10), how it withstands failure (§3.11–3.12), and how it can evolve without being rewritten (§3.14). Equally importantly, they should understand precisely which of these components exist today and which describe the target this project's roadmap — detailed separately in the platform's funding and implementation case — is built to reach.
