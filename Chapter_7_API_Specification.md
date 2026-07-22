# Dark Data Medicine — Platform Architecture Series

## Chapter 7: API Specification (OpenAPI + GraphQL)

*Document status: Normative. Governed by Chapter 2 (API First, §2.3.3), Chapter 3 (§3.9, Communication Architecture), Chapter 4 (per-service endpoint stubs, §4.1–§4.19), Chapter 5 (Domain Model, entity shapes), and Chapter 6 (Ontology, §6.4's `/ontology/*` surface). This chapter is the authoritative contract every client — the web portal, the CLI, partner integrations, and AI agents — is built against.*

*Version 0.1 — Draft for governance review*

---

### 7.0  Purpose and Scope

Chapter 4 gave each of the nineteen services a short table of endpoints, scoped locally to that service's own responsibilities. This chapter consolidates those fragments into one coherent, versioned API contract, and adds everything a fragment-by-fragment view cannot show: a single authentication model that works the same way against every endpoint, one error format every client can rely on regardless of which service actually produced the error, one pagination and filtering convention, and a formal GraphQL schema alongside the REST surface — because Chapter 3 §3.9 committed to both, and a commitment to "both" is only real once both are specified to the same level of rigor.

Per the API First principle (Ch.2 §2.3.3), this chapter is written as the **contract the web portal itself must consume** — there is no privileged, undocumented path the first-party frontend uses that a third-party integrator cannot.

---

### 7.1  API Design Principles

1. **Resource-oriented REST, query-oriented GraphQL — not a duplicate surface.** REST resources map directly onto the Domain Model entities of Chapter 5 (an `Experiment`, a `Submission`, a `Review`); GraphQL is not a second copy of the same CRUD operations but the client-shaped, multi-entity query surface for the traversal-heavy use cases (Knowledge Graph neighbors, cross-entity systematic-review queries) identified in Ch.3 §3.13.
2. **Idempotency by default on all mutating operations.** Every `POST` that creates a resource accepts an optional client-supplied `Idempotency-Key` header; replaying the same request with the same key returns the original result rather than creating a duplicate — critical for the Submission Service (Ch.4 §4.1), where a contributor's retried request after a network timeout must never silently create two submissions for one finding.
3. **Versioned by URL path segment, not by header negotiation.** `/v1/submissions`, not content-type negotiation — chosen for debuggability and cache-friendliness over the marginal elegance of header-based versioning, consistent with Ch.2 §2.11's preference for the option a wider range of client tooling handles correctly by default.
4. **No breaking change within a major version.** Per the Compatibility Policy (§7.2), new optional fields may be added to a response within `v1`; removing or renaming a field, or changing a field's type, requires `v2`.
5. **Every response is a documented, typed contract — never "whatever the database currently returns."** The OpenAPI specification (§7.5) is generated from, and validated against, the Domain Model (Chapter 5) and the Ontology (Chapter 6), not maintained as a hand-written document that can silently drift from what the services actually return.
6. **Public read access requires no authentication; every write requires it.** Directly implementing Open Science First (Ch.2 §2.3.5) for reads and Zero Trust (Ch.2 §2.3.7) for writes.

---

### 7.2  Versioning and Compatibility Policy

| Policy | Rule |
|---|---|
| Version identifier | URL path prefix: `/v1/...` |
| Minimum support window | A major version remains supported for at least 24 months after the next major version's release, giving institutional partners (whose own integration cycles are slower than a typical SaaS consumer's) adequate migration time |
| Deprecation signaling | A `Sunset` HTTP header (RFC 8594) is added to every response of a version once its deprecation date is announced, at least 12 months before removal |
| Non-breaking additive changes | New optional request fields, new response fields, new endpoints, new enum values in a field already documented as extensible — permitted within a major version without notice beyond the standard changelog |
| Breaking changes | Field removal, field type change, endpoint removal, required-field addition to an existing request — always require a new major version |
| Ontology/vocabulary evolution | Handled by Chapter 6 §6.5's term-lifecycle process, not by API versioning — a deprecated `domain` term remains a valid, queryable value under the same API version indefinitely, per Ch.2 §2.6 principle 15 |

