# Dark Data Medicine — Platform Architecture Series

## Chapter 9: Deployment Architecture

*Document status: Normative. Governed by Chapter 2 (Cloud Agnostic §2.3.9, Technology Independence §2.8), Chapter 3 (§3.10 Scalability Strategy, §3.11 High Availability), and Chapter 8 (Security Architecture — every control specified there is realized concretely here). This chapter answers: given everything specified so far, how does it actually get deployed, by whom, and on what?*

*Version 0.1 — Draft for governance review*

---

### 9.0  Purpose and Scope

Every prior chapter specified a *what* and a *why*. This chapter specifies the *how*, *where*, and *by whom* — the concrete infrastructure, environments, and operational processes that turn the target-state architecture of Chapters 3–8 into something actually running. It is organized around the five-stage scalability path first introduced in Chapter 3 §3.10, because deployment architecture is not one fixed diagram — it is a different, deliberately staged diagram at each point in the platform's growth, and conflating them (describing Stage 4's Kubernetes cluster as if it applied to today's Stage 1 reality) would violate the same honesty standard every prior chapter in this series has held to.

---

### 9.1  Deployment Environments

| Environment | Purpose | Data | Access |
|---|---|---|---|
| **Local (Developer)** | Individual contributor development and testing | Synthetic/fixture data only, matching the schema's example entries (Ch.5) | Any contributor with repository access |
| **Staging** | Pre-release integration testing, DAST execution (Ch.8 §8.5), curator UAT | A sanitized, non-production dataset snapshot or synthetic data at production scale | Maintainers and designated testers |
| **Production** | The live, public registry | Real, curator-approved data | Public read; role-gated write per Ch.8 §8.4 |
| **Disaster Recovery (DR)** | Standby environment for the Backup Service's tested restoration target (Ch.4 §4.18) | Restored-from-backup, verified via periodic restoration testing | Administrators only, activated during an actual incident |

**Promotion path.** `Local → Staging → Production`, gated at each transition by the CI/CD checks in §9.4; no direct-to-production deployment path exists for any change, including hotfixes, which pass through an expedited but never skipped staging validation.

---

### 9.2  Stage-by-Stage Deployment Topology

This section is the deployment-level realization of Chapter 3 §3.10's five stages. Each stage diagram shows only what actually needs to be running at that stage — later-stage components are omitted, not merely marked absent, because a deployment diagram cluttered with future infrastructure is itself a form of the overclaiming this series has consistently avoided.

#### 9.2.1  Stage 1 — Single Static Deployment  `OPERATIONAL` (current stage)

```
                    +-------------------------------+
                    |     GitHub Pages (CDN-backed)   |
                    |   static search site + assets    |
                    +-------------------------------+
                                   ^
                                   | build artifact
                    +-------------------------------+
                    |      GitHub Actions Runners      |
                    |  validate-submissions.yml         |
                    |  test-suite.yml                   |
                    |  deploy-site.yml                  |
                    +-------------------------------+
                                   ^
                                   | reads/writes
                    +-------------------------------+
                    |   Git Repository (GitHub)        |
                    |   data/ (JSON entries, versioned)|
                    |   scripts/, tests/, docs/         |
                    +-------------------------------+
```

**Deployment process.** A contributor opens a pull request; `validate-submissions.yml` and `test-suite.yml` run automatically; on merge to the main branch, `deploy-site.yml` regenerates the static search index and publishes it to GitHub Pages. There is no server to provision, patch, or scale — the entire Stage 1 "infrastructure" is GitHub's own hosting, chosen deliberately per Chapter 2 §2.3.9's Cloud Agnostic principle not because GitHub is the permanent home, but because a static site has no meaningful vendor lock-in: the identical build artifact deploys to any static host.

**Cost profile.** Effectively zero marginal hosting cost, directly supporting the sustainability case referenced throughout the platform's funding materials.

#### 9.2.2  Stage 2 — Containerized Services  `PLANNED`

