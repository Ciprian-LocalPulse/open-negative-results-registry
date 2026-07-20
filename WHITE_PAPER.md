# **Open Negative Results Registry (ONRR)**

## **A FAIR-Compliant, Open-Source Infrastructure for Publishing, Indexing, and Preserving Negative Research Results**

**White Paper – Version 1.0**

**Author:** Ciprian Ștefan Pleșca  
**Affiliation:** Founder @LocalPulse; Lead Enterprise AI Architect  
**Contact:** contact@agentflow-enterprise.com  
**Date:** July 2026  
**License:** CC-BY 4.0 (content), MIT (code)

---

## **Table of Contents**

1. Executive Summary  
2. Introduction and Scientific Context  
3. The Problem: Publication Bias and the Costs of Untreated Negative Results  
4. Existing Solutions and Their Limitations  
5. Vision for the Open Negative Results Registry  
6. Design Principles and Architecture  
7. Metadata Schema and FAIR Interoperability  
8. Technical Specifications  
   * 8.1 Backend and API  
   * 8.2 Frontend and UX  
   * 8.3 Database and Storage  
   * 8.4 Security and Privacy  
9. Integrations with External Platforms  
10. Governance and Community Model  
11. Financial and Operational Sustainability  
12. Implementation Roadmap  
13. Case Studies and Pilot Programs  
14. Policy Recommendations and Advocacy  
15. Conclusions and Future Directions  
16. References  
17. Appendices  
    * Appendix A: Registration Form (Example)  
    * Appendix B: Sample JSON for a Registration  
    * Appendix C: Class Diagram (Simplified)  
    * Appendix D: Installation and Deployment Guide  
    * Appendix E: Complete Metadata Schema (JSON Schema)  
    * Appendix F: API Endpoints (OpenAPI 3.0 Snippet)  
    * Appendix G: Security Whitepaper Addendum  
    * Appendix H: Glossary of Terms

---

## **1\. Executive Summary**

The publication of negative results (null findings, failed experiments, non-significant results) represents one of the most critical challenges in contemporary science. Publication bias (the "file drawer problem") distorts the scientific literature, wastes resources through the duplication of failed studies, and undermines the credibility of research.

This white paper presents the **Open Negative Results Registry (ONRR)** – an open-source, FAIR-compliant platform designed for the registration, indexing, and dissemination of negative research results across all scientific domains. ONRR combines metadata standards (DataCite, ClinicalTrials.gov, DCAT), open science principles (OSF, Zenodo, ORCID), and modern architectures (zero-trust, blockchain-secured, federated learning-ready) to create a global, interoperable, and sustainable registry.

The document includes:

* The scientific and ethical context of publishing negative results  
* Analysis of gaps in existing infrastructures  
* Detailed technical specifications (architecture, API, metadata schema)  
* Governance and sustainability models  
* Implementation and adoption roadmap

---

## **2\. Introduction and Scientific Context**

## **2.1 What Are Negative Results?**

Negative results include:

* **Null findings**: Hypotheses not supported by data  
* **Non-significant results**: Statistical effects below significance thresholds  
* **Failed replications**: Studies that do not reproduce prior results  
* **Methodological failures**: Experiments that failed due to technical reasons

## **2.2 Why Do They Matter?**

