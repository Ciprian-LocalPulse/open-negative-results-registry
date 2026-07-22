# Dark Data Medicine — Platform Architecture Series

## Chapter 6: Ontology Specification

*Document status: Normative. Governed by Chapter 2 (Architectural Vision), Chapter 3 (High-Level System Architecture, §3.4.13/§3.6), Chapter 4 (Ontology Service, §4.13), and Chapter 5 (Domain Model, Zone E). Directly consumed by the Database Schema, API Specification, and AI Services Architecture chapters.*

*Version 0.1 — Draft for governance review*

---

### 6.0  Purpose and Scope

Chapter 5 named Zone E — Ontology & Classification — and scoped its entities (Disease/Condition, Ontology Term, Evidence, Disease Category, External Ontology Mapping, Synonym, Controlled Vocabulary, Knowledge Graph Node/Edge) without formalizing how any of them actually behave as a governed vocabulary system. This chapter does that formalization. It answers four questions that Chapter 5 deliberately left open:

1. What **kind** of ontology is this — a lightweight controlled-vocabulary system (SKOS-style) or a fully axiomatized description-logic ontology (OWL-style) — and why?
2. What is the **complete, current, production-grounded list of terms** in every controlled vocabulary the platform already validates against, and what is the **planned expansion path** for each?
3. How does a platform-native term **map onto external, internationally recognized standards** (MeSH, SNOMED CT, RxNorm, ChEBI, ROR, ORCID, and others), and what does the platform do when no clean mapping exists?
4. How does a vocabulary **change over time** without breaking every entry that was classified under an earlier version — the ontology-specific instance of Chapter 2 §2.6's versioning discipline?

A note on honesty, consistent with every prior chapter in this series: the platform's **production** ontology today is five flat, JSON-Schema-enforced enum lists. This chapter specifies the target-state formal ontology those enums are designed to grow into, using the same `OPERATIONAL` / `PLANNED` / `FUTURE` status discipline established in Chapter 3 §3.0. Readers should not infer from this chapter's formal apparatus (SKOS concept schemes, OWL class axioms, competency questions) that the platform currently runs a triple store — it does not. It runs a validated JSON file.

---

### 6.1  Ontology Design Philosophy

**Decision: SKOS-first, with a bounded, targeted use of OWL for specific class hierarchies that benefit from formal reasoning.**

**Rationale.** The Simple Knowledge Organization System (SKOS) is the W3C standard for representing controlled vocabularies, taxonomies, and thesauri — concept schemes with broader/narrower/related relationships and multilingual labels — and is dramatically lower-overhead to implement, govern, and reason about than a full Web Ontology Language (OWL) model with formal class axioms and description-logic consistency checking. Per Chapter 2 §2.11's "standards before invention" and "interoperability over local optimization" principles, the platform adopts SKOS as its primary representation because:

- Every controlled vocabulary the platform needs at launch (domain classification, institution type, intervention type, outcome type) is fundamentally a **classification scheme**, not a set of entities requiring formal logical inference — SKOS is definitionally the right tool for this.
- SKOS interoperates directly with the external standards the platform maps onto (MeSH is published in SKOS/RDF; SNOMED CT and RxNorm both have SKOS-compatible export forms), minimizing translation overhead at the External Ontology Integration layer (§6.4).
- OWL's expressive power — necessary condition axioms, disjointness constraints, automated classification via a reasoner — is reserved for the one place in this platform where it earns its complexity: the **Intervention Class hierarchy** and **Disease Category hierarchy** (§6.6.2), where questions like "is Drug X a member of the SSRI class, and does that make it automatically comparable to other SSRIs in the Knowledge Graph" benefit from real subsumption reasoning that SKOS's simpler broader/narrower relation does not formally guarantee.

**Consequence.** The Ontology Service (Ch.4 §4.13) is designed around a SKOS concept-scheme data model as its default term representation, with an OWL-based reasoning layer introduced specifically and only for the class hierarchies identified in §6.6.2 — not as a platform-wide requirement.

---

### 6.2  Ontology Architecture: Four Layers

