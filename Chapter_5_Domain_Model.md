# Dark Data Medicine — Platform Architecture Series

## Chapter 5: Domain Model

*Document status: Normative. Governed by Chapter 2 (Architectural Vision) and Chapter 3 (High-Level System Architecture). Directly consumed by the Database Schema, Ontology, and API Specification chapters — every table, graph node type, and API resource in those documents must trace back to an entity defined here.*

*Version 0.1 — Draft for governance review*

---

### 5.0  From Servers to Science

Chapters 3 and 4 described machines: services, databases, events, APIs. This chapter describes none of that. It describes the world the platform is *about* — the entities a researcher, curator, or funder would recognize and reason about even if every server in Chapter 4 disappeared and had to be rebuilt from scratch. A domain model that is well-designed survives a complete technology rewrite; a domain model that leaks implementation detail (a "row," a "JSON field," a "service") does not deserve the name.

This chapter is organized into six zones, reflecting the natural structure of the scientific and institutional world the platform models:

| Zone | Concern |
|---|---|
| **A — Scientific Core** | The experiment, its hypothesis, its outcome, and everything methodologically between them |
| **B — People & Institutions** | Who did the work and where |
| **C — Governance & Provenance** | How a finding is reviewed, trusted, corrected, and attributed |
| **D — Publishing & Identity** | How a finding becomes citable, permanent infrastructure |
| **E — Ontology & Classification** | The controlled vocabulary that makes the whole graph queryable |
| **F — Funding & Policy Context** | The economic and regulatory environment a finding exists within |

Sections 5.1–5.6 specify the flagship entities of each zone in full detail — attributes, relationships, cardinality, lifecycle, and invariants — because these are the entities every downstream document depends on most heavily. Section 5.7 is a comprehensive catalog of every supporting entity across all six zones, at the level of detail appropriate to each: enough to scope the Database Schema and Ontology chapters correctly, without inventing false precision for entities that are, at this stage, deliberately still open design questions.

---

### 5.1  Zone A — Scientific Core (Fully Specified)

#### 5.1.1  Experiment

**Definition.** A bounded, methodologically defined act of scientific inquiry — a clinical trial, a preclinical assay, a behavioral study, or a procedural evaluation — undertaken to test one or more Hypotheses.

**Attributes.** `experiment_id` (global, persistent identifier); `title`; `domain` (controlled vocabulary, Zone E); `status` (`Planned` / `Active` / `Terminated` / `Completed`); `date_started`; `date_concluded`; `methodology_summary`; `sample_size` (where applicable); `preregistration_reference` (optional, link to an external registry record).

**Relationships.**
| Relationship | Cardinality | Target Entity |
|---|---|---|
| tests | 1..* → 1..* | Hypothesis |
| follows | 1 → 0..1 | Protocol |
| produces | 1 → 0..* | Dataset |
| produces | 1 → 0..* | Outcome |
| conducted by | 1 → 1..* | Researcher |
| conducted at | 1 → 1..* | Institution |
| funded by | 1 → 0..* | Grant |
| targets | 1 → 1 | Disease (or other Condition) |
| evaluates | 1 → 1..* | Intervention (Drug / Device / Behavioral / Procedure) |
| replicated by | 1 → 0..* | Replication |
| reviewed via | 1 → 1..* | Review |
| cited in | 1 → 0..* | Publication |

**Lifecycle.** `Planned → Active → {Terminated | Completed} → Curated → Published`. An Experiment cannot enter `Curated` state without at least one associated Outcome and at least one completed Review (Zone C).

**Invariants.** An Experiment's `date_concluded` must postdate `date_started`; a `Terminated` Experiment must record a termination reason as part of its associated Outcome; an Experiment cannot be deleted once `Published` — only superseded by a new versioned record (Ch.2 §2.9, Immutable Releases).

#### 5.1.2  Hypothesis

**Definition.** A specific, falsifiable statement an Experiment is designed to test — the entity that gives a negative Outcome its scientific meaning. Without a recorded Hypothesis, a null result is merely an absence of data, not a negative finding.

