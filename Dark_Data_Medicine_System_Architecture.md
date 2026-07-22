# Dark Data Medicine
### System Architecture Documentation

*Domain Model · Database Schema · Ontology & Knowledge Graph · API Contract · Frontend Design System · Backend Services · AI/RAG Services · Testing · Deployment · Security · Performance & Scalability*

**Prepared for the Open Negative Results Registry Project**
Engineering Architecture Reference — Version 1.0
First Edition · 2026
CIPRIAN STEFAN PLESCA
---

## Abstract

This document specifies the complete system architecture of the Open Negative Results Registry ("Dark Data Medicine") at a level of technical detail sufficient for direct implementation by an engineering team. It covers the domain model and entity-relationship structure; a normalized relational database schema with full DDL; an OWL/RDF ontology and knowledge-graph design enabling cross-entry semantic linkage and alignment with standard biomedical vocabularies; a dual API contract expressed as both an OpenAPI 3.0 REST specification and a GraphQL schema; a complete frontend design system with design tokens and component specifications; a decomposed backend service architecture; a Retrieval-Augmented Generation (RAG) subsystem for semantic search, duplicate detection, and curator-assistance tooling, explicitly constrained by a human-in-the-loop governance requirement; a multi-layered testing strategy; a deployment and infrastructure-as-code plan; a structured security threat model and audit; and a performance and scalability plan covering the system's growth from an initial hundreds-of-entries deployment to a production system serving millions of structured biomedical records. Every schema, contract, and configuration listing in this document is a working technical artifact, not illustrative pseudocode, and is intended to be used directly as the starting point for implementation.

---

## Table of Contents