```
Layer 4:  External Standard Mappings        [FUTURE, incremental — §6.4]
             MeSH · SNOMED CT · RxNorm · ChEBI · ATC · ICD-11 · GMDN · ROR · ORCID
                              ^
                              | maps to
Layer 3:  Domain-Specific Terminologies      [PLANNED — §6.6]
             Disease Category · Intervention Class · Methodology Type ·
             Adverse Event Terminology
                              ^
                              | specializes
Layer 2:  Core Controlled Vocabularies        [OPERATIONAL — §6.3]
             domain · institution_type · intervention.type ·
             outcome.result_type · source_type · license
                              ^
                              | governed by
Layer 1:  Ontology Governance & Versioning    [PLANNED — §6.5]
             Term lifecycle · deprecation · migration · SKOS concept scheme
             management · change-proposal review process
```

**How to read this stack.** Layer 1 is process, not data — it is the governance discipline every term in every layer above it must pass through to change. Layer 2 is what exists in production today: five flat enums, already enforced by JSON Schema, already doing real classification work. Layer 3 is the planned enrichment of those flat enums into actual hierarchical taxonomies (a `domain` value like "Oncology" becoming a Disease Category with real subcategories, rather than a single flat string). Layer 4 is the platform's connective tissue to the rest of the scientific data ecosystem — the layer that makes the Knowledge Graph Service (Ch.4 §4.4) capable of answering questions that span the platform's own dataset and the broader open scientific graph (PubMed, OpenAlex, ClinicalTrials.gov) simultaneously.

---

### 6.3  Core Controlled Vocabularies (Layer 2 — `OPERATIONAL`)

These five vocabularies are the platform's **actual, production, JSON-Schema-enforced** controlled terms today. Every term below is drawn directly from the live submission schema, not aspirational.

#### 6.3.1  `domain` (Concept Scheme: `ddm:domain`)

| Term | SKOS `prefLabel` | Status |
|---|---|---|
| `Oncology` | Oncology | `OPERATIONAL` |
| `Neurology` | Neurology | `OPERATIONAL` |
| `Pharmacology` | Pharmacology | `OPERATIONAL` |
| `Cardiology` | Cardiology | `OPERATIONAL` |
| `Psychiatry` | Psychiatry | `OPERATIONAL` |
| `Immunology` | Immunology | `OPERATIONAL` |
| `Infectious Disease` | Infectious Disease | `OPERATIONAL` |
| `Endocrinology` | Endocrinology | `OPERATIONAL` |
| `Other` | Other (unclassified) | `OPERATIONAL` |

**Governance note.** This is the platform's top-level Disease Category grouping (Ch.5 §5.5.1's `Disease Category`), currently flat. Layer 3 (§6.6.1) formalizes each of these nine terms as the root of its own sub-hierarchy rather than a terminal leaf.

#### 6.3.2  `institution_type` (Concept Scheme: `ddm:institutionType`)

| Term | SKOS `prefLabel` | Status |
|---|---|---|
| `University Research Lab` | University Research Lab | `OPERATIONAL` |
| `Hospital/Clinical Center` | Hospital / Clinical Center | `OPERATIONAL` |
| `Pharmaceutical Company` | Pharmaceutical Company | `OPERATIONAL` |
| `Independent Researcher` | Independent Researcher | `OPERATIONAL` |
| `Government Institute` | Government Institute | `OPERATIONAL` |
| `Other` | Other | `OPERATIONAL` |