**Attributes.** `hypothesis_id`; `statement` (structured or free text); `expected_direction` (e.g., "intervention reduces X relative to control"); `confirmed` (boolean, set only after Outcome is recorded).

**Relationships.** tested by → Experiment (many-to-many: one Experiment may test several Hypotheses; one Hypothesis, particularly a well-known one, may be tested by several independent Experiments — the specific relationship the Knowledge Graph Service, Ch.4 §4.4, is built to surface at scale); confirmed/disconfirmed by → Outcome.

**Invariants.** A Hypothesis's `confirmed` field is immutable once set by a curator-approved Outcome — reopening a settled Hypothesis requires a new Experiment and a new Hypothesis record referencing the original, never an edit to the original.

#### 5.1.3  Protocol

**Definition.** The documented methodological plan governing how an Experiment is conducted — the entity that makes an Experiment's Outcome reproducible in principle, per the Reproducibility quality attribute (Ch.2 §2.7).

**Attributes.** `protocol_id`; `version`; `design_type` (RCT, cohort, case-control, preclinical assay, etc.); `blinding` (none/single/double); `primary_endpoint`; `statistical_analysis_plan_summary`; `external_registry_url` (optional, e.g., a ClinicalTrials.gov protocol record).

**Relationships.** governs → Experiment (1 → 1..*, since a single protocol template may govern a multi-site Experiment); amended by → Protocol (self-referential, versioned amendment history).

**Invariants.** Protocol amendments create a new versioned Protocol record linked to the prior version — the amendment history itself is scientifically significant (a protocol amended after seeing partial results is a documented methodological risk factor) and is never overwritten.

#### 5.1.4  Dataset

**Definition.** The structured or unstructured data artifact an Experiment produces — distinct from the Outcome (the scientific conclusion drawn from it), because a Dataset can in principle be reused to test a different Hypothesis than the one it was originally collected for.

**Attributes.** `dataset_id`; `format`; `size`; `license` (Zone D); `access_level` (public / restricted / embargoed); `checksum` (integrity verification).

**Relationships.** produced by → Experiment; described by → Metadata Record (Ch.4 §4.2); cited by → Publication.

#### 5.1.5  Outcome

**Definition.** The recorded result of an Experiment with respect to its Hypothesis — the entity that, when negative or null, is the platform's entire reason for existing.

**Attributes.** `outcome_id`; `result_type` (`Negative` / `Null` / `Inconclusive` / `Positive` — the schema admits `Positive` deliberately, since an Experiment testing multiple Hypotheses may confirm one while disconfirming another, and the platform's scope is the negative/null Outcomes specifically, not a restriction on what an Experiment as a whole may contain); `effect_size` (where applicable); `statistical_significance` (where applicable); `narrative_summary`; `termination_reason` (required if the parent Experiment's status is `Terminated`).

**Relationships.** concludes → Hypothesis; belongs to → Experiment; supports/contradicts → Evidence (Zone A, §5.7); prompts → Replication (0..*).

**Invariants.** An Outcome of type `Negative` or `Null` is the only type eligible for inclusion in the platform's core public registry per its mission (Ch.2 §2.1); `Positive`-typed Outcomes may be recorded for completeness on a multi-hypothesis Experiment but are not the platform's primary curation focus, and this distinction is enforced at the Review Service level (Ch.4 §4.8), not silently dropped.

#### 5.1.6  Intervention (Drug / Device / Biologic / Behavioral / Procedure)

