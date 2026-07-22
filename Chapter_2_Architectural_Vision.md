# Dark Data Medicine — Platform Architecture Series

## Chapter 2: Architectural Vision

*Document status: Normative. This chapter governs all subsequent architecture documents in the series — Domain Model, Database Schema, Ontology, API Specification, Backend Architecture, Frontend Architecture, and AI Services Architecture. Any design decision in a downstream document that conflicts with a principle stated here requires an explicit, recorded deviation (see §2.11).*

*Version 0.1 — Draft for governance review*

---

### 2.0  Purpose and Scope of This Chapter

This chapter does not describe what Dark Data Medicine does. That is the subject of the Domain Model (Chapter 3). It describes *why the system is built the way it is built* — the mission the architecture serves, the multi-decade horizon it is designed against, the philosophical commitments that constrain every technical decision downstream of this document, and the quality attributes by which any proposed change should be judged.

The distinction matters because a registry for negative scientific results carries a specific architectural risk that most software projects do not: its value is almost entirely a function of *trust sustained over decades*, not feature velocity. A negative-results registry that loses researcher trust — through opacity, vendor lock-in, editorial capture, or simple disappearance when its founding maintainer moves on — does not merely lose users. It re-teaches the research community the exact lesson that motivated this project in the first place: that negative findings have nowhere durable to go. This chapter exists to make that failure mode structurally difficult, not merely undesirable.

---

### 2.1  Mission

> **Dark Data Medicine exists to become the world's most trusted open infrastructure for publishing, preserving, discovering, and analyzing negative scientific evidence.**

This is written as a technical mission statement, not a marketing line, and every word in it is a constraint rather than an aspiration:

- **Trusted** — trust is not claimed; it is engineered, through the transparency, auditability, and governance-independence properties formalized throughout this chapter (§2.9 in particular).
- **Open** — every layer of the stack, from schema to source code to governance decisions, is inspectable and forkable by a party outside the founding organization. Openness is a load-bearing architectural property, not a licensing footnote.
- **Infrastructure** — the platform is designed to be *depended upon* the way a DOI registrar or a domain-name system is depended upon: boring, stable, and replaceable in principle even though it is not, in practice, expected to be replaced.
- **Publishing, preserving, discovering, and analyzing** — four distinct architectural capabilities, not one. A system that only publishes (accepts submissions) without preserving (guaranteeing long-term retrievability) has built a mailbox, not a registry. A system that preserves without enabling discovery has built an archive, not infrastructure. A system that enables discovery without analysis has built a search engine, not a scientific instrument. All four capabilities are treated as first-class architectural concerns from this document forward.
- **Negative scientific evidence** — deliberately not restricted to "negative clinical trials." The domain model already spans molecules, devices, behavioral interventions, and procedures across nine clinical and life-science domains, and the architectural principles in this chapter are written to generalize past medicine specifically, consistent with the future-evolution horizon in §2.10.

---

### 2.2  Long-Term Vision

Architecture decisions made today either compound favorably or become liabilities over a twenty-year horizon; there is rarely a neutral outcome. This section states the horizon explicitly so that every subsequent design document can be evaluated against it.

> **Twenty-year vision:** *A globally distributed scientific infrastructure where every failed experiment can be discovered before another researcher unknowingly repeats it — operated not by a single organization, but by a federation of institutions, national registries, and independent mirrors, none of which is individually load-bearing for the system's continued existence.*

Three properties of this vision have immediate, present-day architectural consequences, not merely future ones:

1. **Global distribution is a day-one constraint, not a day-2000 migration project.** A system designed as a centralized monolith and "federated later" typically cannot be federated later without a full data-model rewrite, because centralized assumptions (single source of truth for identifiers, single authority for conflict resolution, single point of trust for validation) leak into every layer of a codebase. Federation-readiness is therefore addressed structurally in §2.3 (Federation First) and must be reflected in the identifier scheme defined in the forthcoming Domain Model chapter.
2. **No single institution should be able to end the project by ending its involvement.** This has already shaped governance decisions (the published governance charter's explicit commitment to a multi-maintainer transition) and must equally shape technical decisions: no proprietary format, no single-vendor managed database, no build step that only runs on infrastructure one organization controls.
3. **Twenty years is longer than most software frameworks live.** A framework released today has a realistic probability of being unmaintained, in the conventional sense, well before 2046. This motivates the technology-independence principle formalized in §2.8: the architecture's guarantees must be expressible independently of any specific programming language, database engine, or cloud provider, so that a future maintainer can re-implement the *architecture* without renegotiating the *mission*.

---

### 2.3  Architectural Philosophy

A list of buzzwords ("API First," "AI First") is not a philosophy; it is a slogan. Each principle below is stated with its **rationale** (why the principle exists) and its **consequences** (what it structurally forbids or requires), because a principle that cannot be violated in a checkable way is not an architectural constraint — it is a preference.

#### 2.3.1  FAIR First

**Principle.** Every object stored in the platform — every entry, every dataset release, every contributor record — shall satisfy the FAIR principles: Findable, Accessible, Interoperable, and Reusable.

**Rationale.** Scientific data that cannot be found or reused has little long-term value regardless of its scientific merit; a negative result sitting in an unindexed file is architecturally indistinguishable from a negative result that was never recorded at all. FAIR is not a data-management best practice layered on top of the system — it is the system's entire reason for existing, restated as an engineering requirement.

**Consequences.**
- Metadata is mandatory on every object; no entity may exist in a storeable-but-undescribed state.
- Every entry and every dataset release carries a persistent identifier (entry-level identifiers today; DOIs at the release level from the point the versioned-release pipeline goes live).
- Data formats are open standards (JSON Schema-validated JSON today; any future storage-layer migration must preserve open, documented serialization).
- Every dataset is exportable in a machine-readable form without requiring access to the platform's own tooling — a CSV or JSON export must remain independently interpretable by a researcher who has never seen the platform's source code.

#### 2.3.2  Metadata First

**Principle.** Metadata is more important than storage.

**Rationale.** Storage without metadata is undiscoverable, and a scientific registry's entire architectural purpose is discovery, not custody. A byte-perfect backup of an unlabelled dataset is a preservation success and a discovery failure; this project treats the latter as the more severe failure mode, because a discovery failure silently reproduces the exact "dark data" problem the platform exists to solve, while a preservation failure is at least visible and correctable.

**Consequences.** Every entity in the system — every file, every experiment record, every dataset DOI, every contributor — must expose structured, queryable metadata as a precondition of being considered "in" the system, not as an optional enrichment applied afterward. Metadata schemas are versioned artifacts subject to the same change-control discipline as code (§2.6).

#### 2.3.3  API First

**Principle.** Every functionality must exist as an API before it exists as a user interface.

**Rationale.** A capability that exists only inside a user interface is a capability the platform's own automation, its downstream integrators (systematic-review tooling, institutional data pipelines, future AI services), and its eventual federated mirrors cannot use. API-first is the mechanism by which the platform avoids becoming, over its twenty-year horizon, a single website that happens to hold important data — the failure mode most directly opposite to the infrastructure mission in §2.1.

**Consequences.** REST and, where graph-shaped queries are the natural access pattern (trend analysis across intervention–outcome relationships), GraphQL interfaces; OpenAPI specifications maintained as the canonical, versioned contract for every endpoint; a command-line interface and language SDKs as thin clients over the same API surface the web interface itself consumes — with no privileged, API-inaccessible path reserved for the first-party frontend.

#### 2.3.4  AI First

**Principle.** Every scientific object should be understandable by both humans and AI systems.

**Rationale.** A twenty-year infrastructure horizon (§2.2) cannot credibly assume the discovery tooling of 2046 resembles a keyword search box. Systematic-review workflows are already moving toward AI-assisted evidence synthesis; a registry whose content is only legible to a human reading a web page will be structurally excluded from that workflow within the lifetime of this architecture, regardless of how well-curated its content is.

**Consequences.** Structured metadata (§2.3.2) as the substrate every AI-facing capability builds on, rather than free-text scraping; vector embeddings generated over entry content to support semantic — not merely keyword — search; an explicit knowledge-graph representation connecting interventions, targets, outcomes, and institutions (elaborated in the forthcoming Ontology chapter); and LLM-integration points designed against the same API surface defined in §2.3.3, so that AI access is a client of the platform, never a privileged internal shortcut around its validation and provenance guarantees.

#### 2.3.5  Open Science First

**Principle.** Everything that can legally and ethically be public should be public.

**Rationale.** This is the direct architectural expression of the platform's mission (§2.1): a registry that defaults to restriction, requiring an active decision to make each object public, will systematically under-share relative to a registry that defaults to openness and requires an active, justified decision to restrict. Given that the platform exists specifically to counteract a research culture's tendency toward under-sharing (documented at length in the companion funding case for this project), its own default behavior must not reproduce that tendency.

**Consequences.** Public-by-default visibility for all schema-conformant, curator-approved entries; CC0-1.0 as the recommended default license, with CC-BY-4.0 available where attribution is required by a contributor's institutional policy; no paywall, account requirement, or embargo period applied to published entries as a platform-level default.

#### 2.3.6  Privacy by Design

**Principle.** Everything that must remain private should remain private forever.

**Rationale.** "Open by default" (§2.3.5) is only a defensible architectural stance if it is paired with an equally strict, structurally enforced privacy boundary — specifically around patient-identifiable information, which has no scientific value to the registry's mission and carries severe harm potential if exposed. This is not in tension with §2.3.5; it defines exactly where its default flips.

**Consequences.** Patient-level data is categorically out of scope for the schema — the domain model operates at the level of the study, never the individual — and this exclusion is enforced at the schema-validation layer (an object containing fields that resemble patient identifiers should be rejected structurally, not merely caught by curator review). Private fields, once excluded, are excluded permanently; "private now, public later" is not a supported state transition for any field type carrying re-identification risk.

#### 2.3.7  Zero Trust

**Principle.** Never trust users, services, requests, or files by default. Everything is validated.

**Rationale.** A registry whose entire value proposition rests on data trustworthiness (§2.1's "trusted") cannot architecturally afford an unvalidated path from any input surface to the published dataset. This applies as much to the platform's own automation (an extraction tool's draft output is not more trusted than a human submission; see the two-layer validation model already operating in production) as to external actors.

**Consequences.** Every write path — human submission, automated extraction, federated mirror synchronization, future AI-assisted curation suggestion — passes through the same schema-validation and provenance-verification gates; no internal service, including the platform's own tooling, is granted a privileged bypass of those gates; every request is authenticated and authorized at the API layer defined in §2.3.3 regardless of its origin.

#### 2.3.8  Federation First

**Principle.** The platform should never assume that all data lives on one server.

**Rationale.** This is the direct technical implementation of the twenty-year vision in §2.2: a federated future cannot be retrofitted onto a codebase whose identifier scheme, conflict-resolution model, and trust model assume a single authoritative database. Federation-readiness must be a day-one property of the data model even while the system operates, in its early years, as a single deployment.

**Consequences.** Globally unique, location-independent entity identifiers (not auto-incrementing database keys); a conflict-resolution and provenance model that can attribute any entry to its originating node even after synchronization across mirrors; a synchronization protocol treated as a first-class API surface (§2.3.3) rather than an internal database-replication detail.

#### 2.3.9  Cloud Agnostic

**Principle.** The architecture supports AWS, Azure, Google Cloud, self-hosted deployment, university clusters, and national research infrastructure equally.

**Rationale.** A twenty-year infrastructure commitment cannot be tied to any single commercial cloud vendor's continued pricing, availability, or existence, and — more immediately relevant given this project's institutional-partnership strategy — university and national research infrastructure operators frequently cannot or will not deploy onto a specific commercial vendor's proprietary managed services, which would otherwise exclude exactly the institutional mirrors the federation vision in §2.3.8 depends on.

**Consequences.** No dependency on a cloud vendor's proprietary managed database, proprietary function-execution runtime, or proprietary object-storage API where an open, portable equivalent exists; infrastructure-as-code expressed in vendor-neutral tooling where practical; the platform's already-adopted static-first architecture for its public-facing search interface is a direct, present-day instance of this principle — a static site is, definitionally, cloud-agnostic.

---

### 2.4  Core Design Goals

The philosophy in §2.3 is normative; this section restates it as a checklist against which any proposed feature or design document should be evaluated:

| Goal | Direct Architectural Expression |
|---|---|
| Simple submission | No-Git contribution path; minimal required schema fields (§2.6) |
| Machine readable | JSON Schema validation on every object (§2.3.1, §2.3.2) |
| Fully versioned | Schema versioning, dataset release versioning, code versioning under uniform change-control discipline |
| Highly auditable | Every decision — curatorial, governance, architectural (§2.11) — recorded and retrievable |
| Scientifically reproducible | Structured methodology fields; source-verifiability requirement in curation |
| Globally scalable | Federation-first data model (§2.3.8); cloud-agnostic deployment (§2.3.9) |
| Long-term maintainable | Technology independence (§2.8); no single-maintainer dependency (§2.5) |
| Vendor independent | No proprietary database, cloud runtime, or file format dependency (§2.5, §2.8) |
| Open by default | FAIR First, Open Science First (§2.3.1, §2.3.5) |
| Accessible to AI | AI First (§2.3.4); structured metadata substrate |

A design document in the downstream series that cannot point to which row of this table it advances should be treated as out of scope for this architecture, or as a candidate for the deviation process in §2.11.

---

### 2.5  Architectural Constraints

Where §2.3–2.4 state what the architecture pursues, this section states what it structurally refuses, as hard constraints rather than preferences:

**The architecture SHALL NOT:**

1. Depend on a commercial cloud vendor's proprietary, non-portable services for any capability that has an open, portable equivalent.
2. Depend on a proprietary database engine where an open-source, standards-compliant engine (or, as at present, a flat validated-file store) is sufficient.
3. Require expensive per-seat or per-usage commercial licenses for any component in the core validation, storage, or discovery path.
4. Depend on a single maintainer for continued operation — technically (bus-factor-one deployment knowledge) or organizationally (the governance transition already committed to in the project's public charter is the direct organizational mitigation for this constraint; this architecture chapter is its technical counterpart).
5. Depend on a single institution as the sole host of the canonical dataset, once the federation model (§2.3.8) is operational.
6. Require vendor lock-in of any kind — export formats, authentication schemes, and storage layers must all be replaceable without a full data migration project.

Each constraint above is written to be checkable: a design proposal either introduces a dependency the constraint forbids, or it does not. This is deliberate. A constraint phrased as "prefer open standards" cannot be enforced in review; a constraint phrased as "SHALL NOT depend on a proprietary database engine" can be.

---

### 2.6  Architectural Principles

The following principles apply uniformly across every entity, service, and interface in the system. They are intentionally granular — closer to invariants than to guidelines — because a twenty-year infrastructure project benefits more from a large number of small, unambiguous rules than from a small number of large, interpretable ones.

1. Every entity has a globally unique, persistent identifier.
2. Every entity has structured, queryable metadata.
3. Every change to any entity is versioned; nothing is silently overwritten.
4. Every API is documented in a machine-readable specification before it is documented in prose.
5. Every submission is validated against a published schema before acceptance.
6. Every schema is itself versioned, with a documented migration path between versions.
7. Every governance and architectural decision that departs from this chapter is recorded, dated, and attributed (§2.11).
8. Everything the platform claims to do is testable by an external party, not merely by internal assertion.
9. Every published result is, in principle, reproducible from its recorded methodology and source metadata.
10. Everything is exportable in an open, documented format without requiring the platform's own tooling to interpret it.
11. Everything published is citeable at a stable, resolvable identifier.
12. Everything is machine readable as a first-class property, not as an accessibility add-on.
13. No entity's public visibility is conditional on any funder's, sponsor's, or donor's preference (this principle is the technical mirror of the governance charter's non-waivable funder-independence rule).
14. No validation gate may be bypassed by an internal service, automated tool, or administrative role without leaving an equally auditable record as a human-submitted entry would.
15. Every deprecation of a schema field, API endpoint, or identifier scheme preserves resolvability of previously issued identifiers, even after the field or endpoint itself is retired.

---

### 2.7  System Quality Attributes

Functional correctness — the system does what its specification says — is necessary but insufficient for infrastructure with a twenty-year horizon. The following quality attributes are treated as co-equal architectural requirements, each owned by a specific, testable expectation:

| Attribute | Architectural Expectation |
|---|---|
| **Availability** | The discovery surface (search) degrades gracefully under backend failure, consistent with a static-first architecture that has no single live-service dependency for read access. |
| **Reliability** | Validation and curation gates behave identically on every run given identical input; no non-deterministic acceptance behavior. |
| **Performance** | Search and trend-analysis operations remain responsive at the scale projected through the platform's population roadmap, without requiring architecture changes at each order-of-magnitude growth step. |
| **Integrity** | No entry's recorded content changes without a versioned, attributed edit record. |
| **Security** | Zero Trust (§2.3.7) applied uniformly; no privileged unauthenticated write path. |
| **Maintainability** | A new contributor can understand and safely modify any single component without full-system context, given the documentation this principle requires. |
| **Portability** | The system can be redeployed onto a materially different infrastructure stack without a data-model rewrite (§2.8, §2.9). |
| **Accessibility** | Both the human-facing interface (WCAG-conformant) and the non-technical contribution path (§2.3's API-first model notwithstanding) remain usable by contributors without specialized technical tooling. |
| **Interoperability** | Every export and API response is consumable by a third-party system without platform-specific tooling, per FAIR First (§2.3.1). |
| **Extensibility** | New domains, schema fields, and entity types can be added through a documented migration process (§2.6, item 6) without breaking existing consumers. |
| **Auditability** | Every consequential decision — curatorial, governance, or architectural — is independently reconstructable from the historical record. |
| **Observability** | The health of the validation pipeline, curation queue, and federation synchronization process (once operational) is externally monitorable, not only internally visible. |
| **Reproducibility** | A published entry's methodology and outcome fields contain sufficient structure for the described finding to be independently assessed. |
| **Transparency** | Governance decisions, funding relationships, and architectural deviations (§2.11) are public by the same Open Science First default (§2.3.5) applied to scientific content. |

---

### 2.8  Technology Independence

**Principle.** The architecture — as a set of guarantees, identifiers, schemas, and interfaces — does not depend on any specific programming language, database engine, cloud provider, or application framework.

**Statement.** The architecture explicitly does not depend on Python, or any other specific language; on any specific relational, document, or graph database product; on any specific cloud provider; or on any specific web or API framework. These are implementation choices, made and documented at the level of individual services, and each is expected to be replaceable without requiring a change to this chapter.

**Rationale.** Section 2.2 states a twenty-year horizon; very few specific technology choices made in 2026 will remain the obvious choice in 2046. An architecture that survives technology change is one whose guarantees are stated independently of implementation — a principle already implicit in the platform's current design (a JSON Schema is a technology-independent contract; the Python validator that currently enforces it is one interchangeable implementation of that contract, and a reimplementation in any other language that satisfies the same schema is, by this principle, architecturally equivalent).

**Consequence for downstream documents.** The Backend Architecture and API Specification chapters should describe *current* implementation choices explicitly labeled as such, distinct from the *permanent* guarantees stated in this chapter and inherited by the Domain Model and Ontology chapters. A future maintainer replacing the current Python tooling with an equivalent implementation in another language should not need to revise this chapter at all.

---

### 2.9  Scientific Integrity Principles

This section is the architecture's direct answer to the question a skeptical researcher, funder, or journalist is most likely to ask: *why should anyone trust a dataset of negative results curated by an independent project?* Each principle below is a structural, not merely declared, answer.

1. **No sponsor influence.** No funder, sponsor, or donor is granted any influence over which entries are accepted, rejected, or featured — a rule already codified as non-waivable in the project's published governance charter, and reinforced architecturally by principle 13 in §2.6 (no visibility gate conditional on funder preference).
2. **No editorial bias.** Curation criteria (methodological completeness, provenance verifiability, non-duplication) are outcome-direction-independent by design; a negative result is never evaluated on whether it is "interesting," only on whether it is genuine and well-documented.
3. **Transparent governance.** Governance decisions are recorded and public, consistent with the Transparency quality attribute in §2.7.
4. **Version history forever.** No entry's history is deletable; corrections are recorded as new versions layered over, not replacing, the original submission record.
5. **Permanent citations.** Every published identifier remains resolvable indefinitely, per §2.6 principle 15 — an identifier is a promise, and breaking it after the fact is treated as an architectural failure, not a routine cleanup.
6. **Immutable releases.** Once a versioned dataset release is published (via the DOI-backed release process), its content at that version is frozen; subsequent corrections appear in a later version, never as a silent edit to a released one.
7. **Conflict-of-interest disclosure.** Contributor and institutional affiliation is captured as structured metadata (§2.3.2), not omitted, so that any future analysis of the dataset can account for potential source bias transparently rather than assuming a neutrality the platform cannot itself guarantee.
8. **Human accountability.** Every accepted entry has an identifiable accountable curator of record, even where automated tooling assisted extraction — automation assists; it is never the accountable party (a direct architectural expression of Zero Trust, §2.3.7, applied to the platform's own tooling).
9. **Machine validation.** Structural and schema-level integrity is enforced by automated validation on every write, independent of and prior to human judgment, so that no entry's basic conformance depends on a curator remembering to check it manually.

---

### 2.10  Future Evolution

The architecture described in this chapter is deliberately built to accommodate — without requiring a rewrite to accommodate — the following future directions, each of which extends rather than contradicts a principle already stated above:

- **AI-native discovery and curation assistance**, building directly on the AI First principle (§2.3.4) and the structured-metadata substrate it depends on (§2.3.2).
- **A formal knowledge graph** connecting interventions, molecular targets, disease conditions, and outcomes, extending the Metadata First principle (§2.3.2) into an explicitly queryable graph structure, detailed in the forthcoming Ontology chapter.
- **Quantum-safe cryptographic signatures** for entry and release provenance, as an evolution of the integrity guarantees in §2.7 and §2.9, adopted ahead of, rather than in reaction to, the point at which current signature schemes become a credible long-term risk — consistent with the twenty-year horizon in §2.2.
- **Federated repositories and institutional mirrors**, the direct realization of the Federation First principle (§2.3.8) and the twenty-year vision (§2.2), moving the platform from a single deployment to a distributed network without requiring the identifier or trust model to change, because both were designed federation-ready from the outset.
- **National registry interoperability**, allowing government and institutional research-infrastructure operators to run compliant mirrors or synchronized nodes, enabled by the Cloud Agnostic (§2.3.9) and Technology Independence (§2.8) principles, which remove the deployment barriers such operators most commonly face.
- **Global replication and semantic reasoning** over the full federated dataset, the natural end state of combining the knowledge-graph, federation, and AI-first directions above into a single distributed scientific reasoning substrate — explicitly framed here as a long-horizon direction this chapter makes *possible*, not as a near-term deliverable of any currently funded program of work.

---

### 2.11  Architectural Decision Principles

*(Added per governance recommendation: these are not individual Architectural Decision Records — those are logged separately as ADRs when specific decisions are made — but the standing rules by which every future ADR is judged.)*

1. **Standards before invention.** Where an international standard already exists and is fit for purpose, it is adopted before a project-specific alternative is designed. A bespoke solution is permissible only where a documented gap analysis shows no suitable standard exists.
2. **Interoperability over local optimization.** A design choice that improves this platform's internal performance or convenience at the cost of interoperability with the broader open-science ecosystem (identifier schemes, metadata standards, licensing norms) requires explicit justification and is disfavored by default.
3. **Open formats over proprietary ones.** Where a proprietary format offers a short-term implementation advantage over an open equivalent, the open format is chosen unless the proprietary format is the only option capable of meeting a stated, documented requirement.
4. **Every new capability must advance at least one of: FAIR compliance, reproducibility, transparency, or reuse of data.** A feature that advances none of these — however useful it may seem in isolation — is out of scope for this architecture and belongs, if anywhere, in a separate, clearly bounded project.
5. **Every major change must be justifiable on both scientific and technical grounds.** A technically elegant change that does not serve the mission in §2.1 is not adopted on elegance alone; a scientifically motivated change that cannot be implemented within the constraints of §2.5 and §2.8 is returned for redesign, not exempted from those constraints.

These five rules exist because a twenty-year infrastructure project will, by design, outlive its founding maintainer's direct involvement in most individual decisions. Dozens of future contributors and researchers will make architectural choices this document's authors will never review individually. The principles in this section — not any specific technology choice elsewhere in this chapter — are what keep those future choices coherent with each other and with the mission stated in §2.1.

---

### 2.12  Summary: How to Use This Chapter

This chapter should be read, in downstream architecture documents, as a constraint satisfaction problem rather than as background reading. Before a design decision is finalized in the Domain Model, Database Schema, Ontology, API Specification, Backend Architecture, Frontend Architecture, or AI Services Architecture chapters, it should be checked against:

- Does it serve the mission stated in §2.1?
- Is it consistent with the twenty-year vision in §2.2?
- Does it violate any philosophy in §2.3 or any hard constraint in §2.5?
- Does it advance at least one goal in §2.4?
- Does it comply with every applicable principle in §2.6?
- Does it uphold the quality attributes in §2.7?
- Does it preserve technology independence (§2.8) and scientific integrity (§2.9)?
- Does it keep the future-evolution paths in §2.10 open rather than foreclosing them?
- If it deviates from any of the above, has that deviation been justified against the decision principles in §2.11 and recorded as an ADR?

A design that cannot answer these questions affirmatively is not ready for the downstream chapters this document governs.