**External mapping target.** Each `institution_type` value is designed to eventually cross-reference the Research Organization Registry (ROR) `types` field, which uses a comparable but not identical classification (`Education`, `Healthcare`, `Company`, `Nonprofit`, `Government`, `Facility`, `Other`) — the mapping is not one-to-one (ROR's `Facility` type, for instance, has no direct platform equivalent) and is scoped as a `FUTURE` cross-vocabulary mapping table (§6.4.6), not a renaming of the platform's own vocabulary to match ROR's.

#### 6.3.3  Intervention `type` (Concept Scheme: `ddm:interventionType`)

| Term | SKOS `prefLabel` | Status |
|---|---|---|
| `Molecule` | Molecule | `OPERATIONAL` |
| `Drug` | Drug | `OPERATIONAL` |
| `Biologic` | Biologic | `OPERATIONAL` |
| `Device` | Device | `OPERATIONAL` |
| `Behavioral` | Behavioral Intervention | `OPERATIONAL` |
| `Procedure` | Procedure | `OPERATIONAL` |
| `Other` | Other | `OPERATIONAL` |

#### 6.3.4  Outcome `result_type` — *(schema field name pending Database Schema chapter; conceptually present today via the `outcome` free-text field's negative/null framing)*

| Term | SKOS `prefLabel` | Status |
|---|---|---|
| `Negative` | Negative Result | `PLANNED` *(currently implicit, not a separate enum field)* |
| `Null` | Null Result | `PLANNED` |
| `Inconclusive` | Inconclusive | `PLANNED` |
| `Positive` | Positive (non-primary-focus) | `PLANNED` |

**Design note.** Formalizing this as an explicit controlled field, rather than leaving outcome-direction implicit in free text, is one of the highest-value near-term Ontology Service enhancements — it is what allows the Search Service (Ch.4 §4.3) to facet by result type directly, rather than relying on the AI Service's `FUTURE` classification capability to infer it.

#### 6.3.5  `license` (Concept Scheme: `ddm:license`)

| Term | SKOS `prefLabel` | Status |
|---|---|---|
| `CC0-1.0` | CC0 1.0 Universal (Public Domain Dedication) | `OPERATIONAL` |
| `CC-BY-4.0` | Creative Commons Attribution 4.0 | `OPERATIONAL` |

#### 6.3.6  `source_type` (Concept Scheme: `ddm:sourceType`)

| Term | SKOS `prefLabel` | Status |
|---|---|---|
| `original_submission` | Original Submission | `OPERATIONAL` |
| `public_database_extraction` | Public Database Extraction | `OPERATIONAL` |
| `literature_mining` | Literature Mining | `OPERATIONAL` |

---

### 6.4  External Ontology Integration Strategy (Layer 4)

Per Chapter 2 §2.3.1 (FAIR First) and §2.11 (standards before invention), every platform-native controlled vocabulary that has a credible external standard equivalent is designed to map onto it — not to be replaced by it, since the platform's own vocabularies are deliberately simpler and better-suited to its specific curation workflow, but to be **cross-referenced** so that platform data interoperates with the broader scientific data ecosystem.

| Platform Concept | Target External Standard(s) | Mapping Relationship | Status |
|---|---|---|---|
| Disease / Condition (Ch.5 §5.5.1) | **MeSH** (Medical Subject Headings), **SNOMED CT**, **ICD-11** | `skos:closeMatch` or `skos:exactMatch` per term | `FUTURE` |
| Drug / Biologic Intervention | **RxNorm** (US drug nomenclature), **ChEBI** (Chemical Entities of Biological Interest), **ATC** (Anatomical Therapeutic Chemical Classification) | `skos:exactMatch` (RxNorm/ChEBI, molecule-level), `skos:broadMatch` (ATC, class-level) | `FUTURE` |
| Device Intervention | **GMDN** (Global Medical Device Nomenclature) | `skos:closeMatch` | `FUTURE` |
| Institution | **ROR** (Research Organization Registry) | `owl:sameAs`-equivalent (ROR IDs are globally unique per organization) | `FUTURE`, prioritized — see §6.4.1 |
| Researcher | **ORCID** | `owl:sameAs`-equivalent (already a validated schema field, Ch.5 §5.2.1) | `OPERATIONAL` (field present) / `PLANNED` (as an active OIDC-verified link, Ch.4 §4.6) |
| Publication | **Crossref DOI**, **PubMed ID**, **OpenAlex ID** | `owl:sameAs`-equivalent | `FUTURE` |
| Methodology Type | A study-design taxonomy aligned with **MSO** (Medical Science Ontology) or equivalent | `skos:closeMatch` | `FUTURE` |
| Adverse Event | **MedDRA** (Medical Dictionary for Regulatory Activities) | `skos:closeMatch` | `FUTURE`, lower priority (Adverse Event is itself a `FUTURE` Ch.5 entity) |

#### 6.4.1  Why ROR and ORCID Are Prioritized Over the Others

Every mapping in the table above extends the platform's discoverability; ROR and ORCID are prioritized specifically because they are **identity** mappings (an Institution or Researcher either is or is not the entity a given ROR/ORCID ID refers to) rather than **classification** mappings (where a Disease term maps onto MeSH with some genuine, harder-to-automate judgment about equivalence). Identity mappings are lower-risk, higher-confidence, and directly unlock deduplication — a critical data-quality capability for the Institution and Researcher entities specifically, since name-based matching alone (`"Johns Hopkins"` vs. `"Johns Hopkins University"` vs. `"JHU"`) is exactly the kind of ambiguity a persistent identifier resolves cleanly.

#### 6.4.2  Mapping Confidence and the `skos:closeMatch` vs. `skos:exactMatch` Distinction

Not every platform term has a clean 1:1 external equivalent, and the ontology's formal representation must not overclaim equivalence where none exists. The platform adopts the standard SKOS mapping-relation distinction:

- **`skos:exactMatch`** — used only where the platform term and the external term are interchangeable in every practical sense (e.g., a specific molecule mapped to its ChEBI entry).
- **`skos:closeMatch`** — used where the terms are similar enough to be useful for search and discovery but not strictly interchangeable (e.g., a platform Disease term mapped to a MeSH heading that is slightly broader or narrower in scope).
- **`skos:broadMatch` / `skos:narrowMatch`** — used explicitly for class-level mappings, such as a specific platform Drug mapped to its broader ATC therapeutic class.
- **No mapping recorded** — used, deliberately, rather than forcing a low-confidence mapping, whenever no external term is a reasonable match; an unmapped term is a visible gap the Ontology Service's `unmapped-term rate` metric (Ch.4 §4.13) is designed to surface, not a failure to hide.

---

### 6.5  Term Lifecycle and Governance (Layer 1)

Every controlled vocabulary in this chapter is subject to the same versioned change process, directly implementing Chapter 2 §2.6 principle 6 (every schema is versioned, with a documented migration path) and Chapter 4 §4.13's governance-review requirement.

```
Term change proposed
   (new term, label change, deprecation, or external-mapping change)
      |
      v
Governance review
   (per Ch.2 §2.6: written rationale + migration plan required —
    NOT a unilateral technical commit, regardless of who proposes it)
      |
      v
New Concept Scheme version published
   (immutable — the prior version remains permanently resolvable,
    per Ch.2 §2.6 principle 15)
      |
      v
If deprecating a term: migration mapping recorded
   (skos:notation "deprecated" + a required successor term reference,
    or an explicit "no successor — term retired without replacement"
    annotation, never a silent removal)
      |
      v
Dependent services notified
   (Metadata, Knowledge Graph, Search, AI — per the OntologyVersionPublished
    event, Ch.4 §4.13)
      |
      v
Existing entries classified under the deprecated term remain valid
   and queryable under both the old and new term until curators
   complete a (non-urgent) reclassification pass
```

**Why deprecated terms are never deleted.** An Experiment curated in 2027 under a `domain` value that is later split into two more specific terms must remain fully interpretable in 2046, consistent with the platform's twenty-year horizon (Ch.2 §2.2). Deleting a term would silently invalidate every historical entry classified under it — a direct violation of Ch.2 §2.9's Immutable Releases principle, applied here specifically to vocabulary rather than to data entries.

**Governance authority.** Per Chapter 4 §4.13, only `Curation Lead` and `Administrator` roles may approve a vocabulary change, and — critically — every such change requires the same documented, public rationale the project's governance charter already requires for schema changes generally; there is no separate, lower-bar process for "just adding a term."

---

### 6.6  Formal Representation (Layer 3, `PLANNED`)

#### 6.6.1  SKOS Concept Scheme Structure

Each Core Controlled Vocabulary in §6.3 is represented, at the point Layer 3 is implemented, as a SKOS `ConceptScheme` containing `Concept` instances related by `skos:broader` / `skos:narrower` / `skos:related`. An illustrative expansion of the currently-flat `domain` scheme into a genuine hierarchy:

```
ConceptScheme: ddm:domain
  Concept: ddm:domain/Oncology
    skos:prefLabel: "Oncology"
    skos:narrower:
      - ddm:domain/Oncology/SolidTumor
      - ddm:domain/Oncology/Hematologic
      - ddm:domain/Oncology/Pediatric
    skos:closeMatch: mesh:D009369  ("Neoplasms")

  Concept: ddm:domain/Oncology/SolidTumor
    skos:prefLabel: "Solid Tumor Oncology"
    skos:broader: ddm:domain/Oncology
    skos:narrower:
      - ddm:domain/Oncology/SolidTumor/NSCLC
      - ddm:domain/Oncology/SolidTumor/Breast
      - ... (per the platform's actual curated entry distribution,
             added incrementally rather than pre-populated speculatively)
```

**Design principle: grow the hierarchy from curated data, not from a speculative complete taxonomy.** Per Chapter 2 §2.11 principle 5 ("every major change must be justifiable on both scientific and technical grounds"), new narrower Concepts under `Oncology` are added when the curation team actually has entries that need that level of specificity — not pre-populated with every conceivable subcategory in advance, which would create a maintenance burden and an appearance of coverage the dataset does not yet have.

#### 6.6.2  Where OWL Reasoning Is Applied: Intervention Class Hierarchy

The one part of this ontology designed for actual description-logic reasoning, per the decision in §6.1:

```
Class: ddm:InterventionClass
  DisjointWith: (siblings under the same parent are mutually exclusive
                 by design, enabling automated consistency checking)

Class: ddm:InterventionClass/SSRI
  SubClassOf: ddm:InterventionClass/Antidepressant
  EquivalentTo: hasATCCode some atc:N06AB   (a necessary-and-sufficient
                                              condition, enabling a reasoner
                                              to automatically classify any
                                              Drug carrying that ATC code
                                              as an SSRI, rather than
                                              requiring a curator to
                                              manually tag it)
```

**Why this specific hierarchy earns OWL's complexity.** The funding case for this platform explicitly identifies cross-drug-class trend analysis (e.g., "show every negative result across any SSRI, not just the specific molecule I searched for") as a headline Knowledge Graph Service use case. Automated subsumption reasoning is what makes that query correct and complete without requiring a curator to manually tag every individual drug's class membership by hand — the reasoner infers it from the ATC code, which is itself an external, already-governed classification (§6.4).

#### 6.6.3  Competency Questions

Following standard ontology-engineering methodology, the formal ontology's adequacy is tested against a fixed set of competency questions it must be able to answer correctly. A representative subset:

1. *"Show every negative result for any intervention in the same drug class as [a named SSRI], across every institution type."* — requires Layer 3 class-hierarchy reasoning (§6.6.2) plus Layer 2's `institution_type` facet.
2. *"Which negative results have never been assigned an external disease-ontology mapping?"* — a direct query against the `unmapped-term rate` metric (Ch.4 §4.13), used to prioritize curator ontology-enrichment work.
3. *"If I search using the MeSH heading for a disease rather than the platform's own term, do I still find the relevant entries?"* — tests the Layer 4 mapping's practical query-time utility, not just its existence as a static annotation.
4. *"What was the `domain` classification scheme's state at the time a specific historical entry was curated, even if the scheme has since been revised?"* — tests the versioning discipline in §6.5.
5. *"Which platform Institution Type values have no reasonable ROR `types` equivalent, and how are those entries handled?"* — tests that the mapping strategy (§6.4) degrades gracefully rather than silently, per the explicit "no mapping recorded" option in §6.4.2.

A formal ontology that cannot correctly answer all five of these — evaluated as an explicit test suite once Layer 3/4 are implemented — is not considered complete, regardless of how many terms it contains.

---

### 6.7  Semantic Relationship Catalog

Beyond the standard SKOS `broader`/`narrower`/`related` relations used for hierarchical classification, the Knowledge Graph Service (Ch.4 §4.4) requires a set of domain-specific, typed relationships to represent genuinely scientific connections between entities. These are distinct from classification relations: they connect *instances* (a specific Drug, a specific Disease), not concept-scheme terms.

| Relation | Domain → Range | Meaning |
|---|---|---|
| `treats` | Intervention → Disease | The Intervention is intended to address the Disease (may or may not be effective — this relation records intent, not Outcome) |
| `sameDrugClassAs` | Intervention → Intervention | Both share an `InterventionClass` membership (§6.6.2) |
| `contraindicatedFor` | Intervention → Disease/Condition | A recorded safety concern (sourced from curated Adverse Event data, `FUTURE`) |
| `targetsGeneOrProtein` | Intervention → (external ontology reference, e.g., a UniProt/HGNC identifier) | Mechanism-of-action linkage, `FUTURE`, dependent on molecular-target metadata not yet in the core schema |
| `replicates` | Experiment → Experiment | Matches Ch.5 §5.3.3's Replication entity |
| `contradicts` | Outcome → Outcome | Two Outcomes reach opposing conclusions about the same or closely related Hypothesis |
| `supports` | Evidence → Hypothesis | Matches Ch.5 §5.5.3 |
| `sameInstitutionAs` | Institution → Institution (via ROR) | Deduplication relation, §6.4.1 |
| `sameResearcherAs` | Researcher → Researcher (via ORCID) | Deduplication relation, §6.4.1 |
| `precededBy` / `supersedes` | Ontology Term → Ontology Term | The deprecation/migration relation from §6.5 |

Each relationship in this catalog is a typed edge in the Knowledge Graph Service's graph store (Ch.4 §4.4, Ch.3 §3.8), and each is subject to the same provenance requirement as any other platform data: a `treats` or `contraindicatedFor` edge must be traceable to the curated Experiment/Outcome data (or, for `FUTURE` AI-assisted linking, to the AI Service's confidence-scored suggestion, per Ch.2 §2.9) that justifies it — no relationship edge is asserted without a recorded basis.