---

### 7.3  Authentication and Authorization

Delegated to, and consistent with, the Authentication Service specification (Ch.4 §4.6):

- **Public GET requests** (search, entry retrieval, ontology lookup, export) require no `Authorization` header.
- **Authenticated requests** carry `Authorization: Bearer <JWT>`, obtained via the ORCID OIDC flow (`/v1/auth/login` → `/v1/auth/callback` → token issuance).
- **Scopes**, embedded in the JWT and checked per-endpoint: `submit:write`, `review:write` (Curator/Curation Lead only), `admin:write` (Administrator only), `federation:sync` (Federation Node service-to-service only).
- **Service-to-service calls** (e.g., the Import Service calling the Submission Service, Ch.4 §4.15) use a distinct system-account JWT, never a human's token, so that every audit record correctly attributes machine-originated actions to a system account rather than impersonating a human curator — directly implementing Ch.4 §4.15's security posture.
- **Rate limits** are scope- and role-dependent (§7.9), enforced at the API Gateway (Ch.3 §3.1) before a request reaches any individual service.

---

### 7.4  Common Conventions

**Pagination.** Cursor-based, not offset-based, chosen because the dataset is append-heavy and offset pagination silently skips or duplicates records when new entries are curated between page requests — a real risk given the platform's continuous curation pipeline.
```
GET /v1/entries?limit=50&cursor=eyJpZCI6ICJlbnRyeV8xMjM0In0
```
Response envelope:
```json
{
  "data": [ /* ... */ ],
  "pagination": {
    "next_cursor": "eyJpZCI6ICJlbnRyeV8xMjg0In0",
    "has_more": true
  }
}
```

**Filtering.** Query parameters map directly onto indexed, faceted fields defined in the Search Service (Ch.4 §4.3): `?domain=Oncology&institution_type=University+Research+Lab&result_type=Negative`.

**Sorting.** `?sort=date_concluded:desc` — a documented allow-list of sortable fields per resource, not arbitrary field sorting, to keep index design tractable.

**Standard error format — RFC 7807 (`application/problem+json`)**, uniform across every one of the nineteen services regardless of which one produced the error:
```json
{
  "type": "https://darkdatamedicine.org/errors/schema-validation-failed",
  "title": "Schema Validation Failed",
  "status": 422,
  "detail": "Field 'domain' must be one of the controlled vocabulary values.",
  "instance": "/v1/submissions/sub_a1b2c3",
  "errors": [
    { "field": "domain", "code": "invalid_enum_value", "received": "Onco" }
  ]
}
```
This single error contract is what lets a client — including the AI Service's own tooling (Ch.4 §4.5) — handle failures from any of the nineteen backing services identically, without service-specific error-parsing logic.

---

### 7.5  REST API Reference

Consolidated from every service's Chapter 4 endpoint table, organized by resource group, with request/response entities cross-referenced to their Chapter 5 Domain Model definitions.

#### 7.5.1  Submissions (Ch.4 §4.1 → Ch.5 §5.3.1)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `POST` | `/v1/submissions` | `SubmissionCreateRequest` (wraps a draft `Experiment`/`Hypothesis`/`Outcome`) | `201` → `Submission` | `submit:write` or anonymous (no-Git path) |
| `GET` | `/v1/submissions/{id}` | — | `200` → `Submission` (+ version history) | Owner or `review:write` |
| `GET` | `/v1/submissions/{id}/versions` | — | `200` → `SubmissionVersion[]` | Owner or `review:write` |
| `GET` | `/v1/submissions/{id}/status` | — | `200` → `{status, queue_position}` | Owner or `review:write` |

