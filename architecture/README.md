# Architecture Documentation

This folder contains every architecture and technical-specification document
produced for the Open Negative Results Registry ("Dark Data Medicine").

Two independent documentation efforts live here side by side — both kept in
full, unedited, because they were produced separately and neither should be
treated as replacing the other until a maintainer explicitly consolidates
them (see the note at the bottom of this page).

## The 16-Chapter Platform Architecture Series

The primary, actively-maintained architecture reference. Read in order for a
full system walkthrough, or jump to the chapter you need.

1. [Executive Summary](Chapter_1_Executive_Summary.md)
2. [Architectural Vision](Chapter_2_Architectural_Vision.md)
3. [High-Level System Architecture](Chapter_3_High_Level_System_Architecture.md)
4. [Component Architecture](Chapter_4_Component_Architecture.md)
5. [Domain Model](Chapter_5_Domain_Model.md)
6. [Ontology Specification](Chapter_6_Ontology_Specification.md)
7. [API Specification](Chapter_7_API_Specification.md)
8. [Security Architecture](Chapter_8_Security_Architecture.md)
9. [Deployment Architecture](Chapter_9_Deployment_Architecture.md)
10. [Developer Guide](Chapter_10_Developer_Guide.md)
11. [Operations Manual](Chapter_11_Operations_Manual.md)
12. [AI Services Architecture](Chapter_12_AI_Services_Architecture.md)
13. [Deployment Implementation Reference](Chapter_13_Deployment_Implementation_Reference.md)
14. [Security Implementation Reference](Chapter_14_Security_Implementation_Reference.md)
15. [Testing Architecture](Chapter_15_Testing_Architecture.md)
16. [Performance Architecture](Chapter_16_Performance_Architecture.md)

## Full-Length Reference Documents

Comprehensive, single-file documents produced independently of the chapter
series above. Each stands on its own.

- [`DarkData-Medicine_WhitePaper.md`](DarkData-Medicine_WhitePaper.md) — the
  full academic case for the project: the publication-bias problem, prior
  art, and the empirical argument for this registry.
- [`Dark_Data_Medicine_System_Architecture.md`](Dark_Data_Medicine_System_Architecture.md) —
  a complete, single-document system architecture reference covering the
  domain model, database schema, ontology, API contract, frontend design
  system, backend services, AI/RAG services, testing, deployment, security,
  and performance in one continuous read.
- [`Technical_Architecture.md`](Technical_Architecture.md) — a FAIR-compliant
  infrastructure specification for the registry (renamed from `Technical
  Architecture.md` to remove a space in the filename; content unchanged).

## A Note on Overlap

These two documentation efforts (the chapter series and the two full-length
references) were produced independently and cover substantially overlapping
ground from different angles. Nothing has been merged, cut, or rewritten —
every document is reproduced here exactly as it was written. If you are
new to the project, the chapter series is the recommended entry point;
the full-length documents are best used as deep-dive references on a
specific topic. Reconciling or formally deprecating one in favor of the
other is a maintainer decision, not something this reorganization makes
for you.