- [Introduction & Architectural Overview](#introduction-architectural-overview)
  - [1.1 Purpose and Audience](#11-purpose-and-audience)
  - [1.2 Architectural Principles](#12-architectural-principles)
  - [1.3 C4 Model Overview](#13-c4-model-overview)
    - [1.3.1 System Context](#131-system-context)
    - [1.3.2 Containers](#132-containers)
  - [1.4 Technology Stack Summary](#14-technology-stack-summary)
  - [1.5 Document Map](#15-document-map)
- [Domain Model](#domain-model)
  - [2.1 Bounded Contexts](#21-bounded-contexts)
  - [2.2 Core Entities](#22-core-entities)
    - [2.2.1 Entry (Aggregate Root of the Registry Catalog context)](#221-entry-aggregate-root-of-the-registry-catalog-context)
    - [2.2.2 Intervention (Value Object, owned by Entry)](#222-intervention-value-object-owned-by-entry)
    - [2.2.3 Researcher (Entity, Identity & Attribution context)](#223-researcher-entity-identity-attribution-context)
    - [2.2.4 Curator (Entity, Identity & Attribution context)](#224-curator-entity-identity-attribution-context)
    - [2.2.5 Submission (Aggregate Root of the Submission Intake context)](#225-submission-aggregate-root-of-the-submission-intake-context)
    - [2.2.6 ReviewChecklistItem and CuratorDecision (Curation & Review context)](#226-reviewchecklistitem-and-curatordecision-curation-review-context)
    - [2.2.7 DuplicateCandidate (Curation & Review context)](#227-duplicatecandidate-curation-review-context)
    - [2.2.8 DatasetRelease and DOIRecord (Publication & Release context)](#228-datasetrelease-and-doirecord-publication-release-context)
    - [2.2.9 Domain, License, SourceType, InstitutionType (Controlled Vocabularies)](#229-domain-license-sourcetype-institutiontype-controlled-vocabularies)
  - [2.3 Entity Relationship Overview](#23-entity-relationship-overview)
  - [2.4 Aggregate Roots and Invariants](#24-aggregate-roots-and-invariants)
  - [2.5 Domain Events](#25-domain-events)
- [Database Schema](#database-schema)
  - [3.1 Design Rationale](#31-design-rationale)
  - [3.2 Full Schema DDL](#32-full-schema-ddl)
    - [3.2.1 Reference and Vocabulary Tables](#321-reference-and-vocabulary-tables)
    - [3.2.2 Identity Tables](#322-identity-tables)
    - [3.2.3 Catalog Tables (Published Registry)](#323-catalog-tables-published-registry)
    - [3.2.4 Submission and Curation Tables](#324-submission-and-curation-tables)
    - [3.2.5 Release and Audit Tables](#325-release-and-audit-tables)
  - [3.3 Indexing Strategy](#33-indexing-strategy)
  - [3.4 Constraints and Referential Integrity](#34-constraints-and-referential-integrity)
  - [3.5 Schema Versioning and Migrations](#35-schema-versioning-and-migrations)
  - [3.6 Read Models for Search and Analytics](#36-read-models-for-search-and-analytics)
- [Ontology & Knowledge Graph](#ontology-knowledge-graph)
  - [4.1 Why an Ontology Layer](#41-why-an-ontology-layer)
  - [4.2 Core Ontology Classes (OWL/Turtle)](#42-core-ontology-classes-owlturtle)
  - [4.3 Datatype Properties](#43-datatype-properties)
  - [4.4 Alignment with External Vocabularies](#44-alignment-with-external-vocabularies)
  - [4.5 Knowledge Graph Property-Graph Model](#45-knowledge-graph-property-graph-model)
  - [4.6 Example SPARQL Query](#46-example-sparql-query)
  - [4.7 Example Cypher Query](#47-example-cypher-query)
- [API Contract](#api-contract)
  - [5.1 API Design Principles](#51-api-design-principles)
  - [5.2 REST API — OpenAPI 3.0 Specification](#52-rest-api-openapi-30-specification)
  - [5.3 GraphQL Schema](#53-graphql-schema)
  - [5.4 Authentication and Authorization for APIs](#54-authentication-and-authorization-for-apis)
  - [5.5 Versioning and Deprecation Policy](#55-versioning-and-deprecation-policy)
  - [5.6 Rate Limiting and Pagination Conventions](#56-rate-limiting-and-pagination-conventions)
  - [5.7 Error Model](#57-error-model)
- [Frontend Design System](#frontend-design-system)
  - [6.1 Design Principles](#61-design-principles)
  - [6.2 Design Tokens](#62-design-tokens)
  - [6.3 Typography System](#63-typography-system)
  - [6.4 Component Library Specification](#64-component-library-specification)
    - [6.4.1 EntryCard](#641-entrycard)
    - [6.4.2 SearchBar](#642-searchbar)
    - [6.4.3 DomainFilterChip](#643-domainfilterchip)
    - [6.4.4 DataTable](#644-datatable)
    - [6.4.5 Badge](#645-badge)
    - [6.4.6 Modal / Dialog](#646-modal-dialog)
    - [6.4.7 Toast / Inline Notification](#647-toast-inline-notification)
  - [6.5 Layout and Responsive Grid](#65-layout-and-responsive-grid)
  - [6.6 Accessibility Standards](#66-accessibility-standards)
  - [6.7 State Management Architecture (Frontend)](#67-state-management-architecture-frontend)
- [Backend Services](#backend-services)
  - [7.1 Service Decomposition Overview](#71-service-decomposition-overview)
  - [7.2 Ingestion & Validation Service](#72-ingestion-validation-service)
  - [7.3 Curation & Review Service](#73-curation-review-service)
  - [7.4 Search Indexing Service](#74-search-indexing-service)
  - [7.5 Export Service](#75-export-service)
  - [7.6 Notification Service](#76-notification-service)
  - [7.7 Identity & Access Service](#77-identity-access-service)
  - [7.8 Dataset Release Service](#78-dataset-release-service)
  - [7.9 Inter-Service Communication](#79-inter-service-communication)
  - [7.10 Sequence: Submission-to-Publication Flow](#710-sequence-submission-to-publication-flow)
- [AI/RAG Services](#airag-services)
  - [8.1 Purpose and Governance Constraints](#81-purpose-and-governance-constraints)
  - [8.2 Embedding Pipeline](#82-embedding-pipeline)
  - [8.3 Vector Store Schema](#83-vector-store-schema)
  - [8.4 Retrieval Architecture for Duplicate Detection](#84-retrieval-architecture-for-duplicate-detection)
  - [8.5 Curator-Assist Summarization](#85-curator-assist-summarization)
  - [8.6 Auto-Classification (Domain Suggestion)](#86-auto-classification-domain-suggestion)
  - [8.7 Literature-Mining Extraction Pipeline](#87-literature-mining-extraction-pipeline)
  - [8.8 Prompt Templates and Guardrail Design](#88-prompt-templates-and-guardrail-design)
  - [8.9 Evaluation and Monitoring of AI Components](#89-evaluation-and-monitoring-of-ai-components)
- [Testing Strategy](#testing-strategy)
  - [9.1 Test Pyramid Overview](#91-test-pyramid-overview)
  - [9.2 Unit Testing](#92-unit-testing)
  - [9.3 Contract Testing](#93-contract-testing)
  - [9.4 Integration Testing](#94-integration-testing)
  - [9.5 End-to-End Testing](#95-end-to-end-testing)
  - [9.6 Data Quality and Validation Testing](#96-data-quality-and-validation-testing)
  - [9.7 Load and Performance Testing](#97-load-and-performance-testing)
  - [9.8 Security Testing](#98-security-testing)
  - [9.9 Accessibility Testing](#99-accessibility-testing)
  - [9.10 Test Environment Strategy](#910-test-environment-strategy)
- [Deployment Architecture](#deployment-architecture)
  - [10.1 Environments](#101-environments)
  - [10.2 Containerization Strategy](#102-containerization-strategy)
  - [10.3 CI/CD Pipeline](#103-cicd-pipeline)
  - [10.4 Infrastructure as Code](#104-infrastructure-as-code)
  - [10.5 Release Strategy](#105-release-strategy)
  - [10.6 Static Site / GitHub Pages Deployment Path](#106-static-site-github-pages-deployment-path)
  - [10.7 Disaster Recovery and Backup](#107-disaster-recovery-and-backup)
- [Security Audit](#security-audit)
  - [11.1 Threat Model (STRIDE)](#111-threat-model-stride)
  - [11.2 Data Classification](#112-data-classification)
  - [11.3 Authentication and Authorization Model (RBAC)](#113-authentication-and-authorization-model-rbac)
  - [11.4 OWASP Top 10 Mapping](#114-owasp-top-10-mapping)
  - [11.5 Secrets Management](#115-secrets-management)
  - [11.6 Dependency and Supply Chain Security](#116-dependency-and-supply-chain-security)
  - [11.7 Audit Logging](#117-audit-logging)
  - [11.8 Incident Response Plan](#118-incident-response-plan)
- [Performance & Scalability](#performance-scalability)
  - [12.1 Scalability Goals and Non-Functional Requirements](#121-scalability-goals-and-non-functional-requirements)
  - [12.2 Caching Strategy](#122-caching-strategy)
  - [12.3 Database Scaling](#123-database-scaling)
  - [12.4 Search Scaling](#124-search-scaling)
  - [12.5 CDN and Static Asset Delivery](#125-cdn-and-static-asset-delivery)
  - [12.6 Capacity Planning Model](#126-capacity-planning-model)
  - [12.7 Performance Budgets](#127-performance-budgets)
- [Observability & Monitoring](#observability-monitoring)
  - [13.1 Observability Principles](#131-observability-principles)
  - [13.2 Structured Logging](#132-structured-logging)
  - [13.3 Metrics](#133-metrics)
  - [13.4 Distributed Tracing](#134-distributed-tracing)
  - [13.5 Alerting and Service Level Objectives](#135-alerting-and-service-level-objectives)
- [Compliance & Regulatory Mapping](#compliance-regulatory-mapping)
  - [14.1 Scope of This Chapter](#141-scope-of-this-chapter)
  - [14.2 No Protected Health Information by Design](#142-no-protected-health-information-by-design)
  - [14.3 GDPR-Relevant Considerations](#143-gdpr-relevant-considerations)
  - [14.4 Data Residency](#144-data-residency)
  - [14.5 Research Data Sharing Frameworks](#145-research-data-sharing-frameworks)
- [API Client Examples](#api-client-examples)
  - [15.1 Purpose](#151-purpose)
  - [15.2 REST: Searching Entries by Domain and Keyword](#152-rest-searching-entries-by-domain-and-keyword)
  - [15.3 REST: Submitting a New Entry](#153-rest-submitting-a-new-entry)
  - [15.4 GraphQL: Fetching an Entry with Related Entries and Release Provenance](#154-graphql-fetching-an-entry-with-related-entries-and-release-provenance)
  - [15.5 GraphQL: Subscribing to New Publications in a Domain](#155-graphql-subscribing-to-new-publications-in-a-domain)
- [Appendix A: Consolidated API Quick Reference](#appendix-a-consolidated-api-quick-reference)
- [Appendix B: Glossary of Technical Terms](#appendix-b-glossary-of-technical-terms)
- [Appendix C: Key Architecture Decisions Log](#appendix-c-key-architecture-decisions-log)
- [Appendix D: Illustrative Infrastructure Cost Model](#appendix-d-illustrative-infrastructure-cost-model)

---

# Introduction & Architectural Overview

## 1.1 Purpose and Audience

This document is the authoritative engineering architecture reference for the Open Negative Results Registry ("Dark Data Medicine") — the technical companion to the project's companion white paper, which addresses motivation, governance, and policy. Where the white paper argues why the system should exist, this document specifies exactly how it is built: its domain model, data schema, service decomposition, contracts, and operational characteristics, in sufficient detail for an engineering team to implement, review, or extend the system without requiring further design decisions to be made from scratch. The intended audience is backend and frontend engineers, database administrators, security reviewers, and technical leads evaluating or implementing this system.

## 1.2 Architectural Principles

Six principles govern every design decision in this document, and any future architectural change should be evaluated against them explicitly rather than by convenience alone.

- Data trustworthiness over raw throughput — every architectural layer preserves a human curation gate; no component is permitted to auto-publish unreviewed content, including AI-assisted components (Chapter 8).
- Progressive scalability — the architecture must run cheaply at hundreds of entries (a single small Postgres instance and a static site) and scale cleanly to millions of entries (read replicas, a dedicated search cluster, a CDN) without a rewrite, by keeping the domain model and API contract stable across that growth (Chapter 12).
- Source-of-truth clarity — the version-controlled JSON entry files remain canonical; every other representation (relational rows, graph nodes, search index documents, vector embeddings) is a derived, rebuildable projection of that source of truth.
- Open, standards-based contracts — REST via OpenAPI 3.0 and GraphQL via a standard SDL, rather than a bespoke protocol, so any client (the registry's own frontend, a third-party research tool, or a future mobile app) can integrate without special-cased support.
- Explicit, auditable AI boundaries — AI/RAG components (Chapter 8) assist curators and improve discoverability; they never make an unreviewed publication decision, and every AI-assisted suggestion is logged and attributable.
- Security and privacy by construction — no schema field accepts patient-identifiable information (Chapter 11); every service enforces the same role-based access model; every write path is audit-logged.

## 1.3 C4 Model Overview

This document follows the C4 model (Context, Containers, Components, Code) for describing the system at decreasing levels of abstraction. This section states the top two levels narratively; Chapters 2 through 12 provide the component- and code-level detail.

### 1.3.1 System Context

At the context level, the system has four external actor types — Contributors (researchers and clinicians submitting entries, with or without technical familiarity), Curators (reviewers who approve, reject, or request changes to submissions), Consumers (anyone searching, exporting, or querying the dataset, including automated meta-analysis tooling), and External Systems (ClinicalTrials.gov and other public trial registries, ORCID, Zenodo, and standard biomedical vocabularies such as MeSH, SNOMED CT, and ChEBI) — interacting with a single logical system: the Registry.

### 1.3.2 Containers

At the container level, the Registry is composed of: a version-controlled Data Repository (the canonical JSON entries); a Relational Database serving as a queryable projection for the API and analytics; a Search Index (initially embedded, scaling to a dedicated cluster per Chapter 12) serving full-text and faceted queries; a Knowledge Graph store supporting semantic and ontology-aligned queries (Chapter 4); a Vector Store supporting embedding-based similarity search for duplicate detection and semantic recall (Chapter 8); a set of Backend Services (Chapter 7) implementing ingestion, curation, export, notification, identity, and dataset-release workflows; a Public API Gateway exposing both REST (OpenAPI) and GraphQL contracts (Chapter 5); and a Frontend Application (Chapter 6) consumed by both contributors and consumers.

| Container | Responsibility | Primary Technology (recommended) |
| --- | --- | --- |
| Data Repository | Canonical, version-controlled source of truth for every entry | Git (GitHub), JSON Schema Draft 7 |
| Relational Database | Queryable projection; transactional writes for submissions/reviews | PostgreSQL 16 |
| Search Index | Full-text and faceted search over published entries | OpenSearch (Elasticsearch-compatible) |
| Knowledge Graph Store | Ontology-aligned semantic queries and cross-entry linkage | Neo4j or Apache Jena (RDF triple store) |
| Vector Store | Embedding similarity search for duplicate detection and RAG recall | pgvector (Postgres extension) or a dedicated vector DB |
| Backend Services | Ingestion, validation, curation, export, notification, identity, release | Node.js/TypeScript or Python (FastAPI), containerized |
| API Gateway | Unified REST + GraphQL contract, auth, rate limiting | Apollo Router / Kong / managed API Gateway |
| Frontend Application | Search, browse, submit, and curate experiences | React + TypeScript, static-first with progressive enhancement |

## 1.4 Technology Stack Summary

The recommendations in this document favor mature, widely supported, and — where the project's cost constraints from the companion white paper apply — low-operating-cost technologies over novel or exotic alternatives. Every recommendation in this stack is substitutable; the architectural contracts (schema, API, service boundaries) are designed to remain stable even if a specific implementation technology is swapped.

| Layer | Recommended Technology | Rationale |
| --- | --- | --- |
| Relational database | PostgreSQL 16 | Mature, free, strong JSON and full-text support, pgvector extension available |
| Search | OpenSearch | Open-source, Elasticsearch-API-compatible, no licensing cost at this scale |
| Graph store | Neo4j Community / Apache Jena | Native property-graph or RDF triple-store options depending on query pattern needs |
| Backend runtime | Node.js 20 (TypeScript) or Python 3.12 (FastAPI) | Strong ecosystem for both REST/GraphQL tooling and data-science/AI integration |
| API contracts | OpenAPI 3.0, GraphQL SDL | Both are open standards with broad client/tooling support |
| Frontend | React 18 + TypeScript, Vite | Matches the existing static search interface described in the companion white paper; incrementally upgradable |
| Containerization | Docker + Kubernetes (or a managed container platform) | Standard portable deployment unit; supports the environment strategy in Chapter 10 |
| CI/CD | GitHub Actions | Already used by the project's existing validation and test workflows; no new tooling to adopt |
| Object storage | S3-compatible storage | Dataset export artifacts, vector index snapshots, backup archives |

## 1.5 Document Map

Chapter 2 defines the domain model shared by every downstream layer. Chapter 3 specifies the relational database schema. Chapter 4 specifies the ontology and knowledge-graph layer. Chapter 5 specifies the public API contract. Chapter 6 specifies the frontend design system. Chapter 7 specifies backend service decomposition. Chapter 8 specifies the AI/RAG subsystem and its governance constraints. Chapter 9 specifies the testing strategy. Chapter 10 specifies deployment architecture. Chapter 11 is a structured security audit. Chapter 12 addresses performance and scalability. Appendices provide a consolidated API reference and a technical glossary.

# Domain Model

## 2.1 Bounded Contexts

Following domain-driven design practice, the system is organized into five bounded contexts, each owning its own model and communicating with the others through well-defined events and API contracts rather than shared mutable state.

| Bounded Context | Owns | Key Entities |
| --- | --- | --- |
| Submission Intake | The lifecycle of a contributor-submitted entry before curation decisions | Submission, Contributor, DraftEntry |
| Curation & Review | The human review workflow and its outcomes | ReviewChecklistItem, CuratorDecision, DuplicateCandidate |
| Registry Catalog | The published, canonical dataset of accepted entries | Entry, Intervention, Domain, Institution, License, SourceType |
| Identity & Attribution | Researcher and curator identity, credit, and roles | Researcher, Curator, ORCIDIdentity, Role |
| Publication & Release | Versioned dataset snapshots and external citation | DatasetRelease, DOIRecord, SchemaVersion |

## 2.2 Core Entities

The following entities constitute the domain model's core vocabulary. Attribute lists here describe conceptual, domain-level attributes; the physical column types and constraints are specified in Chapter 3.

### 2.2.1 Entry (Aggregate Root of the Registry Catalog context)

An Entry is the central entity of the entire system: a single, published, curator-approved negative or null research result. It is immutable once published except through an explicit, audited correction workflow (Section 2.5). Attributes: experimentId (stable public identifier), domain (controlled vocabulary reference), targetDisease, hypothesis, outcome, methodologySummary, dateConcluded, sourceType, sourceUrl (optional), license, keywords (list), createdAt, updatedAt, currentSchemaVersion, and a status flag (Published, Corrected, Retracted).

### 2.2.2 Intervention (Value Object, owned by Entry)

Intervention describes what was tested: type (Molecule, Drug, Biologic, Device, Behavioral, Procedure, Other), name, and an optional dosage. It is modeled as a value object rather than an independent entity at the Entry level, but is separately normalized in the relational schema (Chapter 3) to support cross-entry queries such as "every entry testing Compound X."

### 2.2.3 Researcher (Entity, Identity & Attribution context)

A Researcher represents a real-world contributor, optionally linked to a verified ORCID identifier. A Researcher may author zero or more Submissions and, transitively, zero or more published Entries. Attributes: orcid (optional, unique when present), displayName (optional, since anonymous/unattributed contribution is supported), institutionType, and a contributionCount derived attribute.

### 2.2.4 Curator (Entity, Identity & Attribution context)

A Curator is a Researcher who additionally holds review authority over one or more Domains. Attributes: researcherRef, assignedDomains (list), activeSince, and a conflictOfInterestDeclarations list, each entry of which references an Entry or Institution the curator has disclosed a connection to.

### 2.2.5 Submission (Aggregate Root of the Submission Intake context)

A Submission is the mutable, pre-publication representation of a contributor's reported negative result, before it becomes an immutable, published Entry. Attributes: submissionId, submittedVia (NoGitForm, DirectPullRequest, BulkExtraction), rawPayload (the plain-language or JSON payload as originally submitted), proposedEntry (the curator- or automation-mapped structured draft), status (Received, InReview, ChangesRequested, Approved, Rejected, Merged), and a linked ReviewChecklistResult once review begins.

### 2.2.6 ReviewChecklistItem and CuratorDecision (Curation & Review context)

Each Submission under review is evaluated against a fixed set of ReviewChecklistItem instances (schema validation, PII screen, genuine-negative-result confirmation, domain correctness, duplicate screen, source verification, license completeness), each recorded with a pass/fail/needs-clarification result. A CuratorDecision aggregates these results into a final Approve, RequestChanges, or Reject outcome, always attributed to a specific Curator and timestamped for audit purposes.

### 2.2.7 DuplicateCandidate (Curation & Review context)

A DuplicateCandidate links a Submission under review to one or more existing published Entries that a similarity check (schema-field matching in the baseline implementation; embedding-based similarity once the AI/RAG subsystem in Chapter 8 is deployed) has flagged as potentially describing the same underlying study. Attributes: submissionRef, candidateEntryRef, similarityScore, similarityMethod (ExactFieldMatch, EmbeddingCosineSimilarity), and a curatorResolution (ConfirmedDuplicate, ConfirmedDistinct, Unresolved).

### 2.2.8 DatasetRelease and DOIRecord (Publication & Release context)

A DatasetRelease is an immutable, versioned snapshot of every Entry published as of a specific point in time, corresponding to a tagged release of the underlying data repository. Each DatasetRelease is associated with exactly one DOIRecord once archived via the project's Zenodo integration (Chapter 7). Attributes of DatasetRelease: releaseVersion, publishedAt, entryCount, includedSchemaVersion, and a changesSummary. Attributes of DOIRecord: doi, mintedAt, and archiveUrl.

### 2.2.9 Domain, License, SourceType, InstitutionType (Controlled Vocabularies)

These four entities are modeled as versioned, enumerated reference data rather than free text: Domain (Oncology, Neurology, Pharmacology, Cardiology, Psychiatry, Immunology, Infectious Disease, Endocrinology, Other), License (CC0-1.0, CC-BY-4.0), SourceType (OriginalSubmission, PublicDatabaseExtraction, LiteratureMining), and InstitutionType (UniversityResearchLab, HospitalClinicalCenter, PharmaceuticalCompany, IndependentResearcher, GovernmentInstitute, Other). Adding a new value to any of these vocabularies is a versioned schema-governance action (Section 3.5), never a silent data-layer change.

## 2.3 Entity Relationship Overview

The diagram below is expressed in a compact textual notation (entity[attributes] --relationship--> entity) rather than a graphical figure, to keep this reference precise and diff-friendly in version control; a rendered ER diagram should be generated from the DDL in Chapter 3 by the implementing team's schema-visualization tooling of choice.

```
Researcher (1) ---- authors ----> (0..*) Submission
Submission (1) ---- proposes ----> (0..1) Entry            [pre-publication draft]
Submission (1) ---- undergoes ---> (1..*) ReviewChecklistItem
Submission (1) ---- resolved_by -> (0..1) CuratorDecision
Submission (0..*) -- flagged_as -> (0..*) DuplicateCandidate -> (1) Entry [existing]
Curator (1) ------- is_a -------> (1) Researcher
Curator (1) ------- decides ----> (0..*) CuratorDecision
Entry (1) --------- has --------> (1) Intervention           [value object]
Entry (1) --------- classified_by -> (1) Domain
Entry (1) --------- licensed_under -> (1) License
Entry (1) --------- sourced_via --> (1) SourceType
Entry (1) --------- submitted_from -> (1) InstitutionType
Entry (0..*) ------ included_in -> (1..*) DatasetRelease
DatasetRelease (1) - archived_as -> (0..1) DOIRecord
Entry (1) --------- linked_to ----> (0..*) Entry             [KnowledgeGraph: same-intervention, same-target]
```

*Figure 2.1 — Core entity relationships across all five bounded contexts.*

## 2.4 Aggregate Roots and Invariants

Two aggregate roots enforce the system's most important consistency rules. The Submission aggregate enforces that a status transition to Merged can only occur after an associated CuratorDecision with outcome Approve exists, and that a Submission can never directly become a published Entry without passing through this decision — there is no code path, including in the AI/RAG subsystem described in Chapter 8, that permits auto-publication. The Entry aggregate enforces that once status is Published, the core scientific-content fields (hypothesis, outcome, methodologySummary, tested intervention) are immutable except through a Correction workflow that creates a new, linked correction record rather than silently overwriting history.

## 2.5 Domain Events

The system emits the following domain events, which downstream containers (search index, knowledge graph, vector store) subscribe to in order to keep their derived projections synchronized with the canonical data repository, per the source-of-truth principle in Section 1.2.

| Event | Emitted When | Primary Subscribers |
| --- | --- | --- |
| SubmissionReceived | A new Submission is created via any intake path | Curation queue, notification service |
| ChecklistItemEvaluated | A curator or automated check records a checklist result | Curation dashboard, audit log |
| SubmissionApproved | A CuratorDecision with outcome Approve is recorded | Entry publication pipeline |
| EntryPublished | A new Entry is merged into the canonical data repository | Search index, knowledge graph, vector store, notification service |
| EntryCorrected | A published Entry is amended via the correction workflow | Search index, knowledge graph, notification service |
| EntryRetracted | A published Entry is flagged as retracted | Search index (removed from default results), audit log |
| DatasetReleaseCreated | A new versioned snapshot is tagged | Zenodo integration service, citation metadata generator |

# Database Schema

## 3.1 Design Rationale

The companion white paper's architecture chapter specifies a Git-based, JSON-file-per-entry pattern as the canonical source of truth, chosen for its zero-cost hosting, built-in audit trail, and forkability. This chapter specifies a normalized relational schema that serves as a queryable, transactional projection of that same data, generated and kept synchronized via the EntryPublished and related domain events. The relational layer exists to serve the API contract (Chapter 5), support the curation workflow's transactional needs, and support analytical and reporting queries at a scale beyond what an in-process script scanning JSON files can efficiently handle.

## 3.2 Full Schema DDL

The following PostgreSQL Data Definition Language listing is the authoritative relational schema. It is organized into five logical groups mirroring the bounded contexts in Section 2.1: reference/vocabulary tables, identity tables, catalog tables, submission/curation tables, and release/audit tables.

### 3.2.1 Reference and Vocabulary Tables

```sql
-- Controlled vocabularies. Each is a small, versioned lookup table rather
-- than a database-level ENUM type, so that adding a new value is a data
-- migration with full audit history rather than a schema-altering DDL
-- change requiring an exclusive table lock.

CREATE TABLE domain (
    code            TEXT PRIMARY KEY,             -- e.g. 'oncology'
    display_name    TEXT NOT NULL,                 -- e.g. 'Oncology'
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE license (
    code            TEXT PRIMARY KEY,             -- 'CC0-1.0', 'CC-BY-4.0'
    display_name    TEXT NOT NULL,
    requires_attribution BOOLEAN NOT NULL,
    license_url     TEXT NOT NULL
);

CREATE TABLE source_type (
    code            TEXT PRIMARY KEY,             -- 'original_submission', etc.
    display_name    TEXT NOT NULL,
    requires_source_url BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE institution_type (
    code            TEXT PRIMARY KEY,
    display_name    TEXT NOT NULL
);

CREATE TABLE intervention_type (
    code            TEXT PRIMARY KEY,             -- 'Molecule','Drug', etc.
    display_name    TEXT NOT NULL
);
```

### 3.2.2 Identity Tables

```sql
CREATE TABLE researcher (
    researcher_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orcid           TEXT UNIQUE,                   -- nullable: anonymous OK
    display_name    TEXT,
    institution_type_code TEXT REFERENCES institution_type(code),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT orcid_format CHECK (
        orcid IS NULL OR orcid ~ '^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$'
    )
);

CREATE TABLE curator (
    curator_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    researcher_id   UUID NOT NULL REFERENCES researcher(researcher_id),
    active_since    DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE curator_domain_assignment (
    curator_id      UUID NOT NULL REFERENCES curator(curator_id),
    domain_code     TEXT NOT NULL REFERENCES domain(code),
    PRIMARY KEY (curator_id, domain_code)
);

CREATE TABLE curator_conflict_declaration (
    declaration_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curator_id      UUID NOT NULL REFERENCES curator(curator_id),
    entry_id        UUID REFERENCES entry(entry_id),
    institution_note TEXT,
    declared_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.2.3 Catalog Tables (Published Registry)

```sql
CREATE TABLE entry (
    entry_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id       TEXT NOT NULL UNIQUE,     -- public, citable identifier
    domain_code         TEXT NOT NULL REFERENCES domain(code),
    target_disease      TEXT NOT NULL,
    hypothesis          TEXT NOT NULL,
    outcome             TEXT NOT NULL,
    methodology_summary TEXT NOT NULL,
    date_concluded      DATE NOT NULL,
    source_type_code    TEXT NOT NULL REFERENCES source_type(code),
    source_url          TEXT,
    license_code        TEXT NOT NULL REFERENCES license(code),
    institution_type_code TEXT NOT NULL REFERENCES institution_type(code),
    submitting_researcher_id UUID REFERENCES researcher(researcher_id),
    status              TEXT NOT NULL DEFAULT 'published'
                         CHECK (status IN ('published','corrected','retracted')),
    schema_version      TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    search_vector       TSVECTOR                  -- maintained by trigger, Sec 3.3
);

CREATE TABLE intervention (
    intervention_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id            UUID NOT NULL REFERENCES entry(entry_id) ON DELETE CASCADE,
    intervention_type_code TEXT NOT NULL REFERENCES intervention_type(code),
    name                TEXT NOT NULL,
    dosage              TEXT
);

CREATE TABLE keyword (
    keyword_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    value               TEXT NOT NULL UNIQUE
);

CREATE TABLE entry_keyword (
    entry_id            UUID NOT NULL REFERENCES entry(entry_id) ON DELETE CASCADE,
    keyword_id          UUID NOT NULL REFERENCES keyword(keyword_id),
    PRIMARY KEY (entry_id, keyword_id)
);

CREATE TABLE entry_correction (
    correction_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id            UUID NOT NULL REFERENCES entry(entry_id),
    corrected_field     TEXT NOT NULL,
    previous_value      TEXT NOT NULL,
    new_value           TEXT NOT NULL,
    reason              TEXT NOT NULL,
    curator_id          UUID NOT NULL REFERENCES curator(curator_id),
    corrected_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.2.4 Submission and Curation Tables

```sql
CREATE TABLE submission (
    submission_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submitted_via       TEXT NOT NULL
                         CHECK (submitted_via IN
                           ('no_git_form','direct_pull_request','bulk_extraction')),
    raw_payload         JSONB NOT NULL,
    proposed_entry      JSONB,                    -- curator/automation-mapped draft
    status              TEXT NOT NULL DEFAULT 'received'
                         CHECK (status IN
                           ('received','in_review','changes_requested',
                            'approved','rejected','merged')),
    submitting_researcher_id UUID REFERENCES researcher(researcher_id),
    resulting_entry_id  UUID REFERENCES entry(entry_id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_checklist_item (
    checklist_item_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id       UUID NOT NULL REFERENCES submission(submission_id)
                         ON DELETE CASCADE,
    check_name          TEXT NOT NULL,            -- e.g. 'schema_validation'
    result              TEXT NOT NULL
                         CHECK (result IN ('pass','fail','needs_clarification')),
    notes               TEXT,
    evaluated_by        TEXT NOT NULL,             -- 'system' or curator_id
    evaluated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE curator_decision (
    decision_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id       UUID NOT NULL REFERENCES submission(submission_id),
    curator_id          UUID NOT NULL REFERENCES curator(curator_id),
    outcome             TEXT NOT NULL
                         CHECK (outcome IN ('approve','request_changes','reject')),
    rationale           TEXT,
    decided_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE duplicate_candidate (
    duplicate_candidate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id       UUID NOT NULL REFERENCES submission(submission_id),
    candidate_entry_id  UUID NOT NULL REFERENCES entry(entry_id),
    similarity_score    NUMERIC(5,4) NOT NULL,
    similarity_method   TEXT NOT NULL
                         CHECK (similarity_method IN
                           ('exact_field_match','embedding_cosine_similarity')),
    resolution          TEXT NOT NULL DEFAULT 'unresolved'
                         CHECK (resolution IN
                           ('confirmed_duplicate','confirmed_distinct','unresolved'))
);
```

### 3.2.5 Release and Audit Tables

```sql
CREATE TABLE dataset_release (
    release_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_version     TEXT NOT NULL UNIQUE,      -- e.g. 'v0.3.0'
    published_at        TIMESTAMPTZ NOT NULL,
    entry_count         INTEGER NOT NULL,
    included_schema_version TEXT NOT NULL,
    changes_summary      TEXT
);

CREATE TABLE doi_record (
    doi_record_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_id           UUID NOT NULL REFERENCES dataset_release(release_id),
    doi                  TEXT NOT NULL UNIQUE,
    minted_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    archive_url          TEXT NOT NULL
);

CREATE TABLE audit_log (
    audit_id             BIGSERIAL PRIMARY KEY,
    event_type           TEXT NOT NULL,            -- e.g. 'EntryPublished'
    actor_type            TEXT NOT NULL CHECK (actor_type IN ('curator','system','contributor')),
    actor_id              TEXT,
    entity_type           TEXT NOT NULL,            -- e.g. 'entry', 'submission'
    entity_id             UUID NOT NULL,
    payload               JSONB,
    occurred_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 3.3 Indexing Strategy

Beyond the primary-key and foreign-key indexes implied by the DDL above, the schema requires several purpose-built indexes to support the query patterns the API contract (Chapter 5) exposes.

```sql
-- Full-text search over the fields most relevant to a keyword query.
CREATE FUNCTION entry_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.target_disease, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.hypothesis, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.outcome, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.methodology_summary, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_entry_search_vector
  BEFORE INSERT OR UPDATE ON entry
  FOR EACH ROW EXECUTE FUNCTION entry_search_vector_update();

CREATE INDEX idx_entry_search_vector ON entry USING GIN (search_vector);
CREATE INDEX idx_entry_domain        ON entry (domain_code);
CREATE INDEX idx_entry_date_concluded ON entry (date_concluded DESC);
CREATE INDEX idx_intervention_name    ON intervention (lower(name));
CREATE INDEX idx_submission_status    ON submission (status) WHERE status <> 'merged';
CREATE INDEX idx_audit_entity         ON audit_log (entity_type, entity_id);
```

## 3.4 Constraints and Referential Integrity

Every foreign key in the schema above is enforced at the database level rather than only in application code, consistent with the trustworthiness-over-throughput principle in Section 1.2: an application-layer bug should not be able to produce an Entry referencing a nonexistent Domain or License. CHECK constraints enforce the same enumerated-vocabulary and format rules (ORCID format, status-value sets) that the JSON Schema layer in the canonical data repository enforces, providing defense in depth rather than relying on a single validation layer.

## 3.5 Schema Versioning and Migrations

Relational schema changes are managed through a forward-only migration tool (Flyway or an equivalent), with every migration script checked into version control alongside the application code that depends on it. A breaking change to the canonical JSON Schema's field set triggers a corresponding, explicitly authored relational migration in the same release, and the included_schema_version field on dataset_release records exactly which schema version a given snapshot was published under, so that historical API consumers can detect and handle schema drift.

## 3.6 Read Models for Search and Analytics

Rather than serving high-volume search and trend-analysis queries directly against the transactional entry table, the architecture maintains materialized read models — a denormalized entry_search_document view feeding the OpenSearch index described in Chapter 12, and a domain_trend_summary materialized view feeding the trend-analysis endpoints in Chapter 5 — both refreshed asynchronously via the EntryPublished and EntryCorrected domain events rather than on every read, keeping transactional write latency independent of read-side query complexity.

```sql
CREATE MATERIALIZED VIEW domain_trend_summary AS
SELECT
  d.code                         AS domain_code,
  d.display_name                 AS domain_name,
  count(e.entry_id)              AS entry_count,
  count(DISTINCT i.name)         AS distinct_interventions,
  count(DISTINCT e.target_disease) AS distinct_disease_targets,
  max(e.date_concluded)          AS most_recent_conclusion
FROM domain d
LEFT JOIN entry e ON e.domain_code = d.code AND e.status = 'published'
LEFT JOIN intervention i ON i.entry_id = e.entry_id
GROUP BY d.code, d.display_name;

CREATE UNIQUE INDEX ON domain_trend_summary (domain_code);
```

*Listing 3.1 — Materialized trend-summary view refreshed on publication events, used by the analytics endpoints in Chapter 5.*

# Ontology & Knowledge Graph

## 4.1 Why an Ontology Layer

The relational schema in Chapter 3 answers questions phrased in terms of the registry's own vocabulary: which entries belong to a given domain, which interventions share a name. It does not, by itself, answer questions that require external biomedical knowledge — for instance, "show me every negative result for any intervention class related to mTOR inhibition," where "mTOR inhibition" is a pharmacological concept not literally present in any entry's free-text fields. An ontology layer, aligning registry entities with established biomedical vocabularies, closes this gap by letting the system reason over concept hierarchies and synonyms rather than only literal string matches.

## 4.2 Core Ontology Classes (OWL/Turtle)

The registry defines a lightweight OWL ontology, namespaced under a project-controlled URI, that models its own core concepts and provides the anchor points for alignment with external vocabularies in Section 4.4. The listing below is expressed in Turtle syntax.

```turtle
@prefix ddm:  <https://ontology.darkdatamedicine.org/core#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

ddm:NegativeResultEntry   a owl:Class ;
    rdfs:label "Negative Result Entry" ;
    rdfs:comment "A single, curator-approved negative or null research finding." .

ddm:Intervention          a owl:Class ;
    rdfs:label "Tested Intervention" .

ddm:DiseaseTarget         a owl:Class ;
    rdfs:label "Target Disease or Condition" .

ddm:Researcher            a owl:Class ;
    rdfs:label "Researcher" .

ddm:Institution           a owl:Class ;
    rdfs:label "Submitting Institution" .

ddm:MedicalDomain         a owl:Class ;
    rdfs:label "Medical Domain Classification" .

# Object properties
ddm:testsIntervention     a owl:ObjectProperty ;
    rdfs:domain ddm:NegativeResultEntry ;
    rdfs:range  ddm:Intervention .

ddm:targetsDisease        a owl:ObjectProperty ;
    rdfs:domain ddm:NegativeResultEntry ;
    rdfs:range  ddm:DiseaseTarget .

ddm:classifiedAs          a owl:ObjectProperty ;
    rdfs:domain ddm:NegativeResultEntry ;
    rdfs:range  ddm:MedicalDomain .

ddm:contributedBy         a owl:ObjectProperty ;
    rdfs:domain ddm:NegativeResultEntry ;
    rdfs:range  ddm:Researcher .

ddm:relatedEntry          a owl:ObjectProperty , owl:SymmetricProperty ;
    rdfs:domain ddm:NegativeResultEntry ;
    rdfs:range  ddm:NegativeResultEntry ;
    rdfs:comment "Links entries sharing an intervention or disease target, used for knowledge-graph traversal." .
```

*Listing 4.1 — Core OWL class and object-property definitions for the registry ontology.*

## 4.3 Datatype Properties

Datatype properties attach literal values — the same scalar fields present in the relational schema — to ontology individuals, so that a single entry can be represented simultaneously as a relational row, a search-index document, and an RDF individual without duplicated modeling effort.

```
ddm:hasExperimentId   a owl:DatatypeProperty ; rdfs:domain ddm:NegativeResultEntry ; rdfs:range xsd:string .
ddm:hasHypothesis     a owl:DatatypeProperty ; rdfs:domain ddm:NegativeResultEntry ; rdfs:range xsd:string .
ddm:hasOutcome        a owl:DatatypeProperty ; rdfs:domain ddm:NegativeResultEntry ; rdfs:range xsd:string .
ddm:dateConcluded     a owl:DatatypeProperty ; rdfs:domain ddm:NegativeResultEntry ; rdfs:range xsd:date .
```

## 4.4 Alignment with External Vocabularies

The registry's value as a knowledge-graph node increases substantially when its own concepts are linked, via owl:sameAs or skos:closeMatch relations, to established, widely adopted external vocabularies, allowing a query written against a standard vocabulary term to also surface registry entries.

| Registry Concept | External Vocabulary | Alignment Purpose |
| --- | --- | --- |
| DiseaseTarget | MeSH (Medical Subject Headings) | Standard disease/condition terminology used by PubMed and most biomedical literature |
| DiseaseTarget (clinical contexts) | SNOMED CT | Clinical terminology alignment for EHR- and hospital-system interoperability |
| Intervention (molecules/drugs) | ChEBI (Chemical Entities of Biological Interest) | Standard chemical/molecular identifiers enabling structure-aware queries |
| Intervention (approved drugs) | RxNorm | Normalized drug naming for cross-referencing with prescribing and trial data |
| Researcher | ORCID | Persistent researcher identity, already part of the core schema (Chapter 3) |
| DatasetRelease | DOI (via Crossref/DataCite through Zenodo) | Persistent, citable identifier for versioned dataset snapshots |

## 4.5 Knowledge Graph Property-Graph Model

While the OWL/RDF model in Sections 4.2 through 4.4 is the interoperability-oriented representation, day-to-day graph queries — "find entries connected to this one within two hops via a shared intervention" — are typically more ergonomic against a property-graph store. The registry therefore also maintains a property-graph projection, kept synchronized with the canonical data via the same EntryPublished domain event described in Chapter 2.

```
// Node labels
(:Entry {experimentId, domain, targetDisease, hypothesis, outcome, dateConcluded})
(:Intervention {name, type})
(:DiseaseTarget {name, meshId})
(:Researcher {orcid, displayName})

// Relationships
(:Entry)-[:TESTS]->(:Intervention)
(:Entry)-[:TARGETS]->(:DiseaseTarget)
(:Entry)-[:CONTRIBUTED_BY]->(:Researcher)
(:Entry)-[:RELATED_TO {sharedDimension: 'intervention' | 'disease_target'}]->(:Entry)
```

*Listing 4.2 — Neo4j property-graph schema (label and relationship shape).*

## 4.6 Example SPARQL Query

The following SPARQL query, run against the RDF triple store, answers a question the relational schema alone cannot: "which negative-result entries concern any intervention chemically classified under a given ChEBI parent class."

```sql
PREFIX ddm:  <https://ontology.darkdatamedicine.org/core#>
PREFIX chebi: <http://purl.obolibrary.org/obo/chebi#>

SELECT ?entry ?hypothesis ?outcome WHERE {
  ?entry ddm:testsIntervention ?intervention ;
         ddm:hasHypothesis ?hypothesis ;
         ddm:hasOutcome ?outcome .
  ?intervention owl:sameAs ?chebiTerm .
  ?chebiTerm rdfs:subClassOf* chebi:CHEBI_35475 .   # example: mTOR inhibitor class
}
```

## 4.7 Example Cypher Query

The equivalent property-graph query, expressed in Cypher against the Neo4j projection, finds every entry within two relationship hops of a given entry via a shared intervention or disease target — the core traversal supporting the "related negative results" feature on the entry detail page (Chapter 6).

```cypher
MATCH (e:Entry {experimentId: $experimentId})-[:TESTS|TARGETS]->(shared)<-[:TESTS|TARGETS]-(related:Entry)
WHERE related.experimentId <> $experimentId
RETURN DISTINCT related.experimentId, related.targetDisease, related.outcome
LIMIT 10;
```

# API Contract

## 5.1 API Design Principles

The registry exposes two parallel, equally authoritative API contracts — REST via OpenAPI 3.0 and GraphQL via a standard schema definition language — rather than favoring one client style over another, since the consumer base spans simple scripted searches (well served by REST), rich interactive frontends fetching nested, variably shaped data (well served by GraphQL), and third-party meta-analysis tooling that may prefer either. Both contracts are generated from, and must remain consistent with, the single domain model specified in Chapter 2; no field or relationship should exist in one contract without a documented reason it is absent from the other.

## 5.2 REST API — OpenAPI 3.0 Specification

The following is the core OpenAPI 3.0 document for the registry's public REST surface, covering entry retrieval and search, submission intake, and dataset-release metadata. Authentication, curation-only, and administrative endpoints are covered narratively in Sections 5.3 and 5.4 rather than reproduced in full here, to keep this listing focused on the publicly consumed surface.

```yaml
openapi: 3.0.3
info:
  title: Dark Data Medicine Registry API
  version: "1.0.0"
  description: >
    Public API for the Open Negative Results Registry. Read endpoints
    require no authentication. Write endpoints (submission intake) require
    an API key; curation endpoints require curator-role authentication
    (see Section 5.4).
servers:
  - url: https://api.darkdatamedicine.org/v1

paths:
  /entries:
    get:
      summary: List and search published entries
      parameters:
        - name: q
          in: query
          schema: { type: string }
          description: Free-text search across disease, intervention, hypothesis, outcome
        - name: domain
          in: query
          schema: { type: string }
          description: Filter by domain code, e.g. 'oncology'
        - name: institutionType
          in: query
          schema: { type: string }
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: pageSize
          in: query
          schema: { type: integer, default: 25, maximum: 100 }
      responses:
        '200':
          description: A paginated list of entries
          content:
            application/json:
              schema: { $ref: '#/components/schemas/EntryPage' }

  /entries/{experimentId}:
    get:
      summary: Retrieve a single entry by its public experiment ID
      parameters:
        - name: experimentId
          in: path
          required: true
          schema: { type: string }
      responses:
        '200':
          description: The requested entry
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Entry' }
        '404':
          description: No entry with that experiment ID exists

  /entries/{experimentId}/related:
    get:
      summary: Retrieve knowledge-graph-linked related entries
      parameters:
        - name: experimentId
          in: path
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Entries sharing an intervention or disease target
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/EntrySummary' }

  /domains:
    get:
      summary: List all domain vocabulary values and their entry counts
      responses:
        '200':
          description: Domain summary list
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/DomainSummary' }

  /submissions:
    post:
      summary: Submit a new candidate negative-result entry
      security: [ { ApiKeyAuth: [] } ]
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/SubmissionInput' }
      responses:
        '201':
          description: Submission accepted for curator review
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Submission' }
        '422':
          description: Submission failed schema validation

  /submissions/{submissionId}:
    get:
      summary: Check the review status of a prior submission
      security: [ { ApiKeyAuth: [] } ]
      parameters:
        - name: submissionId
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: Current submission status
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Submission' }

  /releases:
    get:
      summary: List versioned, DOI-bearing dataset releases
      responses:
        '200':
          description: List of dataset releases
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/DatasetRelease' }

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  schemas:
    Intervention:
      type: object
      required: [type, name]
      properties:
        type: { type: string, enum: [Molecule, Drug, Biologic, Device, Behavioral, Procedure, Other] }
        name: { type: string }
        dosage: { type: string, nullable: true }

    Entry:
      type: object
      required: [experimentId, domain, targetDisease, hypothesis, outcome,
                 methodologySummary, dateConcluded, sourceType, license, institutionType]
      properties:
        experimentId: { type: string }
        domain: { type: string }
        targetDisease: { type: string }
        testedIntervention: { $ref: '#/components/schemas/Intervention' }
        hypothesis: { type: string }
        outcome: { type: string }
        methodologySummary: { type: string }
        researcherOrcid: { type: string, nullable: true }
        institutionType: { type: string }
        dateConcluded: { type: string, format: date }
        sourceType: { type: string, enum: [original_submission, public_database_extraction, literature_mining] }
        sourceUrl: { type: string, nullable: true }
        license: { type: string, enum: [CC0-1.0, CC-BY-4.0] }
        keywords: { type: array, items: { type: string } }
        status: { type: string, enum: [published, corrected, retracted] }

    EntrySummary:
      type: object
      properties:
        experimentId: { type: string }
        domain: { type: string }
        targetDisease: { type: string }
        outcome: { type: string }

    EntryPage:
      type: object
      properties:
        items: { type: array, items: { $ref: '#/components/schemas/EntrySummary' } }
        page: { type: integer }
        pageSize: { type: integer }
        totalCount: { type: integer }

    DomainSummary:
      type: object
      properties:
        code: { type: string }
        displayName: { type: string }
        entryCount: { type: integer }

    SubmissionInput:
      type: object
      description: Either a fully structured Entry-shaped payload, or a plain-language payload to be curator-mapped.
      properties:
        submittedVia: { type: string, enum: [no_git_form, direct_pull_request, bulk_extraction] }
        payload: { type: object }

    Submission:
      type: object
      properties:
        submissionId: { type: string, format: uuid }
        status: { type: string, enum: [received, in_review, changes_requested, approved, rejected, merged] }
        resultingEntryId: { type: string, nullable: true }

    DatasetRelease:
      type: object
      properties:
        releaseVersion: { type: string }
        publishedAt: { type: string, format: date-time }
        entryCount: { type: integer }
        doi: { type: string, nullable: true }
        archiveUrl: { type: string, nullable: true }
```

*Listing 5.1 — Core OpenAPI 3.0 specification for the public registry REST API.*

## 5.3 GraphQL Schema

The GraphQL schema exposes the same underlying domain model with the nested, client-shaped querying GraphQL is suited for — particularly useful for the frontend's entry-detail view, which needs an entry, its related entries, and its dataset-release provenance in a single round trip.

```graphql
type Intervention {
  type: InterventionType!
  name: String!
  dosage: String
}

enum InterventionType { MOLECULE DRUG BIOLOGIC DEVICE BEHAVIORAL PROCEDURE OTHER }
enum SourceType { ORIGINAL_SUBMISSION PUBLIC_DATABASE_EXTRACTION LITERATURE_MINING }
enum LicenseCode { CC0_1_0 CC_BY_4_0 }
enum EntryStatus { PUBLISHED CORRECTED RETRACTED }

type Entry {
  experimentId: ID!
  domain: Domain!
  targetDisease: String!
  testedIntervention: Intervention!
  hypothesis: String!
  outcome: String!
  methodologySummary: String!
  researcherOrcid: String
  institutionType: String!
  dateConcluded: String!
  sourceType: SourceType!
  sourceUrl: String
  license: LicenseCode!
  keywords: [String!]!
  status: EntryStatus!
  relatedEntries(limit: Int = 10): [Entry!]!
  includedInReleases: [DatasetRelease!]!
}

type Domain {
  code: String!
  displayName: String!
  entryCount: Int!
}

type DatasetRelease {
  releaseVersion: String!
  publishedAt: String!
  entryCount: Int!
  doi: String
  archiveUrl: String
}

type EntryConnection {
  items: [Entry!]!
  totalCount: Int!
  page: Int!
  pageSize: Int!
}

input SubmissionInput {
  submittedVia: String!
  payload: JSON!
}

type Submission {
  submissionId: ID!
  status: String!
  resultingEntry: Entry
}

type Query {
  entries(q: String, domain: String, institutionType: String, page: Int = 1, pageSize: Int = 25): EntryConnection!
  entry(experimentId: ID!): Entry
  domains: [Domain!]!
  releases: [DatasetRelease!]!
  submission(submissionId: ID!): Submission
}

type Mutation {
  createSubmission(input: SubmissionInput!): Submission!
}

type Subscription {
  entryPublished(domain: String): Entry!
}
```

*Listing 5.2 — GraphQL SDL for the registry API, including a subscription for real-time curator dashboards.*

## 5.4 Authentication and Authorization for APIs

Read endpoints (entry search, retrieval, domain listing, release listing) require no authentication, consistent with the free-and-frictionless-access principle in the companion white paper. Submission-creation endpoints require a lightweight API key (rate-limited per key, per Section 5.6) primarily to deter automated abuse rather than to restrict legitimate contribution. Curation-only endpoints — not reproduced in the public contract above — require OAuth 2.0 bearer-token authentication tied to a Curator record (Chapter 2) and are authorized per the role-based access model detailed in Chapter 11.

## 5.5 Versioning and Deprecation Policy

Both API contracts are versioned in the URL path (/v1) rather than via content negotiation, for client simplicity. A breaking change to either contract requires a new major version path, published alongside the prior version for a minimum deprecation window of twelve months, with deprecation notices surfaced via a Sunset HTTP header on the outgoing version's responses. Non-breaking additions (new optional fields, new endpoints) are released within the existing version without a path change.

## 5.6 Rate Limiting and Pagination Conventions

All list endpoints are paginated with a default page size of 25 and a hard maximum of 100 per request, returned alongside a totalCount field so clients can implement their own pagination controls without a separate count query. Unauthenticated read traffic is rate-limited per source IP at a level generous enough not to impede normal search usage but sufficient to prevent bulk-scraping abuse; authenticated submission traffic is rate-limited per API key at a level calibrated to normal individual or small-lab contribution volume, with limit increases available on request for legitimate bulk-extraction integrations (Chapter 10 of the companion white paper).

## 5.7 Error Model

Both contracts share a consistent error-response shape for predictable client-side error handling.

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Field 'domain' must be one of the supported domain codes.",
    "field": "domain",
    "requestId": "a1b2c3d4-..."
  }
}
```

# Frontend Design System

## 6.1 Design Principles

The frontend design system extends the static search interface described in the companion white paper into a full component library, governed by four principles: clinical credibility over decorative flourish, since the primary audience is practicing researchers and clinicians evaluating whether to trust a data source; content density with legibility, since a search results page may show dozens of structured entries at once; accessibility as a baseline requirement rather than a later pass (Section 6.6); and a static-first rendering strategy, so the core search and browse experience remains fast and functional even without JavaScript, with interactivity layered on as progressive enhancement.

## 6.2 Design Tokens

Design tokens are the single source of styling truth, consumed by both the static site and any future React-based component implementation, defined once as CSS custom properties and mirrored as a JSON token file for non-CSS consumers (for instance, a future native mobile client).

```
:root {
  /* Color — clinical archive palette */
  --ddm-color-ink:        #171a17;
  --ddm-color-paper:      #f4efe3;
  --ddm-color-bg:         #12181a;
  --ddm-color-bg-raised:  #1a2226;
  --ddm-color-accent:     #a8452a;   /* rust — negative-result stamp */
  --ddm-color-teal:       #2f6f62;   /* secondary / links */
  --ddm-color-line:       #3a4448;

  /* Typography */
  --ddm-font-serif:  'Source Serif 4', serif;
  --ddm-font-sans:   'Inter', sans-serif;
  --ddm-font-mono:   'JetBrains Mono', monospace;

  --ddm-text-xs:   0.75rem;
  --ddm-text-sm:   0.875rem;
  --ddm-text-base: 1rem;
  --ddm-text-lg:   1.15rem;
  --ddm-text-xl:   1.6rem;
  --ddm-text-2xl:  2.2rem;

  /* Spacing scale (4px base unit) */
  --ddm-space-1: 0.25rem; --ddm-space-2: 0.5rem;  --ddm-space-3: 0.75rem;
  --ddm-space-4: 1rem;    --ddm-space-6: 1.5rem;  --ddm-space-8: 2rem;
  --ddm-space-12: 3rem;   --ddm-space-16: 4rem;

  /* Radius & elevation */
  --ddm-radius-sm: 2px;
  --ddm-radius-md: 6px;
  --ddm-shadow-card: 0 1px 0 rgba(0,0,0,0.4);
}
```

*Listing 6.1 — Core design tokens, consistent with the search interface delivered alongside the companion white paper.*

## 6.3 Typography System

| Role | Font | Size Token | Usage |
| --- | --- | --- | --- |
| Page / section titles | Source Serif 4, 700 | --ddm-text-2xl | H1-level headings |
| Card / entry titles | Source Serif 4, 600 | --ddm-text-xl | Entry disease-target titles |
| Body copy | Inter, 400 | --ddm-text-base | Descriptive prose, form labels |
| Data / identifiers | JetBrains Mono, 400–500 | --ddm-text-sm / --ddm-text-xs | Experiment IDs, ORCID, code, schema fields |
| Eyebrow / metadata labels | JetBrains Mono, 500, uppercase, tracked | --ddm-text-xs | Domain badges, field labels |

## 6.4 Component Library Specification

The following components form the reusable library backing both the search interface and the (planned) submission and curation dashboards. Each is specified with its states and accessibility requirements rather than pixel-level styling, since the visual token values in Section 6.2 already govern appearance.

### 6.4.1 EntryCard

Displays a single registry entry in list/grid context. States: default, hover (subtle elevation), focus-visible (visible keyboard-focus ring meeting WCAG 2.2 contrast requirements). Required content slots: experiment ID (monospace), domain badge, disease-target title, intervention field, outcome field, optional source link. Must be fully operable via keyboard as a single focusable link wrapping the card.

### 6.4.2 SearchBar

A single-line text input bound to the live client-side or API-backed search query. Must expose an accessible label (visually hidden if using placeholder text alone is deemed insufficient per WCAG), debounce input at 200–300ms before triggering a search request in the API-backed (non-static) implementation, and announce result-count changes to assistive technology via an aria-live polite region.

### 6.4.3 DomainFilterChip

A toggleable filter control representing one Domain vocabulary value. States: default, active (selected), disabled (zero matching results for current query). Implemented as a native button element with aria-pressed reflecting active state, never a non-semantic div with a click handler.

### 6.4.4 DataTable

Used in curator-facing views (submission queue, review checklist) rather than the public search page, which uses EntryCard grids instead. Must support column sorting communicated via aria-sort, row selection for bulk curator actions, and a visually and programmatically associated caption describing the table's content.

### 6.4.5 Badge

A small, labeled pill used for domain, license, and status indicators (e.g. "Published", "Corrected"). Color must never be the sole differentiator between statuses; an accompanying text label or icon is required for colorblind-safe and print-safe rendering.

### 6.4.6 Modal / Dialog

Used for curator confirmation actions (e.g. confirming a Reject decision). Must trap focus while open, restore focus to the triggering element on close, be dismissible via the Escape key, and be implemented via the native <dialog> element or an equivalent accessible dialog pattern rather than a custom overlay lacking these behaviors.

### 6.4.7 Toast / Inline Notification

Used for transient confirmation of actions such as a successful submission. Must use an aria-live polite (not assertive, to avoid interrupting a screen-reader user mid-task) region and must not be the sole means of conveying an important state change — critical status changes are always also reflected in persistent page state.

## 6.5 Layout and Responsive Grid

The layout uses a single fluid content column capped at a maximum reading width for prose sections, and a CSS Grid auto-fill pattern (minmax(300px, 1fr)) for entry-card collections, consistent with the reference search interface. Three breakpoints govern layout shifts: a mobile breakpoint below 520px (single-column, reduced header padding), a tablet breakpoint between 520px and 900px (two-column card grid), and a desktop breakpoint above 900px (full auto-fill grid, typically three to four columns depending on viewport width).

## 6.6 Accessibility Standards

The frontend targets WCAG 2.2 Level AA as its minimum conformance bar, given the registry's use by a professional audience that may include users of assistive technology. This includes: a minimum 4.5:1 contrast ratio for body text and 3:1 for large text and UI component boundaries; full keyboard operability for every interactive element, with a visible focus indicator distinct from mouse-hover styling; correct semantic HTML landmarks (header, nav, main, footer) on every page; form labels programmatically associated with their inputs; and respecting the prefers-reduced-motion media query for any transition or animation introduced beyond the current static site's minimal hover transitions.

## 6.7 State Management Architecture (Frontend)

For the current static-site implementation, application state is minimal (search query string, active domain filter) and held in plain JavaScript variables re-rendering a DOM fragment on change, as implemented in the reference site delivered with the companion white paper. Should the frontend evolve into a full React single-page application to support authenticated curator dashboards (Chapter 7), state is recommended to be partitioned into three layers: server-cache state (entries, domains, releases) managed via a data-fetching library with built-in caching and revalidation; ephemeral UI state (modal open/closed, active filter chip) managed via local component state; and cross-cutting session state (authenticated curator identity and role) managed via a single, narrowly scoped context provider rather than a general-purpose global store, to avoid the maintainability cost of an overgrown centralized state tree for what remains, at its core, a read-heavy content browsing application.

# Backend Services

## 7.1 Service Decomposition Overview

The backend is organized as a modular monolith at launch scale, with clear internal module boundaries mirroring the bounded contexts in Chapter 2, and an explicit extraction path to independent deployable services once submission or query volume justifies the added operational complexity. This section describes the eight logical services regardless of whether they are deployed as one process or many; the boundary discipline (each service owns its own data access and communicates with others only via the domain events in Section 2.5 or direct API calls) is what matters, not the deployment topology.

| Service | Owns | Primary Dependencies |
| --- | --- | --- |
| Ingestion & Validation | Accepting submissions from all intake paths; schema validation | Relational DB, JSON Schema validator |
| Curation & Review | Checklist evaluation, curator decisions, duplicate resolution | Relational DB, Vector Store (for AI-assisted duplicate detection) |
| Search Indexing | Keeping the OpenSearch index synchronized with published entries | OpenSearch, Relational DB (event subscriber) |
| Knowledge Graph Sync | Keeping the graph/RDF projections synchronized | Neo4j / RDF store (event subscriber) |
| Export | On-demand Excel/CSV export; scheduled dataset-release snapshotting | Relational DB, Object Storage |
| Notification | Curator and contributor email/webhook notifications | Relational DB (event subscriber), Email provider |
| Identity & Access | Researcher/curator identity, ORCID linkage, role assignment | Relational DB, ORCID OAuth |
| Dataset Release | Zenodo integration, DOI minting, release changelog generation | Object Storage, Zenodo API |

## 7.2 Ingestion & Validation Service

Responsible for accepting a Submission through any of the three intake paths (no-Git form, direct Pull Request, bulk extraction), normalizing it into the canonical Submission shape, and running automated schema validation immediately, synchronously, before persisting the Submission with a Received status. A failed schema validation returns a structured, field-level error response (mirroring the error model in Section 5.7) rather than a generic failure, so a contributor using the API directly receives actionable feedback without waiting for curator involvement.

## 7.3 Curation & Review Service

Owns the ReviewChecklistItem and CuratorDecision entities and orchestrates the review workflow: presenting a curator dashboard view of pending Submissions filtered to their assigned Domains (Chapter 2), running the automated portion of the checklist (schema validation status, duplicate-candidate lookup via the AI/RAG subsystem in Chapter 8), and recording the human curator's decisions. This service is the only component in the entire system authorized to transition a Submission to Approved, and the only trigger for the EntryPublished domain event — an invariant enforced both at the domain-model level (Section 2.4) and at the database level via the CHECK constraints in Chapter 3.

## 7.4 Search Indexing Service

Subscribes to EntryPublished, EntryCorrected, and EntryRetracted events and maintains the OpenSearch index accordingly: indexing a new document on publication, updating the relevant document's fields on correction, and either removing or flagging a document as retracted, per Chapter 12's performance and scalability plan. This service performs no business logic of its own beyond shaping the domain event payload into an OpenSearch-compatible document; the search-relevance and ranking logic itself lives in the OpenSearch index configuration.

## 7.5 Export Service

Provides on-demand Excel and CSV export of search-filtered result sets (extending the existing export_to_excel.py utility described in the companion white paper into an API-triggered service) and runs the scheduled process that produces a full DatasetRelease snapshot on a maintainer-triggered or calendar-scheduled basis, writing the resulting archive to object storage and handing off to the Dataset Release Service (Section 7.8) for DOI minting.

## 7.6 Notification Service

Subscribes to SubmissionReceived, ChecklistItemEvaluated, SubmissionApproved, and related events to send appropriately scoped notifications: a contributor receives a confirmation on submission and a status update on approval or rejection; a curator with a Domain assignment receives a digest of newly received Submissions in their domain rather than a notification per individual event, to avoid notification fatigue at higher submission volumes.

## 7.7 Identity & Access Service

Manages Researcher and Curator records, including optional ORCID OAuth linkage (allowing a contributor to authenticate via their existing ORCID account rather than creating a new, registry-specific credential) and role assignment for curators, including the Domain-scoped authorization enforced throughout the Curation & Review Service and detailed in the security model in Chapter 11.

## 7.8 Dataset Release Service

Handles the integration with Zenodo's GitHub-linked archiving mechanism described in the companion white paper: on a tagged release of the underlying data repository, this service triggers Zenodo's archival process, retrieves the minted DOI once available, and persists it to the DOIRecord entity (Chapter 2), making it immediately available via the /releases API endpoint (Chapter 5).

## 7.9 Inter-Service Communication

Services communicate primarily through the domain events specified in Section 2.5, published to a lightweight message broker (a managed queue service, or, at launch scale, an in-process event emitter within the modular monolith) rather than through direct synchronous calls between services, except where a synchronous response is functionally required — for instance, the Ingestion & Validation Service's immediate schema-validation response to a submitting client. This event-driven pattern is what allows the Search Indexing, Knowledge Graph Sync, and Notification services to be added, removed, or scaled independently without modifying the Curation & Review Service that originates the events they consume.

## 7.10 Sequence: Submission-to-Publication Flow

The following sequence, expressed as an ordered step list rather than a graphical sequence diagram for version-control friendliness, traces a submission from intake through to searchable publication, consolidating the service interactions described above.

1. Contributor submits via the no-Git form; the Ingestion & Validation Service receives the payload and maps it to a Submission record with status Received.
2. Automated schema validation runs synchronously; on failure, a structured error is returned immediately and no further processing occurs.
3. On success, a SubmissionReceived event is published; the Notification Service confirms receipt to the contributor, and the Curation & Review Service adds the Submission to the relevant Domain curator's queue.
4. The AI/RAG subsystem (Chapter 8) runs an asynchronous duplicate-candidate check and populates DuplicateCandidate records before a curator opens the Submission, so the curator sees this information immediately rather than waiting on a synchronous check.
5. A curator reviews the Submission against the checklist (Chapter 8 of the companion white paper), records a CuratorDecision, and — on Approve — triggers the Submission's transition to Approved and then Merged.
6. The Merged transition writes a new Entry row, commits the corresponding JSON file to the canonical data repository, and publishes an EntryPublished event.
7. The Search Indexing Service, Knowledge Graph Sync Service, and Notification Service each independently consume the EntryPublished event and update their respective projections and notifications.
8. The entry becomes visible via both API contracts (Chapter 5) and the public search interface (Chapter 6) typically within seconds of the curator's approval.

# AI/RAG Services

## 8.1 Purpose and Governance Constraints

The registry incorporates Retrieval-Augmented Generation (RAG) and related AI components to reduce curator workload and improve discoverability, in four specific, bounded roles: semantic duplicate detection, curator-facing submission summarization, domain-classification suggestion, and literature-mining candidate extraction. Every one of these roles is advisory. This chapter's single most important architectural constraint, restated from Section 1.2, is that no AI component may transition a Submission to Approved or otherwise cause an Entry to be published; the CuratorDecision entity (Chapter 2) and its associated database CHECK constraint (Chapter 3) make this a structural guarantee rather than a policy convention, and any future AI capability added to this subsystem must preserve that guarantee.

## 8.2 Embedding Pipeline

Every published Entry, and every incoming Submission at intake time, is passed through a text-embedding model to produce a dense vector representation of its concatenated hypothesis, outcome, target disease, and intervention name fields. This embedding is stored in the Vector Store (pgvector or a dedicated vector database) alongside a reference to the source Entry or Submission, and is recomputed whenever those source fields change (including via the Correction workflow in Chapter 2).

```python
# Illustrative embedding pipeline (Python)
def embed_entry_for_similarity(entry: dict) -> list[float]:
    composite_text = " ".join([
        entry["target_disease"],
        entry["tested_intervention"]["name"],
        entry["hypothesis"],
        entry["outcome"],
    ])
    return embedding_model.embed(composite_text)  # returns e.g. a 768-dim vector

def upsert_embedding(entry_id: str, vector: list[float]):
    db.execute(
        "INSERT INTO entry_embedding (entry_id, embedding) VALUES (%s, %s) "
        "ON CONFLICT (entry_id) DO UPDATE SET embedding = EXCLUDED.embedding",
        (entry_id, vector),
    )
```

*Listing 8.1 — Illustrative embedding upsert logic; the embedding model itself is an interchangeable dependency, not an architectural commitment.*

## 8.3 Vector Store Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE entry_embedding (
    entry_id     UUID PRIMARY KEY REFERENCES entry(entry_id) ON DELETE CASCADE,
    embedding    VECTOR(768) NOT NULL,
    model_name   TEXT NOT NULL,
    computed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_entry_embedding_ann
  ON entry_embedding USING hnsw (embedding vector_cosine_ops);

CREATE TABLE submission_embedding (
    submission_id UUID PRIMARY KEY REFERENCES submission(submission_id) ON DELETE CASCADE,
    embedding     VECTOR(768) NOT NULL,
    model_name    TEXT NOT NULL,
    computed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

*Listing 8.2 — pgvector-based schema using HNSW indexing for approximate nearest-neighbor similarity search.*

## 8.4 Retrieval Architecture for Duplicate Detection

When a new Submission is received, its embedding is compared via cosine similarity against every existing published Entry's embedding, and the top-k nearest neighbors above a calibrated similarity threshold are written as DuplicateCandidate records with similarityMethod set to embedding_cosine_similarity, supplementing the exact-field-match check already performed by the Curation & Review Service (Chapter 7). This retrieval step runs asynchronously immediately after intake, so a curator opening a Submission for the first time already sees any likely duplicates flagged, rather than needing to search manually.

```sql
SELECT e.experiment_id, e.target_disease, e.outcome,
       1 - (ee.embedding <=> $1) AS similarity
FROM entry_embedding ee
JOIN entry e ON e.entry_id = ee.entry_id
WHERE e.status = 'published'
ORDER BY ee.embedding <=> $1
LIMIT 5;
```

*Listing 8.3 — Nearest-neighbor duplicate-candidate query ($1 is the new submission’s embedding vector).*

## 8.5 Curator-Assist Summarization

For submissions arriving as long-form, plain-language text (the no-Git form path, Chapter 7 of the companion white paper), a language-model-based summarization step proposes a first-draft mapping of the plain-language answer onto the formal schema fields — for instance, drafting a candidate methodologySummary sentence from a longer free-text description — which the curator reviews, edits, and confirms rather than accepting blindly. This proposed mapping is stored as the Submission's proposedEntry field (Chapter 2) and is never treated as equivalent to a curator-confirmed value until a CuratorDecision explicitly approves it.

## 8.6 Auto-Classification (Domain Suggestion)

A lightweight classification model, trained or prompted against the existing Domain vocabulary, suggests a likely Domain value for a new Submission based on its free-text content, surfaced to the curator as a pre-selected but always-editable field rather than a silently applied classification, since Section 8.1's human-in-the-loop constraint applies to every field, not only the outcome and hypothesis fields most directly tied to scientific claims.

## 8.7 Literature-Mining Extraction Pipeline

Extending the ClinicalTrials.gov seed-extraction tool described in the companion white paper, a RAG-based extraction pipeline can process open-access journal abstracts and PubMed Central records, using retrieval over a curated set of characteristic negative-result phrasings (Chapter 9 of the companion white paper) combined with a language model prompted to extract candidate structured fields from a matching abstract. Every output of this pipeline is written as a Submission with submittedVia set to bulk_extraction and status Received — never directly as a published Entry — entering the identical curator review workflow as any other submission, per the Chapter 8 curation-guide principle in the companion white paper that batch imports receive individual review, not bulk merging.

## 8.8 Prompt Templates and Guardrail Design

Prompts used in the summarization (Section 8.5) and extraction (Section 8.7) pipelines are version-controlled artifacts, not ad hoc strings embedded in application code, and are designed with three guardrails: an explicit instruction that the model must not infer or fabricate a value for any required field it cannot support from the source text, instead leaving it blank for curator completion; a structured output format (JSON matching a subset of the Entry schema) validated against the same JSON Schema used elsewhere in the system before being surfaced to a curator; and an explicit refusal instruction covering any source text that appears to contain patient-identifiable information, flagging the submission for manual handling rather than attempting automated field extraction from it.

```
SYSTEM PROMPT (extraction pipeline, abbreviated):

You are assisting a human curator by proposing a structured draft entry
from a source abstract. You must not infer values you cannot support
directly from the text — leave a field blank rather than guessing.
If the source text contains any patient-identifiable information
(names, dates of birth, medical record numbers), do not attempt
extraction; instead return { "flag_for_manual_review": true,
"reason": "possible PII" }.
Return ONLY a JSON object matching the provided schema. This output
is a DRAFT for human curator review and will not be published
automatically under any circumstance.
```

*Listing 8.4 — Abbreviated system prompt illustrating the guardrail requirements of Section 8.8.*

## 8.9 Evaluation and Monitoring of AI Components

Each AI-assisted component is monitored against curator-facing outcome metrics rather than only model-internal metrics: the duplicate-detection retrieval is evaluated by the rate at which curators confirm versus dismiss a flagged DuplicateCandidate; the summarization and classification assist features are evaluated by curator edit-distance between the proposed and final approved values, since a high edit rate signals the assist feature is not meaningfully reducing curator workload and may need reprompting or retraining. These metrics are reviewed periodically by the project's governance process (Chapter 7 of the companion white paper) rather than treated as a purely engineering concern, since a poorly performing AI assist feature has direct implications for curation quality and therefore for the registry's core trustworthiness value proposition.

# Testing Strategy

## 9.1 Test Pyramid Overview

Testing follows a conventional pyramid shape — a large base of fast unit tests, a smaller layer of integration tests, and a thin top layer of end-to-end tests — with two additions specific to this system's risk profile: a dedicated contract-testing layer (Section 9.3) guarding the API and schema contracts that external consumers depend on, and a dedicated data-quality testing layer (Section 9.6) guarding the scientific-integrity properties that are this project's core value proposition, extending the pytest suite already specified in the companion white paper's reference implementation.

## 9.2 Unit Testing

Every service module (Chapter 7) maintains unit tests for its business logic in isolation, with external dependencies (database, search index, vector store, third-party APIs) replaced by test doubles. Coverage targets are set per-module rather than as a single blanket project-wide number, with the Curation & Review Service and Ingestion & Validation Service — the two services enforcing the system's core trust invariants — held to the highest coverage bar given their outsized importance to data integrity.

## 9.3 Contract Testing

Both the OpenAPI specification (Section 5.2) and the GraphQL schema (Section 5.3) are validated by automated contract tests run on every pull request: the OpenAPI document is linted for internal consistency and checked against a suite of recorded example requests/responses, and the GraphQL schema is checked for backward-incompatible changes (removed fields, changed types) using a schema-diff tool, failing the build if an unversioned breaking change is detected, consistent with the versioning policy in Section 5.5.

```
# Example contract test (pseudocode, run in CI)
openapi-diff baseline/openapi-v1.yaml current/openapi-v1.yaml \
  --fail-on-incompatible-change

graphql-inspector diff baseline/schema.graphql current/schema.graphql \
  --fail-on-breaking
```

## 9.4 Integration Testing

Integration tests exercise real (containerized, ephemeral) instances of PostgreSQL, OpenSearch, and the vector store together, verifying that the domain events described in Section 2.5 correctly propagate across service boundaries — for example, asserting that publishing an EntryPublished event results in a searchable OpenSearch document within an expected time bound, and that a subsequent EntryCorrected event updates that document rather than creating a duplicate.

## 9.5 End-to-End Testing

A small, deliberately limited suite of end-to-end tests drives the actual frontend against a fully deployed staging environment (Chapter 10), covering the small number of critical user journeys whose failure would be most damaging: submitting an entry via the no-Git form through to curator approval and public searchability; searching and filtering the public registry by domain and keyword; and exporting a filtered result set to Excel. End-to-end tests are kept few and high-value rather than attempting to mirror the full unit/integration test surface, consistent with standard test-pyramid guidance on end-to-end test cost and flakiness risk.

## 9.6 Data Quality and Validation Testing

Extending the existing pytest suite from the companion white paper's reference implementation (covering JSON Schema validity and tooling correctness), the production system additionally runs a continuous data-quality test suite directly against the live, published dataset: verifying that every published Entry's relational row is schema-valid, that every Entry has a corresponding, byte-for-byte-consistent JSON file in the canonical data repository (guarding against silent drift between the two representations described in Chapter 3), and that no published Entry's free-text fields match a maintained pattern list associated with likely accidental PII inclusion, flagging any match for immediate curator attention rather than failing silently.

## 9.7 Load and Performance Testing

Load tests, run against a staging environment sized to mirror production, establish baseline latency and throughput figures for the highest-traffic endpoints — entry search and entry retrieval — under simulated concurrent load, and are re-run before any release that changes the search indexing pipeline, the database schema, or the API gateway configuration, with results compared against the performance budgets specified in Chapter 12.

## 9.8 Security Testing

Automated dependency vulnerability scanning runs on every build (Chapter 11); a periodic (at minimum, pre-major-release) authenticated and unauthenticated penetration test covers the OWASP Top 10 risk categories mapped in Chapter 11; and a dedicated test suite specifically verifies the role-based access control model — for instance, asserting that a Curator scoped to the Oncology domain cannot approve a Submission classified under Neurology, and that an unauthenticated request to any curation-only endpoint is rejected.

## 9.9 Accessibility Testing

Automated accessibility linting (axe-core or equivalent) runs against every frontend page in CI, catching the most common WCAG violations (missing form labels, insufficient contrast, missing alt text) before merge; this is supplemented by periodic manual testing with a screen reader against the critical user journeys identified in Section 9.5, since automated tooling alone cannot verify a genuinely usable screen-reader experience.

## 9.10 Test Environment Strategy

Three environments support the testing strategy above: a fully ephemeral, per-pull-request environment for integration and contract tests, torn down after the test run; a persistent staging environment mirroring production configuration for end-to-end and load testing; and production itself, which additionally runs the continuous data-quality suite (Section 9.6) as a scheduled job rather than only at deploy time, since data-quality regressions can in principle be introduced by a curation decision rather than only by a code deployment.

# Deployment Architecture

## 10.1 Environments

| Environment | Purpose | Data |
| --- | --- | --- |
| Development | Local engineer iteration | Synthetic/seed data only |
| Per-PR Ephemeral | Automated CI test runs (Chapter 9) | Freshly seeded, torn down after run |
| Staging | Pre-release validation, load testing, manual QA | Anonymized snapshot of production or synthetic data at production scale |
| Production | Live public registry | Real, curator-approved data |

## 10.2 Containerization Strategy

Every backend service (Chapter 7) is packaged as an independent container image, built via a multi-stage Dockerfile that separates build-time dependencies from the minimal runtime image, and versioned by both a semantic release tag and the source commit SHA for full build traceability. The frontend is built as a static asset bundle (Chapter 6) rather than a server-rendered container in its current static-first form, deployed independently of the backend services via the static-hosting path described in Section 10.6.

## 10.3 CI/CD Pipeline

The pipeline extends the GitHub Actions workflows already specified in the companion white paper's reference implementation (schema validation, test suite) with additional stages for the full production system.

1. Lint and static analysis (code style, type checking).
2. Unit tests (Section 9.2), run in parallel across service modules.
3. Contract tests (Section 9.3) against the OpenAPI and GraphQL schemas.
4. Container image build and vulnerability scan (Chapter 11).
5. Deployment to the per-PR ephemeral environment; integration and a smoke-test subset of end-to-end tests run against it.
6. On merge to main: deployment to staging; full end-to-end and load-test suites run.
7. Manual promotion gate to production, following the release strategy in Section 10.5.

## 10.4 Infrastructure as Code

All infrastructure — container orchestration resources, database instances, search cluster, object storage buckets, networking and DNS — is defined declaratively (Terraform or an equivalent) and version-controlled alongside the application code, so that environment configuration drift is detectable via the same code-review process applied to application changes, and so that the staging environment can be reliably reconstructed to mirror production for the load-testing purposes described in Section 9.7.

```hcl
# Illustrative Terraform excerpt: production Postgres instance
resource "aws_db_instance" "registry_primary" {
  identifier           = "ddm-registry-prod"
  engine               = "postgres"
  engine_version       = "16"
  instance_class       = "db.r6g.large"
  allocated_storage    = 100
  storage_encrypted    = true
  multi_az             = true
  backup_retention_period = 30
  deletion_protection  = true
}

resource "aws_db_instance" "registry_read_replica" {
  identifier             = "ddm-registry-prod-replica"
  replicate_source_db    = aws_db_instance.registry_primary.identifier
  instance_class         = "db.r6g.large"
}
```

*Listing 10.1 — Illustrative infrastructure-as-code excerpt; the specific cloud provider is substitutable per the technology-stack philosophy in Section 1.4.*

## 10.5 Release Strategy

Production releases follow a blue-green deployment pattern for backend services: a new version is deployed alongside the currently live version, smoke-tested against production-equivalent traffic patterns, and cut over via a load-balancer switch rather than an in-place replacement, allowing an immediate rollback by switching traffic back if a post-deployment issue is detected. Database migrations (Section 3.5) are designed to be backward-compatible within a single release cycle — additive changes deployed and verified before any dependent, destructive change (such as dropping a deprecated column) is applied in a subsequent release — so that the blue-green rollback path remains valid even across a schema change.

## 10.6 Static Site / GitHub Pages Deployment Path

Consistent with the companion white paper's low-cost architecture philosophy, the public search interface (Chapter 6) continues to support a fully static deployment path via GitHub Pages, generated by the same deploy-site.yml workflow already specified in the reference implementation, for deployments that do not require the full API-backed backend described in this document — for instance, a fork of the project run by a smaller institution without the operational capacity for the full containerized stack. The full production architecture in this chapter is additive to, not a replacement for, that lightweight deployment option.

## 10.7 Disaster Recovery and Backup

The canonical data repository's own Git history (Chapter 3) is an inherent, cost-free backup of the scientific content itself, mirrored across every contributor's and forker's local clone, per the bus-factor mitigation discussed in the companion white paper. The relational database additionally maintains automated daily snapshots with a minimum 30-day retention, and the vector store and search index — both fully rebuildable from the canonical data and the relational database via the domain-event replay mechanism (Section 2.5) — are not independently backed up, since their recovery path is regeneration rather than restoration. A documented recovery runbook specifies the expected recovery time objective for each container: near-zero for the canonical Git repository (already replicated), low single-digit hours for the relational database (snapshot restore), and a few additional hours for full search-index and knowledge-graph rebuild from the restored relational data.

# Security Audit

## 11.1 Threat Model (STRIDE)

The following STRIDE-structured threat model covers the production system's primary attack surfaces: the public API (Chapter 5), the curator dashboard, and the data pipelines feeding the search, graph, and vector projections.

| STRIDE Category | Representative Threat | Primary Mitigation |
| --- | --- | --- |
| Spoofing | An attacker impersonates a curator to approve a fraudulent entry | OAuth 2.0 bearer auth tied to verified ORCID identity; MFA recommended for curator accounts |
| Tampering | An attacker modifies a published Entry’s outcome field directly in the database | All writes to entry go through the Curation & Review Service; direct DB write access restricted to migration tooling; full audit_log trail (Chapter 3) |
| Repudiation | A curator denies having approved a specific submission | Every CuratorDecision is immutably logged with curator identity and timestamp (Chapter 2, Chapter 3) |
| Information Disclosure | Patient-identifiable information is inadvertently published in a free-text field | No PII-designed schema fields; automated PII-pattern screening (Section 9.6); mandatory curator PII checklist item |
| Denial of Service | Automated scraping or submission flooding degrades service for legitimate users | Per-IP and per-API-key rate limiting (Section 5.6); WAF in front of the API gateway |
| Elevation of Privilege | A contributor-level API key is used to call curator-only endpoints | Role-based access control enforced at the API gateway and re-verified at the service layer (defense in depth) |

## 11.2 Data Classification

Three data classes are defined, each with a distinct handling policy: Public (published Entry content, domain vocabularies, dataset-release metadata — no restriction on access or replication); Restricted (raw Submission payloads prior to publication, curator conflict-of-interest declarations, and API keys — accessible only to the submitting contributor, assigned curators, and system processes); and Prohibited (any patient-identifiable information, which the schema is designed to never accept, per Chapter 12 of the companion white paper, and which triggers mandatory manual escalation, per Section 8.8, if inadvertently detected in submitted free text).

## 11.3 Authentication and Authorization Model (RBAC)

Three roles govern authorization across the system: Contributor (able to create Submissions and view the status of their own prior submissions; no access to other contributors’ unpublished Submissions); Curator (able to review and decide on Submissions within their assigned Domains only, per the curator_domain_assignment table in Chapter 3; read access to all Submissions for cross-domain duplicate checking, but decision authority scoped to assigned domains); and Administrator (able to manage Domain, License, and other controlled-vocabulary values per the schema-governance process in Section 3.5, and to manage Curator role assignments). Role checks are enforced at both the API gateway layer (coarse-grained: does this token have any curator role at all) and the service layer (fine-grained: does this specific curator’s domain assignment cover this specific submission’s domain), providing defense in depth against a gateway misconfiguration alone being sufficient to cause a privilege-escalation vulnerability.

## 11.4 OWASP Top 10 Mapping

| OWASP Category | Applicability | Control |
| --- | --- | --- |
| Broken Access Control | High — curation permissions are the system’s core trust boundary | Domain-scoped RBAC (Section 11.3); automated authorization test suite (Section 9.8) |
| Cryptographic Failures | Medium — API keys and OAuth tokens in transit/at rest | TLS everywhere; API keys hashed at rest; secrets management (Section 11.5) |
| Injection | Medium — free-text fields, search queries | Parameterized queries throughout (no raw SQL string interpolation); OpenSearch query builder, not raw query strings, from user input |
| Insecure Design | Addressed architecturally | Human-in-the-loop publication invariant (Section 2.4, Section 8.1) as a designed-in control, not a bolt-on |
| Security Misconfiguration | Medium — infrastructure sprawl across containers/environments | Infrastructure as code (Section 10.4) with environment-config drift detection |
| Vulnerable and Outdated Components | High — many open-source dependencies (Chapter 1 stack) | Automated dependency scanning on every build (Section 11.6) |
| Identification and Authentication Failures | Medium | ORCID-linked OAuth (Section 7.7); MFA recommended for curator/administrator roles |
| Software and Data Integrity Failures | High — core to data-trust value proposition | Immutable audit log (Chapter 3); Git-based canonical data repository with full history |
| Security Logging and Monitoring Failures | Medium | Centralized audit_log table (Chapter 3) plus infrastructure-level access logging |
| Server-Side Request Forgery | Low — limited outbound-request surface (Zenodo, ORCID, ClinicalTrials.gov integrations) | Allow-listed outbound domains only for integration services (Section 7.8) |

## 11.5 Secrets Management

API keys, OAuth client secrets, database credentials, and third-party integration tokens (Zenodo, ORCID) are stored in a dedicated secrets manager, never in source control or plain environment-variable files committed to a repository, and are injected into containers at runtime rather than baked into container images. Secrets are rotated on a defined schedule and immediately upon any suspected compromise, with rotation itself automated where the underlying provider supports it.

## 11.6 Dependency and Supply Chain Security

Every backend and frontend dependency is scanned for known vulnerabilities on every build via an automated software-composition-analysis tool, with a defined severity threshold blocking merge for high and critical findings. Dependency versions are pinned (via lockfiles) rather than left floating, and a scheduled, separate process proposes dependency updates on a regular cadence so that version drift does not accumulate silently between security-driven update cycles.

## 11.7 Audit Logging

The audit_log table specified in Chapter 3 records every state-changing action across the system — submission creation, checklist evaluation, curator decisions, entry publication, correction, and retraction — with actor identity, timestamp, and a structured payload of the change. This log is append-only at the database permission level (no UPDATE or DELETE grant on the table for any application role) and is the primary evidentiary record for any future dispute about who approved or changed a given Entry and when.

## 11.8 Incident Response Plan

A documented incident response runbook defines severity tiers (from a minor, contained issue to a full data-integrity incident affecting published entries) and corresponding response steps: immediate containment (e.g., revoking a compromised API key or curator credential), impact assessment using the audit log (Section 11.7) to determine the scope of any unauthorized change, remediation (reverting an unauthorized Entry change via the Correction workflow, Chapter 2), and post-incident review feeding back into the governance process described in the companion white paper’s governance chapter, particularly where an incident reveals a gap in the curator conflict-of-interest or role-assignment model.

# Performance & Scalability

## 12.1 Scalability Goals and Non-Functional Requirements

The architecture is designed against three illustrative scale milestones, chosen to bound the design decisions in this chapter rather than as a firm forecast: an initial-launch scale of low thousands of entries and modest search traffic, servable by the single-instance topology described in Section 12.7; a growth scale of roughly one hundred thousand entries and meaningfully higher concurrent search traffic, requiring the read-replica and dedicated-search-cluster additions described in Sections 12.3 and 12.4; and a long-horizon scale of several million entries, requiring the sharding and CDN strategies described in Sections 12.3 and 12.5. The explicit non-functional target carried through all three milestones is that a search query returns results within a sub-second budget (Section 12.7) regardless of dataset size, since search responsiveness is central to the registry’s core "check before you repeat the experiment" use case.

## 12.2 Caching Strategy

Three cache layers reduce load on the primary data stores: an HTTP-level cache (via CDN edge caching, Section 12.5) for fully public, unauthenticated GET responses such as domain listings and individual published entries, which change infrequently relative to read volume; an application-level cache (in-memory or a managed cache service) for the materialized trend-summary view (Chapter 3) and other aggregate statistics, refreshed on the same EntryPublished event cadence as the underlying materialized view; and client-side caching within the frontend’s data-fetching layer (Section 6.7) to avoid redundant re-fetches of already-loaded entries during a single browsing session.

## 12.3 Database Scaling

At launch scale, a single PostgreSQL primary instance is sufficient. At growth scale, read traffic (search-adjacent lookups, entry retrieval) is offloaded to one or more read replicas (Listing 10.1), with all write traffic (submissions, curator decisions, publications) remaining on the primary to preserve the strong consistency the curation workflow requires. At long-horizon scale, the entry and audit_log tables — the two tables expected to grow largest and least boundedly — are candidates for time-based partitioning (by date_concluded and occurred_at respectively), keeping individual partition sizes, and therefore index-maintenance and query-planning costs, bounded as total row count grows.

## 12.4 Search Scaling

OpenSearch is deployed as a single-node cluster at launch scale, growing to a multi-node cluster with index sharding and replica shards for both query throughput and availability at growth scale. Index design follows a denormalized-document pattern — each OpenSearch document embeds its Domain display name, Intervention name, and other frequently filtered fields directly, rather than requiring a join at query time — since OpenSearch, unlike the relational store, is optimized for flat-document retrieval rather than relational joins.

## 12.5 CDN and Static Asset Delivery

The frontend’s static assets (Chapter 6) and any fully public, cacheable API responses are served through a CDN with edge caching, reducing both latency for geographically distributed researchers and load on the origin API gateway. Cache invalidation for a specific Entry’s cached representation is triggered directly by the EntryPublished and EntryCorrected domain events (Section 2.5), rather than relying solely on a time-based expiry, so that a correction becomes visible promptly rather than only after a cache TTL elapses.

## 12.6 Capacity Planning Model

Capacity planning tracks three leading indicators rather than a single aggregate metric: submission intake rate (driving Ingestion & Validation and Curation & Review Service load), search query rate (driving OpenSearch and CDN capacity), and dataset growth rate (driving database storage and the partitioning timeline in Section 12.3). Each indicator is monitored against the performance budgets in Section 12.7, with a documented scale-up trigger — for instance, moving from a single-node to multi-node OpenSearch cluster once sustained query latency approaches the defined budget under current traffic — rather than reactive scaling only after a user-visible degradation occurs.

## 12.7 Performance Budgets

| Operation | Target (p95 latency) | Scaling Lever if Exceeded |
| --- | --- | --- |
| Entry retrieval by experimentId | < 100ms | CDN edge caching (Section 12.5) |
| Search query (keyword + domain filter) | < 400ms | OpenSearch sharding/replica scaling (Section 12.4) |
| Submission intake (schema validation) | < 300ms | Horizontal scaling of the Ingestion & Validation Service |
| Duplicate-candidate retrieval (vector similarity) | < 500ms | HNSW index tuning; dedicated vector-store scaling (Section 8.3) |
| Full dataset export (Excel/CSV) | < 30s for datasets up to 100k entries | Asynchronous job with notification on completion beyond this threshold |
| Search index freshness after publication | < 60s | Search Indexing Service horizontal scaling; event-queue throughput tuning |

# Observability & Monitoring

## 13.1 Observability Principles

The system follows the three-pillars model of observability — structured logs, metrics, and distributed traces — applied consistently across every backend service in Chapter 7, so that a single request (for instance, a Submission moving through validation, duplicate-checking, and curator review) can be followed end to end across service boundaries during incident investigation, rather than requiring an engineer to manually correlate disjoint logs.

## 13.2 Structured Logging

Every service emits structured (JSON) logs rather than free-text log lines, with a consistent minimum field set: timestamp, service name, log level, a correlation/request ID, and — for any log line touching a Submission or Entry — the relevant entity identifier, allowing logs to be filtered and joined across services during investigation. Logs never include full free-text submission content by default, consistent with the data-classification policy in Section 11.2, to avoid inadvertently duplicating potentially sensitive content into a less access-controlled logging system.

```json
{
  "timestamp": "2026-03-14T10:22:01Z",
  "level": "info",
  "service": "curation-review-service",
  "correlationId": "a1b2c3d4-...",
  "event": "CuratorDecisionRecorded",
  "submissionId": "9f8e...",
  "curatorId": "c771...",
  "outcome": "approve"
}
```

*Listing 13.1 — Illustrative structured log entry format.*

## 13.3 Metrics

Each service exposes a standard metrics endpoint (Prometheus-compatible) covering request rate, error rate, and latency distribution per endpoint (the RED method — Rate, Errors, Duration), supplemented by domain-specific business metrics: submissions received per day per domain, mean time from submission to curator decision, duplicate-candidate confirmation rate (feeding the AI evaluation loop in Section 8.9), and search query volume, all dashboarded for both engineering on-call use and governance reporting to the project’s maintainers.

## 13.4 Distributed Tracing

A trace context (a correlation ID, propagated per Listing 13.1) follows a request across every service it touches — from initial submission intake through asynchronous duplicate-candidate computation to eventual curator notification — allowing an engineer to reconstruct the full timeline of a specific Submission’s processing when investigating an anomaly, particularly useful for diagnosing latency in the asynchronous, event-driven flows described in Section 7.9.

## 13.5 Alerting and Service Level Objectives

Alerting thresholds are defined against the performance budgets in Section 12.7 and a small set of availability SLOs — for instance, a target of 99.5% successful response rate for the public entry-retrieval and search endpoints over a rolling 30-day window, reflecting the free, publicly relied-upon nature of the read path described in the companion white paper. Breaches page the on-call engineer only for user-facing degradation (elevated error rate, latency budget breach, search-index staleness beyond the freshness budget); purely internal, self-healing conditions (a single transient job retry) are logged and dashboarded but do not page, to keep on-call alert volume meaningful rather than noisy.

# Compliance & Regulatory Mapping

## 14.1 Scope of This Chapter

This chapter maps the architecture specified in this document against major data-protection and research-data regulatory frameworks, for the benefit of an implementing team’s own compliance review. It is not a legal opinion, and any specific compliance determination should be made with qualified legal counsel reviewing the implementing organization’s actual deployment and jurisdictional obligations.

## 14.2 No Protected Health Information by Design

The domain model (Chapter 2) and its schema (Chapter 3) contain no field designed to accept patient names, dates of birth, medical record numbers, or other direct patient identifiers, and the curator checklist (Chapter 8 of the companion white paper) includes an explicit PII screening step reinforced by the automated pattern-based scan described in Section 9.6 of this document. Because the system is architected to never intentionally hold Protected Health Information (PHI) as defined under frameworks such as HIPAA, it is not designed or positioned as a HIPAA-covered system; an implementing organization that is itself a HIPAA-covered entity should still apply its own independent compliance review before connecting this system to any internal data source that might carry PHI.

## 14.3 GDPR-Relevant Considerations

Where a Researcher record (Chapter 2) includes an ORCID identifier or display name, this constitutes personal data under the EU General Data Protection Regulation for contributors within its scope. The architecture supports GDPR-relevant data-subject rights as follows: the right of access is supported via the existing /submissions/{submissionId} endpoint pattern extended to a researcher’s own full contribution history; the right to erasure is supported for a Researcher’s identity linkage (the orcid and display_name fields) while preserving the scientific content of any already-published Entry as an anonymized contribution, consistent with the legitimate-interest and scientific-archival exemptions many jurisdictions provide for research data, and consistent with the immutability-of-published-scientific-content principle in Section 2.4; and data portability is inherently supported by the existing Excel/CSV export tooling (Section 7.5) and the fully open, machine-readable nature of the canonical JSON data repository itself.

## 14.4 Data Residency

The architecture does not mandate a specific data-residency configuration; the containerized, infrastructure-as-code deployment model (Section 10.4) supports deploying the relational database, search index, and object storage within a specific geographic region or regions as required by an implementing organization’s regulatory obligations, with the canonical Git-based data repository (hosted on GitHub) understood as a separate, globally replicated component whose residency characteristics are governed by the hosting provider’s own terms rather than by this architecture’s infrastructure choices.

## 14.5 Research Data Sharing Frameworks

The licensing model specified in Chapter 3 (CC0-1.0 and CC-BY-4.0 at the individual Entry level) is designed to align with the data-sharing expectations of major research funders — including funder mandates requiring open licensing of publicly funded research outputs — and with the FAIR data principles discussed in the companion white paper’s meta-science chapter, without requiring any funder-specific customization of the core schema itself.

# API Client Examples

## 15.1 Purpose

This chapter provides working request/response examples against both API contracts specified in Chapter 5, intended as copy-adaptable starting points for client implementers rather than an exhaustive client SDK reference.

## 15.2 REST: Searching Entries by Domain and Keyword

```bash
curl -s \
  "https://api.darkdatamedicine.org/v1/entries?domain=oncology&q=MCF-7&pageSize=10" \
  -H "Accept: application/json"

# Example response (truncated)
{
  "items": [
    {
      "experimentId": "ONC_2025_0001",
      "domain": "oncology",
      "targetDisease": "Breast Cancer (MCF-7 cells)",
      "outcome": "No significant difference in cell viability vs control after 48 hours."
    }
  ],
  "page": 1,
  "pageSize": 10,
  "totalCount": 1
}
```

## 15.3 REST: Submitting a New Entry

```bash
curl -s -X POST "https://api.darkdatamedicine.org/v1/submissions" \
  -H "X-API-Key: $DDM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "submittedVia": "direct_pull_request",
    "payload": {
      "domain": "cardiology",
      "targetDisease": "Heart Failure with Preserved Ejection Fraction",
      "testedIntervention": { "type": "Drug", "name": "Compound_D" },
      "hypothesis": "Reduces hospitalization vs standard of care.",
      "outcome": "No significant reduction observed at interim analysis.",
      "methodologySummary": "Multi-center RCT, phase III, interim futility analysis.",
      "institutionType": "HospitalClinicalCenter",
      "dateConcluded": "2025-11-01",
      "sourceType": "original_submission",
      "license": "CC0-1.0"
    }
  }'

# Example response
{ "submissionId": "9f8e7a2c-...", "status": "received", "resultingEntryId": null }
```

## 15.4 GraphQL: Fetching an Entry with Related Entries and Release Provenance

```
query EntryDetail($id: ID!) {
  entry(experimentId: $id) {
    experimentId
    targetDisease
    hypothesis
    outcome
    testedIntervention { type name dosage }
    relatedEntries(limit: 5) {
      experimentId
      targetDisease
      outcome
    }
    includedInReleases {
      releaseVersion
      doi
    }
  }
}

# Variables: { "id": "ONC_2025_0001" }
```

## 15.5 GraphQL: Subscribing to New Publications in a Domain

```
subscription OncologyFeed {
  entryPublished(domain: "oncology") {
    experimentId
    targetDisease
    outcome
  }
}
```

This subscription pattern is the basis for the curator dashboard’s live queue view (Section 6.4.4) and for any future third-party integration wanting real-time notification of new entries within a specific domain, without polling the /entries endpoint on a fixed interval.

# Appendix A: Consolidated API Quick Reference

This appendix summarizes the public REST surface specified in full in Chapter 5, for quick lookup without needing to re-read the complete OpenAPI listing.

| Method & Path | Auth | Purpose |
| --- | --- | --- |
| GET /entries | None | Search/list published entries with query, domain, and pagination parameters |
| GET /entries/{experimentId} | None | Retrieve a single published entry |
| GET /entries/{experimentId}/related | None | Knowledge-graph-linked related entries |
| GET /domains | None | List domain vocabulary values with entry counts |
| POST /submissions | API Key | Submit a new candidate negative-result entry |
| GET /submissions/{submissionId} | API Key | Check review status of a prior submission |
| GET /releases | None | List versioned, DOI-bearing dataset releases |

GraphQL clients should prefer the single /graphql endpoint documented in Section 5.3, using the entries, entry, domains, releases, and submission queries and the createSubmission mutation, with the entryPublished subscription available for real-time curator dashboard use cases (Section 6.4, Section 7.6).

# Appendix B: Glossary of Technical Terms

- Aggregate root — In domain-driven design, the entity through which all changes to a cluster of related objects must be made, enforcing that cluster’s consistency rules (Section 2.4).
- Bounded context — A explicit boundary within which a particular domain model applies, allowing different parts of a system to use the same term with different precise meanings without conflict (Section 2.1).
- C4 model — A hierarchical approach to describing software architecture at four levels of zoom: Context, Containers, Components, and Code (Section 1.3).
- Domain event — A record of something that happened in the domain that other parts of the system may need to react to, published and consumed asynchronously (Section 2.5).
- HNSW (Hierarchical Navigable Small World) — An approximate nearest-neighbor search algorithm used for efficient vector similarity search at scale (Section 8.3).
- OWL (Web Ontology Language) — A W3C standard for authoring ontologies, used here to define the registry’s core concepts and their alignment with external biomedical vocabularies (Chapter 4).
- RAG (Retrieval-Augmented Generation) — An AI architecture pattern combining a retrieval step over a knowledge store with a generative language model, used here for curator-assist features (Chapter 8).
- RBAC (Role-Based Access Control) — An authorization model in which permissions are attached to roles rather than individual users, and users are assigned one or more roles (Section 11.3).
- SPARQL — The standard query language for RDF triple stores, analogous to SQL for relational databases (Section 4.6).
- STRIDE — A threat-modeling mnemonic covering Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege (Section 11.1).
- Value object — In domain-driven design, an object defined entirely by its attribute values rather than a persistent identity, such as the Intervention value object owned by Entry (Section 2.2.2).

# Appendix C: Key Architecture Decisions Log

This appendix consolidates the most consequential architectural decisions made across this document into a single, scannable log, in a lightweight Architecture Decision Record (ADR) style, for future maintainers evaluating whether a given decision remains valid as the system evolves.

| Decision | Chosen Approach | Primary Alternative Rejected | Reference |
| --- | --- | --- | --- |
| Canonical data storage | Git-based JSON files as source of truth; relational DB as derived projection | Relational DB as sole source of truth | Ch. 3.1 |
| Ontology representation | OWL/RDF for standards alignment, plus a synchronized property graph for traversal queries | Property graph only (simpler, but weaker external-vocabulary alignment) | Ch. 4.5 |
| API contract style | Both OpenAPI (REST) and GraphQL, kept in sync from one domain model | GraphQL only | Ch. 5.1 |
| AI publication authority | AI/RAG components are strictly advisory; only a human CuratorDecision can publish | Auto-publication above a high AI confidence threshold | Ch. 8.1, Ch. 2.4 |
| Service topology at launch | Modular monolith with clear internal boundaries, extractable later | Microservices from day one | Ch. 7.1 |
| Search technology | OpenSearch | Proprietary managed search service | Ch. 1.4 |
| Deployment strategy | Blue-green with backward-compatible migrations | Rolling deployment with in-place migration | Ch. 10.5 |
| Duplicate detection | Hybrid: exact-field-match plus embedding-based similarity, both curator-reviewed | Embedding similarity alone (faster, but auto-decision risk) | Ch. 8.4 |

End of document.

# Appendix D: Illustrative Infrastructure Cost Model

This appendix provides an illustrative, order-of-magnitude cost model for operating the production architecture described in this document at each of the three scale milestones defined in Section 12.1. Every figure below is a stylized planning assumption for comparing the relative cost shape across scale tiers, not a vendor quote or a commitment; an implementing team should replace these with actual quotes from its chosen infrastructure provider before budgeting.

| Cost Category | Launch Scale (low thousands of entries) | Growth Scale (~100k entries) | Long-Horizon Scale (millions of entries) |
| --- | --- | --- | --- |
| Relational database | Single small instance | Primary + 1–2 read replicas | Primary + replicas + partitioned tables |
| Search index | Single-node OpenSearch, or embedded/static search (Ch. 6 static path) | Small multi-node cluster | Sharded, multi-node cluster with dedicated replicas |
| Knowledge graph / vector store | Single small instance, or pgvector co-located with primary DB | Dedicated small instance | Dedicated, horizontally scaled instance |
| Backend services (compute) | Single small container host | Small autoscaled container cluster | Larger autoscaled cluster across multiple availability zones |
| CDN / static hosting | Free-tier static hosting (GitHub Pages path, Ch. 10.6) | Standard CDN plan | CDN with elevated bandwidth tier |
| Object storage (exports, backups) | Minimal, near-free at this volume | Small ongoing cost, dominated by dataset export volume | Moderate ongoing cost, mitigated by lifecycle policies on old exports |
| Dominant cost driver | Curator time (per the companion white paper’s sustainability chapter), not infrastructure | Search and database compute | Search and database compute, plus multi-region redundancy if required |

The recurring pattern across all three tiers, consistent with the companion white paper’s sustainability chapter, is that infrastructure cost remains a secondary concern relative to human curator capacity even at the long-horizon scale, since every component in this architecture was deliberately chosen — open-source, horizontally scalable, and substitutable per the technology-stack philosophy in Section 1.4 — to avoid a licensing-cost or vendor-lock-in curve that would otherwise dominate the project’s budget as it grows.

This concludes the System Architecture Documentation. Together with the companion white paper, this document is intended to give an implementing team everything needed to build, review, deploy, and operate the Open Negative Results Registry: the case for why it should exist, and the complete technical specification of how it is built.