#### 7.5.2  Entries & Metadata (Ch.4 §4.2 → Ch.5 §5.1.1, §5.1.5)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/entries` | — (query params: filters, §7.4) | `200` → `Entry[]` (paginated) | Public |
| `GET` | `/v1/entries/{id}` | — | `200` → `Entry` (Experiment + Hypothesis + Outcome, resolved) | Public |
| `GET` | `/v1/entries/{id}/metadata` | — | `200` → `MetadataRecord` | Public |
| `GET` | `/v1/entries/{id}/export` | `?format=json-ld\|csv\|datacite-xml` | `200` → file stream | Public |
| `GET` | `/v1/entries/{id}/replications` | — | `200` → `Replication[]` | Public |

#### 7.5.3  Search (Ch.4 §4.3)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/search` | `?q=&domain=&institution_type=&result_type=&...` | `200` → `SearchResult[]` (ranked, faceted) | Public |
| `GET` | `/v1/search/facets` | — | `200` → `{facet: [{value, count}]}` | Public |

#### 7.5.4  Knowledge Graph (Ch.4 §4.4, `FUTURE`)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/graph/entity/{id}/neighbors` | `?relation=treats\|sameDrugClassAs\|...` (Ch.6 §6.7) | `200` → `GraphNode[]` | Public |
| `POST` | `/v1/graph/query` | Sandboxed graph-traversal query DSL | `200` → `GraphQueryResult` | Public (rate-limited) |

#### 7.5.5  AI Services (Ch.4 §4.5, `FUTURE`)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/ai/summarize/{entryId}` | — | `200` → `{summary, confidence}` | Public |
| `GET` | `/v1/ai/similar/{entryId}` | `?k=10` | `200` → `Entry[]` (semantic-ranked) | Public |
| `POST` | `/v1/ai/classify` | `{draft_text}` | `200` → `{suggested_domain, confidence}` | `submit:write` (curation aid only) |

#### 7.5.6  Authentication (Ch.4 §4.6)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/auth/login` | — | `302` redirect to ORCID OIDC | Public |
| `GET` | `/v1/auth/callback` | OIDC callback params | `200` → `{access_token, refresh_token}` | Public |
| `POST` | `/v1/auth/token/refresh` | `{refresh_token}` | `200` → `{access_token}` | Refresh token |
| `GET` | `/v1/auth/me` | — | `200` → `{researcher, role, scopes}` | Authenticated |

#### 7.5.7  Review / Curation (Ch.4 §4.8 → Ch.5 §5.3.2)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/review/queue` | `?domain=` | `200` → `CurationQueueEntry[]` | `review:write` |
| `POST` | `/v1/review/{submissionId}/decision` | `{decision, checklist_results, notes}` | `200` → `Review` | `review:write` |
| `GET`/`PUT` | `/v1/review/{submissionId}/checklist` | `ChecklistState` | `200` → `ChecklistState` | `review:write` |

#### 7.5.8  Dataset Releases & DOIs (Ch.4 §4.9 → Ch.5 §5.4.2–5.4.3)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/releases` | — | `200` → `DatasetRelease[]` | Public |
| `GET` | `/v1/releases/{version}` | — | `200` → `DatasetRelease` (frozen snapshot reference) | Public |
| `POST` | `/v1/releases` | `{release_notes}` | `201` → `DatasetRelease` (async, returns job status) | `admin:write` |

#### 7.5.9  Notifications (Ch.4 §4.7, `FUTURE`)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET`/`PUT` | `/v1/notifications/preferences` | `NotificationPreferences` | `200` → `NotificationPreferences` | Authenticated |
| `GET` | `/v1/notifications` | — | `200` → `Notification[]` | Authenticated |

#### 7.5.10  Analytics (Ch.4 §4.11)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/analytics/dashboard/{name}` | — | `200` → `Dashboard` | Public (public dashboards) / privileged (internal) |
| `POST` | `/v1/analytics/report` | `ReportSpec` | `202` → `{report_job_id}` | Authenticated |

#### 7.5.11  Federation (Ch.4 §4.12, `FUTURE`)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/federation/nodes` | — | `200` → `FederationNode[]` | Public |
| `POST` | `/v1/federation/sync` | Signed sync message | `200` → `SyncAck` | `federation:sync` (node-authenticated) |