```
                          +----------------------+
                          |   API Gateway (Ch.3)   |
                          |   TLS termination,      |
                          |   rate limiting (Ch.7)  |
                          +-----------+------------+
                                      |
              +----------+----------+----------+----------+
              |          |          |          |          |
              v          v          v          v          v
        +---------+ +---------+ +---------+ +---------+ +---------+
        |Submission| |Metadata | | Search  | |  Auth   | | Review  |
        |Container | |Container| |Container| |Container| |Container|
        +---------+ +---------+ +---------+ +---------+ +---------+
              |          |          |          |          |
              +----------+----------+----------+----------+
                                      |
                          +-----------v------------+
                          |   PostgreSQL (primary)    |
                          |   OpenSearch (single node) |
                          +------------------------+
```

**Deployment process.** Each Chapter 4 service ships as an independently versioned, independently deployable Docker image, built and pushed by CI on every merge to main, deployed via a simple container-orchestration tool (Docker Compose or a single-node equivalent) — deliberately not yet Kubernetes, per the staged-complexity principle in Ch.3 §3.10: Stage 2 exists specifically to prove out the containerized-service model at a scale that does not yet justify full orchestration overhead.

**Trigger for Stage 2 adoption.** Entry volume or curator-queue concurrency exceeding what Stage 1's static/CI-only model comfortably serves — concretely, the point at which the Submission Service needs to accept live API traffic (Ch.7 §7.5.1) rather than only Git pull requests.

#### 9.2.3  Stage 3 — Orchestrated Cluster  `PLANNED`, longer horizon

```
                          +----------------------+
                          |   Load Balancer         |
                          +-----------+------------+
                                      |
                          +-----------v------------+
                          |   Kubernetes Cluster      |
                          |  ---------------------    |
                          |  Deployments (per Ch.4     |
                          |  service, horizontally     |
                          |  autoscaled per §9.5)      |
                          |  ---------------------    |
                          |  Knowledge Graph, AI        |
                          |  Service pods (GPU node      |
                          |  pool for AI inference)      |
                          +-----------+------------+
                                      |
              +----------+----------+----------+----------+
              v          v          v          v          v
        PostgreSQL   OpenSearch    Neo4j     Vector DB   Object
        (HA cluster) (multi-node) (cluster)  (cluster)   Storage
```