---

### 6.8  Ontology Quality Assurance

Consistent with the Machine Validation principle (Ch.2 §2.9) applied to the ontology layer specifically, the following automated checks are `PLANNED` as part of the Ontology Service's CI pipeline, run on every proposed vocabulary change:

| Check | Purpose |
|---|---|
| **Orphan term detection** | Every non-root Concept must have at least one `skos:broader` relation; an orphaned term is a governance-review failure, not a silent gap |
| **Cycle detection** | The `broader`/`narrower` graph must be acyclic; a cycle indicates a modeling error, not a legitimate ontology structure |
| **Disjointness consistency** | For OWL-reasoned hierarchies (§6.6.2), no instance may be classified under two declared-disjoint sibling classes simultaneously |
| **Mapping-confidence audit** | Every `skos:exactMatch` is periodically re-verified against the external source's current version, since external standards (MeSH, SNOMED CT) themselves version and occasionally deprecate terms |
| **Unmapped-term rate trend** | Tracked as a first-class metric (Ch.4 §4.13), reviewed at each governance cycle to prioritize curator ontology-enrichment effort |
| **Competency-question regression suite** | The five questions in §6.6.3 (and any added later) are re-run as an automated test against every proposed ontology version before it is approved |

---

### 6.9  Implementation Status Summary