#### 7.5.12  Ontology (Ch.4 §4.13 → Chapter 6)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/ontology/terms` | `?vocabulary=domain\|institution_type\|...&q=` | `200` → `OntologyTerm[]` | Public |
| `GET` | `/v1/ontology/terms/{id}/mappings` | — | `200` → `ExternalMapping[]` (Ch.6 §6.4) | Public |
| `GET` | `/v1/ontology/schemes/{scheme}/versions` | — | `200` → `ConceptSchemeVersion[]` (Ch.6 §6.5) | Public |

#### 7.5.13  Export / Import (Ch.4 §4.14–§4.15)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/export` | `?format=&filters` | `200` → file stream | Public |
| `POST`/`GET` | `/v1/export/scheduled` | `ScheduledExportConfig` | `200` → config | Authenticated (institutional partner) |
| `POST`/`GET` | `/v1/import/jobs` | `ImportJobConfig` | `202`/`200` → `ImportJob` | `admin:write` (system-account scoped) |
| `GET` | `/v1/import/sources` | — | `200` → `ImportSource[]` | `admin:write` |

#### 7.5.14  Audit, Monitoring, Backup, Administration (Ch.4 §4.16–§4.19, all privileged)

| Method | Path | Request Body | Response | Auth |
|---|---|---|---|---|
| `GET` | `/v1/audit/entries/{id}` | — | `200` → `AuditRecord[]` | `admin:write` |
| `POST` | `/v1/audit/query` | `AuditQuery` | `200` → `AuditRecord[]` | `admin:write` |
| `GET` | `/v1/monitoring/status` | — | `200` → `{status: "operational"\|"degraded"\|"outage"}` | Public (aggregate only) |
| `GET` | `/v1/monitoring/health/{service}` | — | `200` → detailed health | `admin:write` |
| `GET` | `/v1/backup/status` | — | `200` → `BackupJob[]` | `admin:write` |
| `POST` | `/v1/backup/restore` | `RestoreRequest` | `202` → job (requires dual-authorization, Ch.4 §4.18) | `admin:write` × 2 |
| `GET`/`PUT` | `/v1/admin/users` | `UserUpdateRequest` | `200` → `User` | `admin:write` |
| `GET`/`PUT` | `/v1/admin/config` | `SystemConfig` | `200` → `SystemConfig` | `admin:write` |
| `POST` | `/v1/admin/domains` | `DomainProposal` | `202` → routed to Ontology governance review (Ch.6 §6.5) | `admin:write` |

---

### 7.6  GraphQL Schema

The GraphQL surface exists specifically for the cross-entity, traversal-heavy queries REST's one-resource-per-request model handles awkwardly (Ch.3 §3.13). It is read-primary: mutations are intentionally limited to the subset of write operations that genuinely benefit from GraphQL's nested-input shape (primarily Submission creation with deeply nested Experiment/Hypothesis/Outcome data); every other write remains a REST operation, per the design principle in §7.1.

#### 7.6.1  Core Type Definitions (SDL excerpt)