* **Prevention of duplication**: Avoids wasting resources on experiments that have already failed.github+1  
* **Meta-analysis integrity**: Meta-analyses without negative results overestimate true effect sizes.[pplsopenresearch.github](https://pplsopenresearch.github.io/assets/pdfs/OpenResearch_RegisteredReports.pdf)  
* **Transparency**: Increases public and peer reviewer trust in science.researchregistry+1

## **2.3 The Scientific Imperative**

The scientific method relies on falsifiability. Negative results are not failures; they are data points that refine theories, redirect research efforts, and prevent future resources from being wasted. However, the current incentive structure in academia rewards novelty, positive findings, and high-impact publications, creating a systemic bias against negative results.

---

## **3\. The Problem: Publication Bias and the Costs of Untreated Negative Results**

## **3.1 The File Drawer Problem**

Over 50% of clinical trials are never published, with the majority having negative or null results. Journals prefer "novelty" and "positive findings," creating a systemic bias.openaccesspub+1

## **3.2 Estimated Costs**

* **Financial**: Hundreds of millions of USD/year wasted on reproducing failed studies.  
* **Ethical**: Participants in clinical trials exposed to risk without added scientific value.  
* **Epistemic**: The literature becomes distorted; clinical and policy decisions are based on incomplete evidence.

## **3.3 The Replication Crisis**

In psychology, approximately 70% of studies fail to replicate when tested independently. In AI/ML, 95% of enterprise generative AI pilots fail. Without a mechanism to publish these failures, the scientific community continues to invest in doomed approaches.[fortune](https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/)

## **3.4 The Opportunity Cost**

Every unpublished negative result represents:

* Lost learning opportunities for other researchers  
* Duplicated effort and funding  
* Delayed scientific progress  
* Erosion of public trust in science

---

## **4\. Existing Solutions and Their Limitations**

| Platform | Type | Coverage | Limitations |
| ----- | ----- | ----- | ----- |
| **ClinicalTrials.gov** | Registry (RCTs) | Clinical trials only | Does not mandate post-completion negative results; limited to FDA-regulated studies |
| **OSF Registries** | Preregistration | Multidisciplinary | Not a results repository; only study plans |
| **ResearchRegistry.com** | General research | All types | Paid service; limited curation; low adoption |
| **IJNR (International Journal of Negative Results)** | Journal | All domains | Limited capacity; traditional peer review; low visibility |
| **WASTE Journal** | Archive | Negative results | Small platform; limited discoverability |
| **PubMed Central** | Repository | Published articles | Does not accept unpublished negative results |

**Gap:** There is no **open, free, FAIR-compliant registry with a public API and standardized metadata schema** dedicated exclusively to negative results.

---

## 

## **5\. Vision for the Open Negative Results Registry**

## **5.1 Mission**

"To make every negative result discoverable, accessible, interoperable, and reusable – to save science from wasting its own ignorance."

## **5.2 Objectives**

1. **Free and open registration** for any type of study with negative results.  
2. **FAIR-compliant metadata schema** based on standards (DataCite, DCAT, SIO).  
3. **Public REST \+ GraphQL API** for automated integrations.  
4. **Persistent identifiers (DOI)** for every registration.  
5. **Interoperability** with OSF, Zenodo, ORCID, Crossref, PubMed.  
6. **Community-driven governance** that is transparent and decentralized.  
7. **Long-term sustainability** (grants, donations, institutional partnerships).

## **5.3 Core Values**

* **Openness**: All code, data, and documentation are open-source.  
* **Inclusivity**: All disciplines, all geographies, all career stages.  
* **Integrity**: Rigorous metadata validation; anti-spam measures.  
* **Sustainability**: Built for decades, not years.

---

## **6\. Design Principles and Architecture**

## **6.1 Design Principles**

| Principle | Description |
| ----- | ----- |
| **Open by default** | Code, data, documentation – all open-source |
| **FAIR-first** | Metadata schema designed for Findability, Accessibility, Interoperability, Reusability pubmed.ncbi.nlm.nih+1 |
| **Minimal viable bureaucracy** | Registration in \<10 minutes; no barriers |
| **Zero-trust security** | OAuth2/OIDC authentication; mandatory 2FA for admins |
| **Extensible** | Modules for domain-specific needs (clinical, social sciences, AI/ML) |
| **Decentralized** | Self-hosting option for institutions |

## **6.2 High-Level Architecture**

text  
`┌─────────────────────────────────────────────────────────┐`  
`│                     Frontend (React/Next.js)            │`  
`│   - Public Search & Browse                              │`  
`│   - Submission Wizard                                   │`  
`│   - User Dashboard                                      │`  
`└─────────────────────────────────────────────────────────┘`  
                            `│`  
                            `▼`  
`┌─────────────────────────────────────────────────────────┐`  
`│                      API Gateway (Kong/Traefik)         │`  
`│   - Rate limiting, Auth, Logging                        │`  
`└─────────────────────────────────────────────────────────┘`  
                            `│`  
            `┌───────────────┴───────────────┐`  
            `▼                               ▼`  
`┌───────────────────────┐       ┌───────────────────────┐`  
`│   Backend (FastAPI)   │       │   Backend (FastAPI)   │`  
`│   - Submission API    │       │   - Search API        │`  
`│   - Validation        │       │   - Elasticsearch     │`  
`└───────────────────────┘       └───────────────────────┘`  
            `│                               │`  
            `▼                               ▼`  
`┌───────────────────────┐       ┌───────────────────────┐`  
`│   PostgreSQL (DB)     │       │   Elasticsearch       │`  
`│   - Registrations     │       │   - Full-text Search  │`  
`│   - Users, Roles      │       │   - Faceted Search    │`  
`└───────────────────────┘       └───────────────────────┘`  
            `│`  
            `▼`  
`┌───────────────────────┐`  
`│   Object Storage      │`  
`│   (S3-compatible)     │`  
`│   - Attachments, Data │`  
`└───────────────────────┘`

## **6.3 Deployment Options**

* **Cloud-hosted (SaaS)**: Managed by ONRR core team.  
* **Self-hosted (On-premise)**: Docker/Kubernetes deployment for institutions.  
* **Hybrid**: Federated registry model with multiple nodes.

---

## **7\. Metadata Schema and FAIR Interoperability**

## **7.1 Metadata Foundation**

The ONRR schema builds on:

* **DataCite Metadata Schema 4.5** (for DOI and bibliographic metadata)  
* **DCAT 3.0** (for datasets and distributions)  
* **SIO (Semanticscience Integrated Ontology)** (for biomedical entities)  
* **NFDI4Health MDS** (for health research metadata)[pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/40397930/)

## **7.2 Core Entities**

| Entity | Key Fields |
| ----- | ----- |
| **Registration** | `id`, `doi`, `title`, `description`, `study_type`, `discipline`, `hypothesis`, `primary_outcome`, `secondary_outcomes`, `methods`, `sample_size`, `inclusion_criteria`, `exclusion_criteria`, `analysis_plan`, `results_summary`, `conclusion`, `date_submitted`, `date_modified`, `status` |
| **Author** | `id`, `orcid`, `name`, `affiliation`, `email` |
| **Institution** | `id`, `ror_id`, `name`, `country` |
| **Funding** | `id`, `funder_id`, `award_number`, `amount` |
| **RelatedWork** | `id`, `type` (preprint, publication, dataset), `doi`, `url` |

## **7.3 Crosswalks and Mappings**

| External Schema | ONRR Mapping |
| ----- | ----- |
| **ClinicalTrials.gov** | `study_type`, `primary_outcome`, `sample_size`, `inclusion/exclusion` |
| **DataCite** | `doi`, `title`, `creators`, `publisher`, `publication_year` |
| **OSF** | `project_id`, `registration_id` |
| **Zenodo** | `concept_doi`, `version_doi` |

## **7.4 FAIR Compliance Checklist**

| FAIR Principle | Implementation |
| ----- | ----- |
| **Findable** | DOI per registration; indexed in Elasticsearch; searchable via API |
| **Accessible** | Open API; no paywalls; S3 storage for attachments |
| **Interoperable** | Metadata crosswalks to DataCite, DCAT, SIO; JSON-LD support |
| **Reusable** | CC0 for metadata; CC-BY for content; clear licensing |

---

## **8\. Technical Specifications**

## **8.1 Backend and API**

* **Framework**: FastAPI (Python 3.11+)  
* **Authentication**: OAuth2 \+ OpenID Connect (Keycloak/Auth0)  
* **API Endpoints**:  
  * `POST /registrations` – Create registration  
  * `GET /registrations/{id}` – Get registration details  
  * `PUT /registrations/{id}` – Update registration  
  * `DELETE /registrations/{id}` – Delete registration (admin only)  
  * `GET /search?q=...` – Full-text search  
  * `GET /export/csv`, `GET /export/json` – Data export

## **Example API Request (Create Registration)**

text  
`POST /api/v1/registrations`  
`Content-Type: application/json`  
`Authorization: Bearer <token>`

`{`  
  `"title": "Null Effect of Cognitive Training on Working Memory",`  
  `"discipline": "Psychology",`  
  `"study_type": "Experimental",`  
  `"hypothesis": "Cognitive training will improve working memory scores.",`  
  `...`  
`}`

## **8.2 Frontend and UX**

* **Framework**: Next.js 14+ (React Server Components)  
* **Features**:  
  * Multi-step submission wizard (5 steps)  
  * Advanced search with filters (discipline, study type, year, country)  
  * User dashboard (my registrations, generated DOIs)  
  * ORCID integration (login and profile import)

## **8.3 Database and Storage**

* **PostgreSQL 15+**:  
  * Tables: `registrations`, `authors`, `institutions`, `funding`, `audit_log`  
  * Full-text indexes on `title`, `description`, `hypothesis`  
* **Elasticsearch 8.x**:  
  * Index `registrations` for advanced search  
  * Aggregations for statistics (e.g., \#registrations by discipline)  
* **S3-compatible storage**:  
  * MinIO (self-hosted) or AWS S3  
  * Attachments: protocols, datasets, code repositories

## 

## **8.4 Security and Privacy**

* **GDPR Compliance**:  
  * Explicit consent for personal data  
  * Right to erasure (right to be forgotten)  
  * Author pseudonymization on request  
* **Audit Log**:  
  * All modifications logged in `audit_log` with timestamp and user ID  
* **Rate Limiting**:  
  * 100 requests/hour for public API  
  * 1000 requests/hour for authenticated API  
* **Zero-Trust Architecture**:  
  * No implicit trust; all requests authenticated and authorized  
  * Micro-segmentation of services  
  * Encryption in transit (TLS 1.3) and at rest (AES-256)

---

## **9\. Integrations with External Platforms**

## **9.1 ORCID**

* Login via ORCID OAuth  
* Automatic profile import (name, affiliation, email)  
* Link each registration to ORCID author profile

## **9.2 Zenodo / Figshare**

* DOI generation via Zenodo API  
* Automatic upload of attached datasets

## **9.3 Crossref / PubMed**

* Metadata submission for indexing  
* Link to subsequent publications (even if none, can note "null publication")

## **9.4 OSF Registries**

* Cross-registration: ONRR ID in OSF and vice versa  
* Metadata synchronization via API

## **9.5 DataCite**

* DOI registration and metadata updates  
* Event tracking (citations, downloads, views)

---

## **10\. Governance and Community Model**

## **10.1 Governance Structure**

| Body | Role | Composition |
| ----- | ----- | ----- |
| **Steering Committee** | Strategy, policy, funding | 5-7 members (university reps, editors, NGOs) |
| **Technical Committee** | Architecture, security, roadmap | 3-5 senior engineers |
| **Community Advisory Board** | User feedback, advocacy | 10+ community members (researchers, librarians, patients) |
| **Moderators** | Content curation, abuse verification | Rotating volunteers weekly [researchregistry](https://www.researchregistry.com/wp-content/uploads/rr_registration_booklet_v5.2.pdf) |

## **10.2 Usage Policies**

* **License**: CC0 for metadata, CC-BY for content  
* **Conduct**: Code of Conduct based on Contributor Covenant 2.1  
* **Abuse & Spam**:  
  * Reporting via "Report" button  
  * Deletion within 48 hours for fraudulent content  
  * Permanent ban for repeat offenders

## **10.3 Decision-Making**

* **Consensus-based**: Major decisions require 2/3 majority of Steering Committee.  
* **Transparent**: All meeting minutes published on GitHub.  
* **Inclusive**: Community input via GitHub Issues and annual surveys.

---

## **11\. Financial and Operational Sustainability**

## **11.1 Funding Sources**

| Source | Potential | Example |
| ----- | ----- | ----- |
| **EU Grants** | €500k-2M | Horizon Europe, ERC |
| **Donations** | €50-500/user | Open Collective, GitHub Sponsors |
| **Institutional Partnerships** | €10k-100k/year | Universities, libraries, publishers |
| **Premium Features** | €500-5k/org | API rate increase, white-label, analytics |

## **11.2 Annual Operational Costs (Estimate)**

| Category | Cost (EUR/year) |
| ----- | ----- |
| Hosting (cloud, storage) | €10k |
| Development (1-2 FTE) | €80k |
| Governance & Community | €20k |
| Marketing & Advocacy | €15k |
| **Total** | **€125k** |

## **11.3 Sustainability Plan**

* **Year 1-2**: Grant-funded (Horizon Europe, Wellcome Trust).  
* **Year 3-5**: Diversified (50% grants, 30% partnerships, 20% donations).  
* **Year 5+**: Self-sustaining (institutional memberships, premium features).

---

## **12\. Implementation Roadmap**

## **Phase 1: Foundations (0-6 months)**

* MVP backend (FastAPI \+ PostgreSQL)  
* Frontend submission wizard  
* Final metadata schema  
* 10-20 pilot registrations (volunteers)

## **Phase 2: Integrations (6-12 months)**

* DOI generation (Zenodo)  
* ORCID login  
* Public API documented (OpenAPI/Swagger)  
* 100+ registrations

## **Phase 3: Scaling (12-24 months)**

* Self-hosting option (Docker \+ Helm charts)  
* Domain-specific modules (clinical, AI/ML, social sciences)  
* 1000+ registrations  
* Partnerships with 5+ universities

## **Phase 4: Maturation (24-36 months)**

* Indexing in PubMed/Crossref  
* 10k+ registrations  
* Financial sustainability (50% of costs covered)

---

## **13\. Case Studies and Pilot Programs**

## **13.1 Case Study 1: Replication Crisis in Psychology**

* **Context**: 70% of psychology studies fail to replicate.  
* **ONRR Use**: Researchers upload protocols and negative results.  
* **Impact**: Meta-analyses now include negative results, reducing bias.

## **13.2 Case Study 2: AI/ML Failed Experiments**

* **Context**: 95% of enterprise AI pilots fail.[fortune](https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/)  
* **ONRR Use**: Companies upload failed experiments (without NDA conflicts).  
* **Impact**: Other teams avoid the same approaches, accelerating innovation.

## 

## **13.3 Case Study 3: Clinical Trial Null Findings**

* **Context**: Many phase II/III trials show no efficacy.  
* **ONRR Use**: Sponsors register null results before journal submission.  
* **Impact**: Reduces duplication of ineffective treatments; informs meta-analyses.

---

## **14\. Policy Recommendations and Advocacy**

## **14.1 For Publishers**

* **Mandate**: All studies (positive or negative) must be registered before publication.  
* **Incentives**: Badges like "Transparent Registered Report" for articles.

## **14.2 For Funders**

* **Requirement**: Registration of negative results is a criterion for future grants.  
* **Recognition**: Negative results count as outputs in evaluations (e.g., REF, ANR).

## **14.3 For Institutions**

* **Policies**: Internal promotion for researchers who publish negative results.  
* **Infrastructure**: Self-host ONRR instance for universities.

## **14.4 For Governments**

* **National Strategies**: Include negative results infrastructure in open science roadmaps.  
* **Funding**: Dedicated grants for negative results platforms.

---

## **15\. Conclusions and Future Directions**

The Open Negative Results Registry proposes a paradigm shift: **failure is data, not shame**. Through robust technical infrastructure, transparent governance, and strategic advocacy, ONRR can become the global standard for publishing negative results.

**Future Directions:**

* AI-powered summarization for large registrations  
* Federated learning for privacy-preserving analytics  
* Blockchain timestamping for proof-of-existence  
* Integration with preprint servers (arXiv, bioRxiv, medRxiv)

---

## **16\. References**

World Archive of Scientific Trial & Error (WASTE)[wastejournal](https://www.wastejournal.org/)  
Registered Reports: What, Why, & How (PPLS Open Research)[pplsopenresearch.github](https://pplsopenresearch.github.io/assets/pdfs/OpenResearch_RegisteredReports.pdf)  
Open Science Training Handbook[github](https://github.com/Open-Science-Training-Handbook/Open-Science-Training-Handbook_EN/blob/master/02OpenScienceBasics/04ReproducibleResearchAndDataAnalysis.md)  
The Research Registry® Guidebook[researchregistry](https://www.researchregistry.com/wp-content/uploads/rr_registration_booklet_v5.2.pdf)  
International Journal of Negative Results[openaccesspub](https://openaccesspub.org/journal/international-journal-of-negative-results/membership)  
Handling negative research results (EDCH)[edch](http://resources.edch.eu/handling-negative-research-results)  
White Paper \- Open Science in a Digital Republic (CNRS)[science-ouverte.cnrs](https://www.science-ouverte.cnrs.fr/wp-content/uploads/2019/07/White-Paper-Open-Science-March-2016.pdf)  
OSF Registries[cos](https://www.cos.io/products/osf-registries)  
FAIRifying Clinical Studies Metadata (PubMed)[pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/34042684/)  
NFDI4Health Metadata Schema (JMIR Med Inform 2025\)[pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/40397930/)  
Registered Reports (Center for Open Science)[cos](https://www.cos.io/initiatives/registered-reports)  
Metadata Schema and Crosswalk Registry (Zenodo)[zenodo](https://zenodo.org/records/18874800)

---

## **17\. Appendices**

## **Appendix A: Registration Form (Example)**

text  
`# Registration Form`

`## Basic Info`  
`- Title: ...`  
`- DOI: (auto-generated)`  
`- Discipline: (dropdown)`  
`- Study Type: (dropdown)`

`## Hypothesis & Methods`  
`- Research Question: ...`  
`- Primary Hypothesis: ...`  
`- Methods: ...`  
`- Sample Size: ...`  
`- Inclusion/Exclusion: ...`

`## Outcomes`  
`- Primary Outcome: ...`  
`- Secondary Outcomes: ...`  
`- Results Summary: ...`

`## Authors`  
`- Name, ORCID, Affiliation, Email`

`## Attachments`  
`- Protocol (PDF)`  
`- Dataset (CSV/ZIP)`  
`- Code (GitHub URL)`  
---

## **Appendix B: Sample JSON for a Registration**

json  
`{`  
  `"id": "onrr:12345",`  
  `"doi": "10.5281/onrr.12345",`  
  `"title": "Null Effect of Cognitive Training on Working Memory in Adults",`  
  `"discipline": "Psychology",`  
  `"study_type": "Experimental",`  
  `"hypothesis": "Cognitive training will improve working memory scores.",`  
  `"primary_outcome": "Working memory score (WAIS-IV)",`  
  `"secondary_outcomes": ["Attention span", "Processing speed"],`  
  `"sample_size": 120,`  
  `"inclusion_criteria": "Adults 18-65, no neurological conditions",`  
  `"exclusion_criteria": "Prior cognitive training, psychiatric diagnosis",`  
  `"methods": "Randomized controlled trial, 8 weeks training",`  
  `"results_summary": "No significant difference between groups (p=0.42)",`  
  `"conclusion": "Hypothesis not supported. Cognitive training did not improve working memory.",`  
  `"authors": [`  
    `{`  
      `"name": "Jane Doe",`  
      `"orcid": "0000-0000-0000-0000",`  
      `"affiliation": "University of Example",`  
      `"email": "jane.doe@example.edu"`  
    `}`  
  `],`  
  `"date_submitted": "2026-07-20T10:00:00Z",`  
  `"status": "published"`  
`}`  
---

## **Appendix C: Class Diagram (Simplified)**

text  
`+----------------+       +----------------+       +----------------+`  
`| Registration   |<----->| Author         |<----->| Institution    |`  
`+----------------+       +----------------+       +----------------+`  
`| id             |       | id             |       | id             |`  
`| doi            |       | orcid          |       | ror_id         |`  
`| title          |       | name           |       | name           |`  
`| discipline     |       | affiliation    |       | country        |`  
`| study_type     |       | email          |       +----------------+`  
`| hypothesis     |       +----------------+`  
`| primary_outcome|`  
`| methods        |`  
`| results_summary|`  
`+----------------+`  
---

## **Appendix D: Installation and Deployment Guide**

## **Prerequisites**

* Docker 24+  
* Docker Compose 2.20+  
* PostgreSQL 15+  
* Elasticsearch 8.x  
* MinIO (or AWS S3 credentials)

## **Step 1: Clone Repository**

bash  
`git clone https://github.com/Ciprian-LocalPulse/open-negative-results-registry.git`  
`cd open-negative-results-registry`

## **Step 2: Configure Environment**

bash  
`cp .env.example .env`  
*`# Edit .env with your database credentials, S3 keys, etc.`*

## **Step 3: Start Services**

bash  
`docker-compose up -d`

## **Step 4: Run Migrations**

bash  
`docker-compose exec backend python -m migrate`

## **Step 5: Access Application**

* Frontend: `http://localhost:3000`  
* API: `http://localhost:8000/api/v1`  
* API Docs: `http://localhost:8000/docs`

---

## **Appendix E: Complete Metadata Schema (JSON Schema)**

json  
`{`  
  `"$schema": "http://json-schema.org/draft-07/schema#",`  
  `"title": "ONRR Registration",`  
  `"type": "object",`  
  `"properties": {`  
    `"id": {"type": "string"},`  
    `"doi": {"type": "string"},`  
    `"title": {"type": "string", "minLength": 10},`  
    `"discipline": {"type": "string", "enum": ["Psychology", "Medicine", "AI/ML", "Social Sciences", "Other"]},`  
    `"study_type": {"type": "string"},`  
    `"hypothesis": {"type": "string"},`  
    `"primary_outcome": {"type": "string"},`  
    `"secondary_outcomes": {"type": "array", "items": {"type": "string"}},`  
    `"sample_size": {"type": "integer", "minimum": 1},`  
    `"methods": {"type": "string"},`  
    `"results_summary": {"type": "string"},`  
    `"conclusion": {"type": "string"},`  
    `"authors": {`  
      `"type": "array",`  
      `"items": {`  
        `"type": "object",`  
        `"properties": {`  
          `"name": {"type": "string"},`  
          `"orcid": {"type": "string"},`  
          `"affiliation": {"type": "string"},`  
          `"email": {"type": "string", "format": "email"}`  
        `},`  
        `"required": ["name"]`  
      `}`  
    `},`  
    `"date_submitted": {"type": "string", "format": "date-time"},`  
    `"status": {"type": "string", "enum": ["draft", "submitted", "published", "withdrawn"]}`  
  `},`  
  `"required": ["title", "discipline", "hypothesis", "methods", "results_summary", "authors"]`  
`}`  
---

## **Appendix F: API Endpoints (OpenAPI 3.0 Snippet)**

text  
`openapi: 3.0.3`  
`info:`  
  `title: ONRR API`  
  `version: 1.0.0`  
`paths:`  
  `/registrations:`  
    `post:`  
      `summary: Create a new registration`  
      `requestBody:`  
        `required: true`  
        `content:`  
          `application/json:`  
            `schema:`  
              `$ref: '#/components/schemas/Registration'`  
      `responses:`  
        `'201':`  
          `description: Registration created`  
          `content:`  
            `application/json:`  
              `schema:`  
                `$ref: '#/components/schemas/Registration'`  
`components:`  
  `schemas:`  
    `Registration:`  
      `type: object`  
      `properties:`  
        `title:`  
          `type: string`  
        `discipline:`  
          `type: string`  
        `hypothesis:`  
          `type: string`  
        `# ... (full schema as in Appendix E)`  
---

## 

## **Appendix G: Security Whitepaper Addendum**

## **Threat Model**

* **Threat Actors**: Malicious researchers, spammers, state actors, insider threats.  
* **Attack Vectors**: SQL injection, XSS, CSRF, DDoS, credential stuffing, data exfiltration.  
* **Mitigations**: Input validation, parameterized queries, CSP headers, rate limiting, WAF, 2FA.

## **Security Controls**

* **Authentication**: OAuth2 \+ OIDC with PKCE.  
* **Authorization**: RBAC (roles: user, moderator, admin).  
* **Encryption**: TLS 1.3 for transit; AES-256 for storage.  
* **Logging**: Centralized logging with ELK stack; retention 90 days.  
* **Incident Response**: Defined playbook; 24-hour breach notification.

---

## **Appendix H: Glossary of Terms**

| Term | Definition |
| ----- | ----- |
| **Negative Results** | Research findings that do not support the hypothesis or show no significant effect. |
| **FAIR Principles** | Findable, Accessible, Interoperable, Reusable – a framework for data stewardship. |
| **DOI** | Digital Object Identifier – a persistent identifier for digital objects. |
| **ORCID** | Open Researcher and Contributor ID – a unique identifier for researchers. |
| **Zero-Trust** | Security model that assumes no implicit trust; all requests must be authenticated and authorized. |