| Layer | Status | Current Production Equivalent |
|---|---|---|
| Layer 1 — Governance & Versioning | `PLANNED` | Ad hoc PR-based schema-change review; no formal term-lifecycle process yet |
| Layer 2 — Core Controlled Vocabularies | `OPERATIONAL` | Flat JSON Schema enums, exactly as cataloged in §6.3 |
| Layer 3 — Domain-Specific Terminologies | `PLANNED` | None — `domain` and `intervention.type` are single-level today |
| Layer 4 — External Standard Mappings | `FUTURE` (ROR/ORCID prioritized, §6.4.1) | `researcher_orcid` schema field only |
| OWL reasoning (Intervention Class) | `FUTURE` | None |
| Ontology QA pipeline (§6.8) | `PLANNED` | None — vocabulary changes today are reviewed the same way any other schema change is reviewed, without ontology-specific automated checks |

---

### 6.10  Summary and Handoff

This chapter has specified the platform's ontology as a four-layer stack: a governed change process (Layer 1), the five controlled vocabularies already enforced in production (Layer 2), a planned hierarchical enrichment of those vocabularies grounded in actual curated data rather than speculative completeness (Layer 3), and a prioritized mapping strategy onto the external standards that let this platform's data interoperate with the rest of the open scientific data ecosystem (Layer 4). The API Specification chapter's task is to expose every concept scheme, term, and mapping defined here through the `/ontology/*` endpoints first scoped in Chapter 4 §4.13; the AI Services Architecture chapter's task is to specify exactly how embedding generation and entity-linking (Ch.4 §4.5) are permitted to *propose* extensions to this ontology while remaining strictly bound by §6.5's rule that no vocabulary change is ever unilateral, automated, or unreviewed.