```graphql
type Experiment {
  id: ID!
  title: String!
  domain: OntologyTerm!
  status: ExperimentStatus!
  dateStarted: Date
  dateConcluded: Date
  methodologySummary: String
  hypotheses: [Hypothesis!]!
  protocol: Protocol
  datasets: [Dataset!]!
  interventions: [Intervention!]!
  targetDisease: DiseaseCondition!
  conductedBy: [Researcher!]!
  conductedAt: [Institution!]!
  fundedBy: [Grant!]!
  outcomes: [Outcome!]!
  replications: [Replication!]!
  reviews: [Review!]!
  publications: [Publication!]!
}

type Hypothesis {
  id: ID!
  statement: String!
  expectedDirection: String
  confirmed: Boolean
  testedBy: [Experiment!]!
  outcome: Outcome
}

type Outcome {
  id: ID!
  resultType: OutcomeResultType!
  effectSize: Float
  statisticalSignificance: Float
  narrativeSummary: String
  terminationReason: String
  experiment: Experiment!
  concludesHypothesis: Hypothesis!
  evidence: [Evidence!]!
}

type Intervention {
  id: ID!
  type: InterventionType!
  name: String!
  interventionClass: InterventionClass
  sameDrugClassAs: [Intervention!]!
  externalMappings: [ExternalMapping!]!    # Ch.6 §6.4
}

type Researcher {
  id: ID!
  orcid: String
  displayName: String!
  affiliations: [Affiliation!]!
  experiments: [Experiment!]!
  reviews: [Review!]!
}

type Institution {
  id: ID!
  name: String!
  rorId: String
  institutionType: OntologyTerm!
  experiments: [Experiment!]!
}

type OntologyTerm {
  id: ID!
  vocabulary: String!
  label: String!
  broader: [OntologyTerm!]!
  narrower: [OntologyTerm!]!
  externalMappings: [ExternalMapping!]!
  deprecated: Boolean!
  supersededBy: OntologyTerm
}

enum ExperimentStatus { PLANNED ACTIVE TERMINATED COMPLETED }
enum OutcomeResultType { NEGATIVE NULL INCONCLUSIVE POSITIVE }
enum InterventionType { MOLECULE DRUG BIOLOGIC DEVICE BEHAVIORAL PROCEDURE OTHER }
```

#### 7.6.2  Query Type

```graphql
type Query {
  entry(id: ID!): Experiment
  entries(
    filter: EntryFilter
    sort: EntrySort
    pagination: PaginationInput
  ): EntryConnection!

  search(query: String!, filter: EntryFilter): SearchResultConnection!

  ontologyTerm(vocabulary: String!, id: ID!): OntologyTerm
  ontologyTerms(vocabulary: String!, query: String): [OntologyTerm!]!

  interventionClassNeighbors(interventionId: ID!): [Intervention!]!
    # The headline cross-drug-class query from Ch.6 §6.6.3, competency question 1

  researcher(orcid: String!): Researcher
  institution(rorId: String!): Institution
}
```

#### 7.6.3  Mutation Type

```graphql
type Mutation {
  createSubmission(input: SubmissionInput!): SubmissionPayload!
    # Deeply nested Experiment/Hypothesis/Outcome input — the primary
    # justification for a GraphQL mutation existing at all, per §7.1

  addReplication(input: ReplicationInput!): ReplicationPayload!
}
```

**Deliberate omission.** `updateEntry`, `approveSubmission`, `deleteEntry`, and every curation-decision mutation are intentionally **not** part of the GraphQL schema — those remain REST-only operations (`/v1/review/{id}/decision`, §7.5.7) specifically because Chapter 4 §4.8's Review Service treats every curation decision as a security- and audit-sensitive action best served by REST's simpler, more auditable per-operation endpoint shape rather than GraphQL's more flexible, harder-to-statically-audit mutation surface.

#### 7.6.4  Example Query (Competency Question 1 from Ch.6 §6.6.3)

```graphql
query NegativeResultsAcrossDrugClass($interventionId: ID!) {
  interventionClassNeighbors(interventionId: $interventionId) {
    name
    experiments {
      title
      conductedAt { name institutionType { label } }
      outcomes { resultType narrativeSummary }
    }
  }
}
```

---

### 7.7  Webhooks and Event Subscriptions