**Definition.** The thing being tested — a superclass with five concrete subtypes, matching the schema already in production (Chapter 3, Appendix A of the platform's funding case).

**Attributes (shared).** `intervention_id`; `type` (enum: Drug/Biologic/Device/Behavioral/Procedure/Molecule/Other); `name`; `description`.
**Attributes (Drug/Biologic subtype).** `dosage`; `route_of_administration`; `mechanism_of_action` (optional, links to Zone E ontology).
**Attributes (Device subtype).** `device_class`; `regulatory_classification`.

**Relationships.** evaluated in → Experiment; belongs to → Intervention Class (Zone E, a controlled grouping such as "SSRIs" or "monoclonal antibodies," enabling the class-level trend queries the platform's Knowledge Graph is designed to support).

---

### 5.2  Zone B — People & Institutions (Fully Specified)

#### 5.2.1  Researcher

**Definition.** An individual scientific contributor — the primary human actor the platform is built to serve, per its mission statement (Ch.2 §2.1).

**Attributes.** `researcher_id`; `orcid` (pattern-validated, per the existing schema field); `display_name`; `affiliation_history` (versioned, since researchers move institutions); `role_on_platform` (`Contributor` / `Curator` / `Curation Lead` / `Administrator`, per Ch.4 §4.6's RBAC model — a Researcher entity and a platform User account are related but distinct: a Researcher may exist in the domain model as an experiment's author without ever holding a platform account).

**Relationships.** conducts → Experiment; curates → Review; authors → Publication; contributes → Submission.

**Invariants.** A Researcher's ORCID, once recorded, is treated as the canonical deduplication key across the platform — two Researcher records sharing an ORCID are always merged, never treated as distinct individuals.

#### 5.2.2  Institution

**Definition.** An organizational entity — a university, hospital, company, or government body — that conducts, hosts, or funds research.

**Attributes.** `institution_id`; `ror_id` (Research Organization Registry identifier, a `FUTURE` external-ontology integration per Ch.4 §4.13); `name`; `institution_type` (controlled vocabulary matching the existing schema field: University Research Lab, Hospital/Clinical Center, Pharmaceutical Company, Independent Researcher, Government Institute, Other); `country`.

**Relationships.** hosts → Experiment; employs → Researcher (time-bounded, via `affiliation_history`); funds → Grant; partners with → Institution Partnership (a governance/administrative entity distinct from a scientific relationship, tracked per the platform's funding case).

#### 5.2.3  Institution Partnership

**Definition.** A formal, non-scientific relationship between the platform and a partner Institution — the domain-model representation of the partnership program described in the platform's implementation roadmap.

**Attributes.** `partnership_id`; `tier` (Associate / Sponsoring / Founding Partner); `status` (Prospective / Negotiating / Signed / Active); `signed_date`.

**Relationships.** involves → Institution; governed by the funder-independence rule (Ch.2 §2.9) — this entity's existence never influences the acceptance or visibility of any Experiment, Outcome, or Publication record, a constraint enforced structurally (no foreign-key relationship exists, or is permitted to exist, between `Institution Partnership` and any curation-decision entity in Zone C).

---

### 5.3  Zone C — Governance & Provenance (Fully Specified)

#### 5.3.1  Submission

**Definition.** The administrative wrapper around a candidate Experiment/Outcome record as it moves through the platform's intake pipeline — distinct from the Experiment itself, because a Submission can be rejected without the underlying scientific Experiment ceasing to have happened.

**Attributes.** `submission_id`; `submitted_by` (Researcher, or null for the no-Git anonymous path); `source_type` (`original_submission` / `public_database_extraction` / `literature_mining`); `submitted_at`; `schema_version`.

**Relationships.** wraps → Experiment (+ its Hypothesis, Outcome, etc.); reviewed via → Review.

*(Full service-level behavior specified in Ch.4 §4.1; this entry captures only its domain-model shape.)*

#### 5.3.2  Review

**Definition.** A recorded curatorial judgment about a Submission's admissibility — the entity that operationalizes Human Accountability (Ch.2 §2.9) in the domain model.

**Attributes.** `review_id`; `reviewed_by` (Researcher, role = Curator or Curation Lead); `decision` (`Approved` / `Rejected` / `Changes Requested`); `checklist_results` (structured, matching the curation checklist: outcome-genuineness confirmed, duplicate check, source verifiability, PII screen, domain classification); `decided_at`.

**Relationships.** evaluates → Submission; performed by → Researcher.

**Invariants.** Every Review has exactly one `reviewed_by` Researcher — anonymous or unattributed review decisions are not a representable state in this domain model, a direct, structural expression of Ch.2 §2.9's Human Accountability principle.

#### 5.3.3  Replication

**Definition.** An independent attempt by a different Experiment to reproduce a prior Experiment's Outcome with respect to the same Hypothesis.

**Attributes.** `replication_id`; `result` (`Confirmed` / `Contradicted` / `Partially Confirmed`); `notes`.

**Relationships.** replicates → Experiment (the original); performed by → Experiment (the replicating study); linked via → Knowledge Graph edge (Ch.4 §4.4, §4.10).

#### 5.3.4  Audit Record

**Definition.** An immutable log entry capturing a single consequential action anywhere in the domain — the domain-model counterpart to the Audit Service (Ch.4 §4.16).

**Attributes.** `audit_id`; `actor` (Researcher or System Account); `action_type`; `target_entity_type`; `target_entity_id`; `timestamp`; `before_state` / `after_state` (where applicable).

**Relationships.** references → any entity in the domain model, generically, as its `target`.

---

### 5.4  Zone D — Publishing & Identity (Fully Specified)

#### 5.4.1  Publication

**Definition.** A citable, external or platform-native document reporting on an Experiment — distinct from a Dataset (the raw data) and an Outcome (the scientific conclusion), because a single Experiment's Outcome may be reported in zero, one, or several Publications (including zero, which is precisely the dark-data condition the platform exists to address).

**Attributes.** `publication_id`; `type` (`Journal Article` / `Preprint` / `Registry Entry` / `Platform-Native Record`); `doi` (optional, external); `title`; `venue`.

**Relationships.** reports on → Experiment; authored by → Researcher; cites → Dataset.

#### 5.4.2  Dataset Release

**Definition.** A frozen, versioned snapshot of the platform's canonical dataset at a point in time — the entity DOIs (below) actually attach to, per Ch.4 §4.9.

**Attributes.** `release_id`; `version` (semantic versioning); `frozen_at`; `entry_count`; `changelog_summary`.

**Relationships.** contains → Experiment (many, as of the release's freeze point); identified by → DOI.

**Invariants.** Immutable once created (Ch.2 §2.9) — a correction to any contained Experiment appears in a subsequent Dataset Release, never as a silent edit to a released one.

#### 5.4.3  DOI (Digital Object Identifier)

**Definition.** The external, permanently resolvable identifier minted for a Dataset Release (and, potentially in future, for individual high-value Experiment records).

**Attributes.** `doi_string`; `registered_at`; `registrar` (DataCite via Zenodo).

**Relationships.** identifies → Dataset Release.

#### 5.4.4  License

**Definition.** The legal terms under which a Dataset, Experiment record, or Publication may be reused.

**Attributes.** `license_id`; `license_type` (`CC0-1.0` / `CC-BY-4.0` / other, matching the existing schema field); `attribution_required` (boolean).

**Relationships.** governs → Dataset, Experiment, Publication.

---

### 5.5  Zone E — Ontology & Classification (Fully Specified)

#### 5.5.1  Disease / Condition

**Definition.** The medical condition or disease state an Experiment's Intervention targets.

**Attributes.** `condition_id`; `preferred_name`; `synonyms` (array); `external_mappings` (MeSH ID, SNOMED CT ID, ICD-11 code — `FUTURE` per Ch.4 §4.13).

**Relationships.** targeted by → Experiment; classified under → Disease Category (a broader grouping, e.g., "Oncology" as a Zone-A `domain` value versus a specific `Disease` like "non-small-cell lung cancer").

#### 5.5.2  Ontology Term

**Definition.** A single controlled-vocabulary entry in any of the platform's classification systems (domain, institution type, intervention type, and — as the ontology matures — disease and drug classifications drawn from external standards).

**Attributes.** `term_id`; `vocabulary` (which controlled list this belongs to); `label`; `version_introduced`; `deprecated_in` (optional); `superseded_by` (optional, self-referential — the domain-model expression of Ch.2 §2.6 principle 6's migration-path requirement).

**Relationships.** classifies → any Zone A/B/D entity requiring controlled classification; maps to → external ontology term (`FUTURE`).

#### 5.5.3  Evidence

**Definition.** A unit of scientific support or contradiction connecting an Outcome to a broader scientific claim — the entity that lets the Knowledge Graph answer "what does the totality of negative evidence say about X" rather than only "show me one negative result about X."

**Attributes.** `evidence_id`; `strength` (qualitative or quantitative, methodology-dependent); `direction` (`Supports` / `Contradicts` / `Mixed`).

**Relationships.** derived from → Outcome; bears on → Hypothesis (potentially a different, related Hypothesis than the one the originating Experiment directly tested — the mechanism by which one negative result informs reasoning about an adjacent, not-yet-tested question).

---

### 5.6  Zone F — Funding & Policy Context (Fully Specified)

#### 5.6.1  Grant

**Definition.** A specific funding award supporting one or more Experiments.

**Attributes.** `grant_id`; `funder_name`; `award_amount`; `award_period`; `grant_reference_number` (external, e.g., an NIH award number).

**Relationships.** funds → Experiment; awarded by → Funder (Institution, `institution_type = Government Institute` or a dedicated foundation type); awarded to → Researcher / Institution.

**Design note.** A Grant funding an Experiment is recorded as domain metadata (conflict-of-interest disclosure, per Ch.2 §2.9) and is explicitly, structurally prevented from having any relationship to the Review or curation-decision entities in Zone C — the same structural firewall described for Institution Partnership (§5.2.3).

#### 5.6.2  Regulatory Context

**Definition.** The applicable regulatory framework(s) an Experiment was conducted under — capturing jurisdiction-specific obligations (FDAAA reporting, EU CTR, NIH DMS Policy) relevant to the platform's compliance-enablement value proposition described in its funding case.

**Attributes.** `context_id`; `jurisdiction`; `applicable_framework` (controlled vocabulary); `compliance_status` (where disclosed).

**Relationships.** applies to → Experiment.

---

### 5.7  Comprehensive Entity Catalog

The entities in §5.1–5.6 are the flagship entities every downstream document depends on. The table below catalogs the full supporting entity set across all six zones — over 100 named entities in total — at the level of detail appropriate for scoping the Database Schema and Ontology chapters. Entities marked `CORE` are fully specified above; all others are scoped here (name, zone, one-line definition, primary relationship) and will receive full specification in the Database Schema chapter as each is implemented, per the `OPERATIONAL`/`PLANNED`/`FUTURE` discipline established in Chapters 3–4.

**Zone A — Scientific Core**

| Entity | Definition | Primary Relationship |
|---|---|---|
| Experiment `CORE` | See §5.1.1 | — |
| Hypothesis `CORE` | See §5.1.2 | tested by Experiment |
| Protocol `CORE` | See §5.1.3 | governs Experiment |
| Protocol Amendment | A versioned change to a Protocol | amends Protocol |
| Dataset `CORE` | See §5.1.4 | produced by Experiment |
| Dataset Schema | The structural definition of a Dataset's fields | describes Dataset |
| Outcome `CORE` | See §5.1.5 | concludes Hypothesis |
| Intervention `CORE` | See §5.1.6 | evaluated in Experiment |
| Intervention Class | A grouping of related Interventions (e.g., a drug class) | groups Intervention |
| Dosage Regimen | A specific dosing schedule tested within an Experiment | belongs to Intervention |
| Statistical Analysis Plan | The pre-specified analysis method for a Protocol | part of Protocol |
| Primary Endpoint | The pre-specified main measured outcome | part of Protocol |
| Secondary Endpoint | A pre-specified additional measured outcome | part of Protocol |
| Adverse Event | A recorded safety observation during an Experiment (non-identifying, aggregate only) | recorded in Experiment |
| Sample Cohort | The (de-identified, aggregate-described) population studied | part of Experiment |
| Control Arm | The comparison group in a controlled Experiment | part of Experiment |
| Experimental Arm | The intervention-receiving group | part of Experiment |
| Termination Reason | A controlled-vocabulary reason an Experiment was stopped early | part of Outcome |
| Methodology Type | Controlled vocabulary of study designs (RCT, cohort, in vitro, in silico, etc.) | classifies Experiment |
| Preregistration Record | A link to an external prospective-registration entry | associated with Experiment |
| Effect Size Measure | The specific statistical measure reported (e.g., hazard ratio, mean difference) | part of Outcome |
| Confidence Interval | The reported uncertainty bound on an Effect Size Measure | part of Outcome |

**Zone B — People & Institutions**

| Entity | Definition | Primary Relationship |
|---|---|---|
| Researcher `CORE` | See §5.2.1 | — |
| Institution `CORE` | See §5.2.2 | — |
| Institution Partnership `CORE` | See §5.2.3 | — |
| Affiliation | A time-bounded link between a Researcher and an Institution | connects Researcher, Institution |
| Contributor Role | The specific role a Researcher played on an Experiment (PI, co-investigator, data curator) | part of Experiment |
| Curator Profile | Domain-specific curation credentials and assignment history for a Researcher acting as Curator | extends Researcher |
| Institution Type | Controlled vocabulary (University, Hospital, Pharma, Government, Independent, Other) | classifies Institution |
| Research Group | A sub-organizational unit within an Institution (a lab or department) | part of Institution |
| Ethics Committee / IRB | The reviewing body that approved an Experiment's human-subjects protocol | approves Experiment |
| Ethics Approval Record | The specific approval decision and reference number | issued by Ethics Committee |
| Contact Record | Optional, curator-visible-only contact information for a Submission | associated with Submission |

**Zone C — Governance & Provenance**

| Entity | Definition | Primary Relationship |
|---|---|---|
| Submission `CORE` | See §5.3.1 | — |
| Review `CORE` | See §5.3.2 | — |
| Replication `CORE` | See §5.3.3 | — |
| Audit Record `CORE` | See §5.3.4 | — |
| Curation Checklist Item | A single checkable criterion within a Review | part of Review |
| Curation Queue Entry | The administrative position of a Submission awaiting Review | wraps Submission |
| Duplicate Flag | A system- or curator-raised signal that two Submissions may describe the same finding | relates Submission, Submission |
| Correction Record | A post-publication amendment to a published Experiment record | supersedes Experiment (version) |
| Governance Decision | A recorded project-level governance action (per Ch.2 §2.6 principle 7) | standalone, referenced by Audit Record |
| Steering Group Member | A Researcher holding a governance role in the multi-maintainer transition | extends Researcher |
| Conflict of Interest Disclosure | A Researcher's or Institution's declared funding/affiliation relevant to a specific Experiment | associated with Experiment |
| Data Use Agreement | A recorded agreement governing how an Institution Partnership shares data | associated with Institution Partnership |

**Zone D — Publishing & Identity**

| Entity | Definition | Primary Relationship |
|---|---|---|
| Publication `CORE` | See §5.4.1 | — |
| Dataset Release `CORE` | See §5.4.2 | — |
| DOI `CORE` | See §5.4.3 | — |
| License `CORE` | See §5.4.4 | — |
| Citation Record | A recorded instance of a Publication or Dataset Release citing, or being cited by, another work | relates Publication, Publication |
| Attribution Statement | The rendered citation text for a specific entry or release | generated from Dataset Release / Experiment |
| Version | A generic versioning entity applied across Experiment, Protocol, Dataset, and Dataset Release | applies to multiple entities |
| Changelog Entry | A human-readable description of what changed in a given Version | part of Version |
| Export Artifact | A generated file representing a filtered or full-dataset extraction | derived from Dataset Release |
| Persistent Identifier | The superclass of DOI and platform-native entry identifiers | identifies multiple entities |

**Zone E — Ontology & Classification**

| Entity | Definition | Primary Relationship |
|---|---|---|
| Disease / Condition `CORE` | See §5.5.1 | — |
| Ontology Term `CORE` | See §5.5.2 | — |
| Evidence `CORE` | See §5.5.3 | — |
| Disease Category | A broad grouping of Diseases (matching the platform's `domain` field: Oncology, Neurology, etc.) | groups Disease |
| External Ontology Mapping | A link from a platform Ontology Term to an external standard (MeSH, SNOMED CT, ICD-11) | maps Ontology Term |
| Synonym | An alternate label for an Ontology Term or Disease | belongs to Ontology Term |
| Controlled Vocabulary | The superclass of any versioned, governed term set (domain, institution type, intervention type, etc.) | contains Ontology Term |
| Knowledge Graph Node | The graph representation of any entity once resolved into the Knowledge Graph Service (Ch.4 §4.4) | represents any Zone A–F entity |
| Knowledge Graph Edge | A typed relationship between two Knowledge Graph Nodes | connects Knowledge Graph Node, Knowledge Graph Node |
| Semantic Embedding | The AI Service's vector representation of an entity (Ch.4 §4.5) | represents Experiment / Outcome |
| Entity Link Suggestion | An AI-proposed, curator-unconfirmed mapping between free text and an Ontology Term | proposes mapping for Submission |

**Zone F — Funding & Policy Context**

| Entity | Definition | Primary Relationship |
|---|---|---|
| Grant `CORE` | See §5.6.1 | — |
| Regulatory Context `CORE` | See §5.6.2 | — |
| Funder | An Institution acting specifically in a funding capacity | awards Grant |
| Funding Mandate | A specific funder policy requirement (e.g., NIH DMS Policy) relevant to Regulatory Context | applies to Grant |
| Compliance Statement | A recorded assertion that a given Experiment/Submission satisfies a Funding Mandate | associated with Experiment |
| Jurisdiction | A controlled vocabulary of applicable national/regional regulatory territories | part of Regulatory Context |
| Reporting Obligation | A specific, dated requirement (e.g., FDAAA's results-reporting deadline) tied to a Regulatory Context | derived from Funding Mandate |

**Cross-Cutting / Platform-Level (spans multiple zones)**

| Entity | Definition | Primary Relationship |
|---|---|---|
| System Account | A non-human actor (e.g., the Import Service) capable of creating Submissions or Audit Records | acts as Submitter/Actor |
| User Account | The Authentication Service's representation of a platform login, distinct from — but linkable to — a Researcher | authenticates as Researcher |
| Role | An RBAC role (Contributor/Curator/Curation Lead/Administrator) | assigned to User Account |
| Permission | A specific grantable action within a Role | composes Role |
| Session | An active authenticated login | belongs to User Account |
| Notification Preference | A User Account's configured delivery settings | belongs to User Account |
| Notification | A single delivered message instance | delivered to User Account |
| Federation Node | An independently operated mirror instance of the platform | synchronizes with Federation Node |
| Sync Record | A single federation synchronization event between two Federation Nodes | relates Federation Node, Federation Node |
| Conflict Resolution | The recorded outcome of a federation data conflict | resolves Sync Record |
| Backup Snapshot | A point-in-time backup artifact (Ch.4 §4.18) | derived from any persisted entity set |
| Restoration Test Record | A recorded, verified test restoration of a Backup Snapshot | validates Backup Snapshot |
| Health Check Result | A single monitoring probe result for a service (Ch.4 §4.17) | monitors Service (Ch.4 entity, not a Zone A–F domain entity) |
| Alert | A triggered monitoring notification | derived from Health Check Result |
| Metric Data Point | A single time-series measurement feeding the Analytics Service | measures any entity or service |
| Report | A generated Analytics Service output (dashboard snapshot or funder report) | aggregates Metric Data Point |
| API Client | A registered external consumer of the platform's API (Ch.3 §2.3.3) | consumes API |
| Webhook Subscription | A partner-configured outbound notification target | subscribes to Event |
| Rate Limit Policy | A configured throttling rule applied to a User Account, System Account, or API Client | applies to Submission, API Client |
| Schema Version | A specific, immutable version of the JSON Schema governing Submission structure | governs Submission |
| Migration Record | The documented mapping between two Schema Versions | relates Schema Version, Schema Version |

---

### 5.8  Entity Relationship Summary Diagram

A condensed view of how the flagship (`CORE`) entities from each zone connect to one another — the skeleton the full catalog in §5.7 hangs off of.

```
Researcher --conducts--> Experiment --tests--> Hypothesis --confirmed/disconfirmed by--> Outcome
    |                        |                                                              |
    |                        +--follows--> Protocol                                          |
    |                        +--produces--> Dataset                                          |
    |                        +--evaluates--> Intervention                                     |
    |                        +--targets--> Disease/Condition                                  |
    |                        +--funded by--> Grant --awarded by--> Institution (as Funder)     |
    |                        +--conducted at--> Institution                                    |
    |                        +--replicated by--> Replication                                   |
    v                        +--reviewed via--> Review --performed by--> Researcher (Curator)   |
Publication --reports on-----+                                                                 |
    |                        +--wrapped as--> Submission --contains--> (Experiment/Hypothesis/  |
    v                                          Outcome as submitted)                            v
Dataset Release --identified by--> DOI                                                    Evidence --bears on--> Hypothesis
    |
    v
License
```

---

### 5.9  Design Principles Governing This Domain Model

Consistent with Ch.2 §2.11's decision principles, the following rules were applied uniformly while constructing the catalog above and should be applied to any future addition:

1. **Separate the scientific fact from its administrative wrapper.** An Experiment happened whether or not its Submission is ever approved; a Submission's rejection does not retroactively un-happen the underlying science. This separation (§5.1.1 vs. §5.3.1) is why the model can represent "a real negative result that the platform declined to publish for provenance reasons" without contradiction.
2. **Separate the Outcome from the Evidence it contributes.** An Outcome is a fact about one Experiment; Evidence is that fact's contribution to a broader claim, potentially about a Hypothesis the original Experiment never directly tested. This separation is what makes cross-experiment reasoning (the Knowledge Graph's core value proposition, Ch.4 §4.4) representable at all.
3. **Structurally firewall funding and partnership entities from curation-decision entities.** Grant (§5.6.1) and Institution Partnership (§5.2.3) are connected to Experiment for legitimate conflict-of-interest transparency, and are explicitly never connected to Review or any curation-decision entity — the domain-model enforcement of the funder-independence rule central to the project's governance charter.
4. **Every governance-relevant action is a first-class entity, not a log line.** Review, Audit Record, and Governance Decision are modeled as full entities with their own relationships, not as free-text notes on some other entity — because Ch.2 §2.7's Auditability attribute requires them to be independently queryable.
5. **Versioning is a first-class relationship pattern, applied consistently.** Protocol Amendment, Dataset Release, Schema Version, and Correction Record all follow the same self-referential "supersedes/amends" pattern rather than each zone inventing its own versioning convention — directly serving Ch.2 §2.6 principle 3 (nothing is silently overwritten).

---

### 5.10  Summary and Handoff to the Database Schema Chapter

This chapter has specified twenty-one flagship entities in full and cataloged over one hundred supporting entities across six zones, without reference to any specific storage technology, table structure, or service boundary — by design, per Ch.2 §2.8's Technology Independence principle. The Database Schema chapter's task is the inverse of this one: taking every entity defined here and assigning it a concrete storage representation (which Ch.3 §3.8 storage technology, which service from Ch.4 owns it, what its exact field-level types and constraints are), while the Ontology chapter's task is to formalize Zone E specifically into the versioned, governed vocabulary system this chapter has only scoped. Neither downstream chapter is permitted to introduce an entity that does not trace back to this one — and any entity here that a downstream chapter finds it cannot cleanly represent is a signal to revise this chapter, not to route around it silently.