**Deployment process.** Kubernetes manifests (or an equivalent orchestrator satisfying Ch.2 §2.3.9's Cloud Agnostic requirement) define every service's deployment, autoscaling policy, and resource limits declaratively; GitOps-style deployment (a Git-repository-defined desired state, reconciled automatically) is the target process, keeping the deployment configuration itself under the same version-control and review discipline as the application code.

#### 9.2.4  Stage 4–5 — Federation and Global Node Network  `FUTURE`

```
     +----------------+      +----------------+      +----------------+
     |  Primary Node    | <--> |  Institutional   | <--> |  National        |
     |  (this platform's|      |  Mirror Node A    |      |  Registry Node   |
     |  own deployment)  |      |  (partner-hosted)  |      |  (self-hosted)   |
     +----------------+      +----------------+      +----------------+
              |  Federation Service sync (Ch.4 §4.12, Ch.8 §8.10) — mutual TLS +
              |  signed messages, entry/metadata scope only
              v
     Each node runs an independent Stage 3 topology, deployed via the same
     container/Kubernetes artifacts, on infrastructure the operating
     institution controls entirely — per Ch.2 §2.3.9, no node depends on
     any other node's cloud vendor or infrastructure choice.
```

**Deployment process for a new mirror node.** A partner institution's technical team follows a documented self-hosted deployment guide (§9.7), using the identical container images the primary node runs, configures federation credentials through the governance-reviewed onboarding process (Ch.8 §8.10.1), and joins the network without requiring any change to the primary node's own deployment.

---

### 9.3  Infrastructure as Code

Every environment beyond Stage 1's GitHub-native hosting is defined declaratively, version-controlled, and reviewed through the same pull-request process as application code — infrastructure changes are never applied by an administrator manually executing commands against a live environment. This is a direct extension of Chapter 2 §2.6 (every change is versioned, nothing is silently applied) to the infrastructure layer specifically. Tooling is specified as a capability (declarative, idempotent, version-controlled infrastructure definition) rather than a specific product, per Ch.2 §2.8's Technology Independence principle — Terraform, Pulumi, or an equivalent are all conformant implementations.

---

### 9.4  CI/CD Pipeline (Full Lifecycle)

```
Pull Request Opened
      |
      v
Automated checks (parallel):
   - Schema validation (Ch.4 §4.1, Ch.3 §3.2)
   - Unit + integration test suite (Ch.4's Chapter, "tests/")
   - SAST scan (Ch.8 §8.5)
   - Dependency vulnerability scan (Ch.8 §8.8)
   - Lint / code-style check
      |
      v
Human code review  (required, no auto-merge for code — Ch.8 §8.8)
      |
      v
Merge to main
      |
      v
Build container images (per changed service)
      |
      v
Push to container registry (signed, per Ch.8 §8.8)
      |
      v
Deploy to Staging  (automatic)
      |
      v
Staging validation:
   - DAST scan (Ch.8 §8.5)
   - Integration smoke tests
   - (For API changes) OpenAPI/GraphQL schema-compatibility check (Ch.7 §7.2)
      |
      v
Manual promotion gate  (Curation Lead / Administrator approval)
      |
      v
Deploy to Production  (rolling deployment, §9.5)
      |
      v
Post-deployment health check  (Monitoring Service, Ch.4 §4.17)
      |
      v
Automatic rollback if health check fails
```

**Current implementation.** Stage 1's actual pipeline (`validate-submissions.yml`, `test-suite.yml`, `deploy-site.yml`) implements the leftmost and rightmost portions of this diagram — validation, testing, and deployment — without the container build, staging environment, or manual promotion gate stages, which apply from Stage 2 onward once there is a running service to promote rather than only a static site to publish.

---

### 9.5  Scaling and Resource Management

| Concern | Stage 2 Approach | Stage 3+ Approach |
|---|---|---|
| Horizontal scaling | Manual container replica count adjustment | Kubernetes Horizontal Pod Autoscaler, keyed to the per-service metrics defined in Chapter 4 (queue depth for Review, query latency for Search) |
| Database scaling | Single PostgreSQL primary, manual vertical scaling if needed | Read replicas (Ch.3 §3.11) added as read-query volume grows; connection pooling introduced ahead of, not reactively after, connection-limit incidents |
| AI/GPU workloads | N/A (AI Service is `FUTURE`, Ch.4 §4.5) | Dedicated GPU node pool, scaled independently of the general-purpose compute pool, since inference workloads have a fundamentally different resource profile than the platform's other services |
| Cost governance | Reviewed manually at each phase transition, aligned to the budget phases in the platform's funding case | Automated budget-alert thresholds tied to cloud spend, reviewed against the same phase-aligned budget |

---

### 9.6  Configuration and Secrets Deployment

Extending Chapter 8 §8.6.2's secrets-management architecture to deployment specifics: secrets are injected into running containers at deploy time from the secrets-management system, never baked into container images or committed to the infrastructure-as-code repository (§9.3) in plaintext — including in that repository's version history, which per Ch.2 §2.6's permanence guarantees would otherwise make a leaked secret effectively permanent. Environment-specific configuration (staging vs. production endpoints, feature flags) is separated cleanly from secrets, following the same "storage without proper handling has little value, and worse, real risk" logic that has recurred since Chapter 2 §2.3.2.

---

### 9.7  Self-Hosted / Institutional Mirror Deployment Guide (Outline)

For the Stage 4 federation model (§9.2.4), a documented, `FUTURE` deployment guide will cover, at minimum:

1. **Prerequisites.** Container runtime, minimum compute/storage specification, network requirements (mutual TLS support, Ch.8 §8.10).
2. **Deployment.** The identical container images and orchestration manifests the primary node uses (§9.2.3), configured via institution-specific environment variables only — no forked or institution-specific code branch, keeping every node running the same, auditable architecture (Ch.4 §4.21's closing principle, restated at the deployment layer).
3. **Federation onboarding.** Generating a node signing keypair, submitting it through the governance-reviewed onboarding process (Ch.8 §8.10.1), and configuring the sync channel.
4. **Operational handoff.** Pointers to the Operations Manual (the next document in this series) for the institution's own operational team.

This guide's `FUTURE` status reflects that it depends on the Federation Service itself (Ch.4 §4.12) existing, which in turn depends on Stages 2–3 being operational first — deployment documentation is written for infrastructure that exists, not speculatively ahead of it, consistent with this series' honesty standard.

---

### 9.8  Disaster Recovery Deployment

Directly operationalizing the Backup Service (Ch.4 §4.18) and High Availability requirements (Ch.3 §3.11): the DR environment (§9.1) is not a passive backup archive but a deployable environment — the same container images and infrastructure-as-code definitions used in Production, held ready to be stood up against the most recent verified backup. Recovery Time Objective (RTO) and Recovery Point Objective (RPO) targets are defined per Stage:

| Stage | RTO Target | RPO Target |
|---|---|---|
| Stage 1 | N/A — GitHub's own repository redundancy; effectively continuous | Effectively zero (every merge is immediately durable via Git) |
| Stage 2–3 | `PLANNED`: target under 4 hours for full production restoration | `PLANNED`: target under 1 hour of data loss, bounded by backup frequency (Ch.4 §4.18) |
| Stage 4–5 | Federation provides an additional resilience layer — a single node's DR failure does not take the network offline, since other nodes retain synchronized copies (Ch.4 §4.12) | Bounded by the least-stale synchronized peer node's data |

---

### 9.9  Deployment Quality Scenarios (extending Ch.3 §3.15, Ch.8 §8.14)

**Zero-downtime deployment.** *Stimulus:* a new version of the Search Service is deployed during normal operating hours. *Response:* rolling deployment (§9.4) replaces instances gradually behind the load balancer, with the previous version continuing to serve traffic until the new version passes its health check, per Chapter 3 §3.11. *Response Measure:* zero failed user-facing requests during a standard deployment, verified in staging before every production promotion.

**Configuration drift detection.** *Stimulus:* a manual, undocumented change is made directly against a production resource, bypassing the infrastructure-as-code process (§9.3). *Response:* the next infrastructure-as-code reconciliation run (GitOps-style, §9.2.3) detects the drift and either reconciles it back to the declared state or flags it for review, depending on the configured policy. *Response Measure:* no undetected drift persists beyond one reconciliation cycle.

**Cross-node deployment consistency (Stage 4+).** *Stimulus:* a security patch must be deployed across the primary node and every federation mirror simultaneously. *Response:* because every node runs the identical container images (§9.7), the patched image is published once and each node's own operator pulls and deploys it independently, on their own schedule — the architecture does not require, or assume, synchronized deployment timing across independently governed nodes. *Response Measure:* a documented maximum acceptable lag between primary-node patch availability and expected mirror-node adoption, communicated through the federation governance channel (Ch.8 §8.10.1).

---

### 9.10  Implementation Status Summary

| Component | Status |
|---|---|
| Stage 1 static deployment (GitHub Pages + Actions) | `OPERATIONAL` |
| Stage 2 containerized services | `PLANNED` |
| Stage 3 Kubernetes orchestration | `PLANNED`, longer horizon |
| Stage 4–5 federation deployment | `FUTURE` |
| Infrastructure as code | `PLANNED` |
| Full CI/CD pipeline (staging, promotion gate, rollback) | `PLANNED` (validation/test/deploy subset `OPERATIONAL`) |
| DR environment | `PLANNED` |
| Self-hosted mirror deployment guide | `FUTURE` |

---

### 9.11  Summary and Handoff

This chapter has translated the target-state architecture of Chapters 3–8 into a concrete, staged deployment reality — honest about the fact that today's actual deployment is Stage 1's static site and three CI workflows, and precise about exactly what threshold triggers the move to each subsequent stage. The Developer Guide's task is to take everything specified across this entire series and make it actionable for a new engineer's first week on the project — local environment setup, coding standards, the contribution workflow — while the Operations Manual's task is to make this chapter's deployment and disaster-recovery architecture actionable for whoever is on call when something, someday, goes wrong.