For institutional partners (Ch.4's Federation and Notification services) needing push-based integration rather than polling:

```
POST /v1/webhooks
{
  "url": "https://partner.example.edu/ddm-webhook",
  "events": ["entry.published", "release.published"],
  "secret": "<partner-provided HMAC signing secret>"
}
```

Every webhook delivery is signed (`X-DDM-Signature` header, HMAC-SHA256) so the receiving partner can verify authenticity without a separate authenticated callback — consistent with the Zero Trust principle (Ch.2 §2.3.7) applied to outbound, not just inbound, traffic. Delivery failures are retried with exponential backoff and, after a documented threshold, the subscription is marked degraded and the partner notified via the Notification Service (Ch.4 §4.7).

---

### 7.8  Rate Limiting and Quotas

| Client Category | Default Limit | Rationale |
|---|---|---|
| Anonymous (public search/read) | 60 req/min | Prevents casual scraping while keeping the search experience unrestricted for real users |
| Authenticated contributor | 300 req/min | Comfortably supports the no-Git and CLI submission paths (Ch.4 §4.1) |
| Institutional partner (API key) | 3,000 req/min, negotiable | Sized for scheduled bulk export/sync workloads (§7.5.13) |
| System account (internal service-to-service) | Not globally limited; per-service quotas set individually | Internal traffic is governed by service-level capacity planning, not a uniform external-facing limit |

Rate-limit state is communicated via standard `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` headers on every response, enforced at the API Gateway (Ch.3 §3.1) before a request reaches any backing service — keeping rate-limit logic in exactly one place rather than duplicated across nineteen services.

---

### 7.9  SDK and Client Generation

Per Ch.2 §2.3.3 (API First) and Ch.3 §3.13's rationale for choosing OpenAPI, every REST endpoint in §7.5 is defined in a single canonical `openapi.yaml` specification, from which:

- Language-specific client SDKs (Python, R, JavaScript/TypeScript — chosen as the three most common languages among the platform's target contributor and institutional-partner base) are generated automatically on every API version release, never hand-maintained separately and allowed to drift.
- The CLI (`ddm`, referenced throughout Ch.4) is itself built as a thin wrapper over the generated Python SDK, guaranteeing the CLI can never expose a capability the documented API does not also expose — directly enforcing the API First principle rather than merely aspiring to it.
- API documentation (a human-readable reference site) is rendered directly from the same `openapi.yaml`, so the documentation and the implementation cannot diverge without the divergence being immediately visible as a spec-validation failure in CI.

The GraphQL schema (§7.6) is similarly the single source of truth for GraphQL client code generation (via standard GraphQL code-generation tooling), consistent with the same never-hand-maintained-twice principle.

---

### 7.10  API Governance and Change Management

Every change to `openapi.yaml` or the GraphQL SDL is itself subject to the schema-change governance process established in Chapter 2 §2.6 (principle 6) and Chapter 6 §6.5: a documented rationale, an explicit statement of whether the change is additive (§7.2) or breaking, and — for any breaking change — a migration guide published alongside the deprecation notice. The API specification is version-controlled in the same repository discipline as the codebase itself, and every historical version remains permanently retrievable, per Ch.2 §2.6 principle 15, so that a partner integration built against a two-year-old API version can always retrieve the exact contract it was built to.

---

### 7.11  Implementation Status Summary

| Surface | Status |
|---|---|
| REST `/v1/entries`, `/v1/search` (read-only) | `PLANNED` (static-index equivalent `OPERATIONAL` today, Ch.4 §4.3) |
| REST `/v1/submissions` (write) | `PLANNED` (Git PR path `OPERATIONAL` today) |
| REST `/v1/ontology/*` | `PLANNED` |
| REST privileged endpoints (`/v1/admin/*`, `/v1/audit/*`, `/v1/backup/*`) | `PLANNED` |
| GraphQL schema and endpoint | `PLANNED` |
| Webhooks | `FUTURE` |
| Generated SDKs (Python/R/JS) | `FUTURE` |
| API Gateway, rate limiting, versioning infrastructure | `PLANNED` |

---

### 7.12  Summary and Handoff

This chapter is the single point of truth for how any client — human or machine, first-party or partner — talks to the platform, consolidating what Chapter 4 scoped per-service into one versioned, authenticated, uniformly-erroring contract, and formalizing the GraphQL surface Chapter 3 committed to but did not itself specify. The Security Architecture chapter's task is to take the authentication, authorization, and rate-limiting posture summarized here (§7.3, §7.8) and specify it to threat-model depth; the Deployment Architecture chapter's task is to specify exactly how the API Gateway and the services behind it are actually deployed, scaled, and secured in a real infrastructure environment, building on the staged scalability plan in Ch.3 §3.10.
