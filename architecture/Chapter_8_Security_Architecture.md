# Dark Data Medicine — Platform Architecture Series

## Chapter 8: Security Architecture

*Document status: Normative. Governed by Chapter 2 (Zero Trust §2.3.7, Privacy by Design §2.3.6), Chapter 3 (§3.1 API Gateway, §3.12 Failure Scenarios), Chapter 4 (Authentication §4.6, Audit §4.16, Backup §4.18), and Chapter 7 (§7.3 API auth model). This chapter is the authoritative security contract every other document's security-relevant claims must trace back to.*

*Version 0.1 — Draft for governance review*

---

### 8.0  Purpose and Scope

Security has been referenced throughout this series — a Security field in every Chapter 4 service specification, Zero Trust as a founding architectural philosophy in Chapter 2, an authentication model in Chapter 7. This chapter is where those scattered references are unified into a single, coherent security architecture: a threat model, a data classification scheme, an identity and access model specified to implementation depth, and — because this platform is open-source infrastructure accepting public contributions by design — a supply-chain security posture that a typical closed-source enterprise security architecture does not need to address at all.

**What this platform is, and is not, from a security standpoint.** It is not a system that processes protected health information — Chapter 2 §2.3.6 excludes patient-level data from the domain model categorically, and this exclusion is this platform's single most consequential security design decision, because it removes an entire regulatory and threat surface (HIPAA-covered-entity obligations, GDPR special-category data handling) that a clinical data system of comparable scale would otherwise carry. It is a system whose highest-value asset is the **integrity and provenance** of its scientific dataset — the thing an attacker most plausibly wants to compromise is not confidential data extraction, but the trustworthiness of what the registry says is true.

---

### 8.1  Security Philosophy

Security in this architecture is not a separate layer bolted onto Chapters 2–7; it is a restatement of principles already established, made checkable:

| Ch.2 Principle | Security Restatement |
|---|---|
| Zero Trust (§2.3.7) | No request, internal or external, is trusted without validation; no service is exempt |
| Privacy by Design (§2.3.6) | Patient-identifiable data is structurally excluded, not merely policy-excluded |
| Human Accountability (§2.9) | Every consequential action has an identifiable, non-repudiable actor |
| Federation First (§2.3.8) | Trust does not centralize; a compromised node cannot compromise the network |
| Technology Independence (§2.8) | Security controls are specified as guarantees, not tied to one vendor's product |

Three additional principles are introduced specifically in this chapter:

- **Defense in depth.** No single control is trusted as sufficient — schema validation (Ch.4 §4.1), a PII screen (Ch.4 §4.8), and a database-level constraint all independently guard against the same failure mode (patient data entering the dataset), so that any one control's failure does not constitute a breach.
- **Least privilege, checked at every layer.** A role's permission grant (§8.4) is the maximum a user *may* have, not a default every service assumes without re-checking — the API Gateway checking a scope does not exempt the Review Service (Ch.4 §4.8) from independently checking that the caller holds the `Curator` role for the relevant domain.
- **Security posture proportional to twenty-year infrastructure, not to a typical SaaS product's threat model.** A registry expected to remain trusted and operating for decades (Ch.2 §2.2) must defend against slow, patient threats — a compromised long-term contributor, a supply-chain compromise introduced years before detection — not only opportunistic, fast-moving ones.

---

### 8.2  Threat Model

#### 8.2.1  Assets

| Asset | Why It Matters |
|---|---|
| Dataset integrity | The platform's entire value proposition (Ch.2 §2.1) collapses if entries cannot be trusted as genuine |
| Curator and Researcher identity | Falsified attribution undermines Human Accountability (Ch.2 §2.9) |
| Governance and administrative control | Capture of `Administrator` privileges could compromise the funder-independence guarantee (Ch.2 §2.9) |
| Availability of the public registry | Downtime directly undermines the infrastructure mission (Ch.2 §2.1) |
| Contributor trust and platform reputation | A negative-results registry that loses trust re-creates the exact problem it exists to solve (Chapter 2 §2.0) |
| Federation network integrity | A compromised node could inject false data across the entire federated dataset (Ch.4 §4.12) |

#### 8.2.2  Actors and Adversary Classes

| Actor Class | Motivation | Representative Threat |
|---|---|---|
| Opportunistic attacker | Low-effort disruption, credential theft, spam | Automated submission flooding; credential-stuffing against Authentication Service |
| Malicious contributor | Insert false or misleading "negative results" (e.g., to discredit a real, effective intervention) | Crafted submissions designed to pass schema validation while containing fabricated content |
| Compromised legitimate account | An attacker who has taken over a real curator's credentials | Approval of fabricated entries with an apparently legitimate accountable curator |
| Malicious or compromised federation node | Inject falsified data at network scale (Ch.4 §4.12) | Signed-but-false sync messages from a node whose signing key has been compromised |
| Supply-chain attacker | Compromise the codebase itself, given its public, contribution-accepting nature | A malicious dependency or a compromised CI/CD pipeline step (§8.8) |
| Insider (privileged) | Abuse of `Administrator` or `Curation Lead` privileges | Unauthorized data manipulation or governance-rule circumvention |
| Nation-state / advanced actor | Long-horizon reputational or scientific-integrity attack against a public-good research infrastructure | Patient, low-and-slow campaigns — the class this platform's twenty-year horizon (Ch.2 §2.2) is most exposed to and least resembles a typical commercial threat model |

#### 8.2.3  STRIDE Analysis (Representative Flows)

**Flow: Submission → Curation → Publication (Ch.3 §3.3)**

| STRIDE Category | Threat | Mitigation |
|---|---|---|
| **S**poofing | An attacker submits under a falsified ORCID | ORCID identity is OIDC-verified at authentication (Ch.4 §4.6), not self-asserted in the submission payload |
| **T**ampering | A submission is altered in transit or at rest between validation and curator review | Immutable, versioned submission records (Ch.5 §5.3.1); TLS in transit (§8.6); integrity checksums on stored objects |
| **R**epudiation | A curator later denies having approved a specific entry | Every Review is non-repudiably attributed (Ch.5 §5.3.2, Ch.2 §2.9); Audit Service (Ch.4 §4.16) is append-only |
| **I**nformation disclosure | Contact information or other non-public submission fields leak | Field-level access control distinguishing public entry data from curator-only submission metadata (§8.4.3) |
| **D**enial of service | Automated submission flooding exhausts curator review capacity | Rate limiting (Ch.7 §7.8) at the channel level, before entries ever reach the human curation queue |
| **E**levation of privilege | A `Contributor`-scoped token is used to act as `Curator` | Server-side scope re-verification at every service (§8.1, least privilege), never trusting a client-asserted role |

**Flow: Federation Synchronization (Ch.4 §4.12)**

| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Spoofing | A rogue actor impersonates a legitimate federation node | Mutual TLS + cryptographic node identity verification (§8.10) |
| Tampering | A sync message is altered in transit between nodes | HMAC/digital-signature verification on every sync message (Ch.4 §4.12, restated §8.10) |
| Repudiation | A node denies having propagated a false entry | Every synchronized entry retains unambiguous originating-node attribution (Ch.2 §2.9, Ch.4 §4.12) |
| Elevation of privilege | A compromised node attempts to push administrative or governance-affecting data through the sync channel | Sync channel scope is structurally limited to entry/metadata propagation; no governance or role-management data is ever accepted via federation sync (§8.10) |

**Flow: AI-Assisted Curation (Ch.4 §4.5)**

| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Tampering | Adversarial input designed to manipulate an AI classification/entity-linking suggestion | AI output is never auto-applied (Ch.2 §2.9); a manipulated suggestion can mislead a curator but cannot itself alter the dataset |
| Information disclosure | A prompt-injection payload embedded in submitted free text attempts to exfiltrate other entries' data via the AI Service's context | AI Service inference is scoped per-request with no persistent cross-submission memory; output is logged and auditable (§8.9) |

---

### 8.3  Data Classification

| Classification | Examples | Handling Rule |
|---|---|---|
| **Public** | Published entries, metadata, ontology terms, aggregate analytics | Open Science First default (Ch.2 §2.3.5); no authentication required to read |
| **Internal** | Curation-queue state, inter-curator discussion notes, unpublished submission drafts | Visible to `Curator`/`Curation Lead`/`Administrator` roles only |
| **Restricted** | Contributor contact information (optional field), audit logs, system configuration | Visible only to the specific accountable role (e.g., a curator's own assigned queue) or `Administrator` |
| **Prohibited** | Patient-identifiable information of any kind | Never a representable state in the schema (Ch.2 §2.3.6); rejected structurally, not merely by policy |

**Enforcement is layered, not singular** (§8.1's defense-in-depth principle): the JSON Schema itself contains no patient-identifier fields (structural prevention); the curation checklist requires an explicit identifier screen (Ch.4 §4.8, procedural prevention); and a `FUTURE` automated PII-pattern scanner is planned as a third, independent layer at the Submission Service (Ch.4 §4.1) — three controls, so that no single control's gap constitutes a Prohibited-classification breach.

---

### 8.4  Identity and Access Management

#### 8.4.1  Roles and Permission Matrix

| Role | Grants | MFA Required |
|---|---|---|
| `Anonymous` | Read public data; submit via no-Git path | No |
| `Contributor` | Submit via any channel; view own submission status | No (recommended) |
| `Curator` (domain-scoped) | Review/approve/reject submissions in assigned domain(s) | **Yes** |
| `Curation Lead` | All Curator permissions across all domains; ontology change proposal; curator assignment | **Yes** |
| `Administrator` | User/role management; system configuration; dataset release trigger; backup restoration (dual-auth) | **Yes**, plus hardware-key-backed authentication recommended |
| `System Account` | Scoped, service-specific permissions (e.g., Import Service's submission-creation scope) | N/A (key-based service auth, §8.6.2) |
| `Federation Node` | Sync-channel access only, no administrative scope | Mutual TLS + signing key (§8.10) |

#### 8.4.2  Session and Token Management

- Access tokens: short-lived JWTs (target: 15-minute expiry), per Ch.4 §4.6.
- Refresh tokens: longer-lived, revocable, bound to a specific client/device fingerprint to limit the blast radius of a stolen refresh token.
- Every privileged role (`Curator` and above) session is logged to the Audit Service (Ch.4 §4.16) at login, not only at consequential action time — session-level visibility matters for incident investigation even absent a specific flagged action.

#### 8.4.3  Field-Level Access Control

Not every field on a Submission (Ch.5 §5.3.1) is Public-classified even after the parent entry is published: `contact_email_optional` and any internal curator notes remain Restricted regardless of the entry's own publication state — access control in this platform is applied at the field level, not only the resource level, precisely because a single Submission record spans multiple data classifications (§8.3) simultaneously.

#### 8.4.4  Dual Authorization for Destructive or Governance-Critical Actions

Per Ch.4 §4.18 (Backup restoration) and §4.19 (Administration), extended here as a general security architecture rule: any action that is destructive (data restoration, bulk deletion), irreversible at the governance level (role grant to `Administrator`), or capable of altering the funder-independence guarantee (Ch.2 §2.9) requires two independent `Administrator` approvals, logged separately, before execution. A single compromised or coerced administrator credential is, by this rule, structurally insufficient to perform the platform's highest-impact actions.

---

### 8.5  Application Security

| Control | Applied Where |
|---|---|
| Input validation at every trust boundary | Submission Service schema validation (Ch.4 §4.1) as the primary example; identically applied at every other write path per Zero Trust (§8.1) |
| Parameterized queries / ORM-enforced query construction | All Storage Layer access (Ch.3 §3.8), preventing injection regardless of which service or language implements a given data access |
| Dependency vulnerability scanning | Automated, on every CI run, across all services — extending the existing `test-suite.yml` CI pipeline (Ch.3 §3.2) with a dedicated security-scanning step |
| Static Application Security Testing (SAST) | `PLANNED`, integrated into CI for every service as it moves from `PLANNED` to implementation, gating merge on no newly introduced high-severity findings |
| Dynamic Application Security Testing (DAST) | `PLANNED`, run against staging deployments prior to each API version release (Ch.7 §7.2) |
| Secure coding standard | A documented, mandatory checklist for every new service implementation, covering (at minimum) the OWASP Top 10 categories as they apply to this platform's specific architecture |

---

### 8.6  Data Protection

#### 8.6.1  Encryption

- **In transit.** TLS 1.3 minimum for every external connection (API Gateway, web portal, federation sync); mutual TLS specifically for federation node-to-node traffic (§8.10).
- **At rest.** Encryption at rest for every Storage Layer technology in Chapter 3 §3.8 — PostgreSQL, object storage, the graph store, and the vector database alike — with encryption keys managed independently of the data they protect (§8.6.2).
- **Backups.** Encrypted independently of the primary data store's own encryption, per Chapter 4 §4.18's security posture, so that a compromise of the primary environment's keys does not automatically compromise backup confidentiality.

#### 8.6.2  Secrets and Key Management

All credentials, signing keys, and API keys (Zenodo/DataCite registration credentials, federation node signing keys, external-source API credentials for the Import Service) are held in a dedicated secrets-management system, never in application configuration files or source control — a deliberately unglamorous but load-bearing control, since the majority of real-world breaches of comparable open-source infrastructure trace to exactly this failure mode (a credential committed to a public repository). Per the Cloud Agnostic principle (Ch.2 §2.3.9), the secrets-management approach is specified as a capability (encrypted, access-controlled, audit-logged secret storage) rather than tied to one vendor's specific product.

#### 8.6.3  PII Prevention Enforcement Mechanisms

Directly extending §8.3's layered enforcement: (1) schema-level structural exclusion, (2) curator checklist screening, (3) `FUTURE` automated pattern-based scanning at submission time, and (4) periodic retrospective audit sampling of the published dataset — a fourth, independent, lower-frequency control specifically because layers 1–3 all operate at submission time, and a defense-in-depth posture benefits from at least one control that operates independently of the submission pipeline entirely.

---

### 8.7  Network Security

- **API Gateway as the sole external-facing boundary** (Ch.3 §3.1): no backing service (Ch.4 §4.1–§4.19) is directly reachable from outside the platform's internal network — every request, including those from the first-party web portal, transits the Gateway.
- **Web Application Firewall (WAF)**, `PLANNED`, positioned at the Gateway to filter common attack patterns before they reach application logic.
- **DDoS mitigation**, `PLANNED`, layered with the rate-limiting scheme already specified in Chapter 7 §7.8 — rate limiting protects against sustained abuse by authenticated or identifiable clients; DDoS mitigation specifically addresses high-volume, potentially distributed, often unauthenticated traffic.
- **Network segmentation.** The Storage Layer (Ch.3 §3.8) is never directly network-reachable from outside the Infrastructure Layer (Ch.3 §3.2) — a violation of this segmentation would itself be a layering-discipline violation independent of any specific attack, since Chapter 3 §3.2 already forbids the Domain Layer from depending on Storage directly, let alone an external actor.

---

### 8.8  Supply Chain Security

This section addresses a threat surface most enterprise security architectures do not need to specify in this much depth, because most enterprise software is not built as public, contribution-accepting open source. This platform is (Ch.2 §2.3.5), which means its supply chain is, by design, more open than a closed-source system's — and its security architecture must compensate deliberately rather than relying on obscurity it has intentionally forfeited.

| Control | Description | Status |
|---|---|---|
| Dependency pinning | Every dependency version-pinned, not floating, across every service | `OPERATIONAL` (current Python tooling) / `PLANNED` (platform-wide as new services are implemented) |
| Software Bill of Materials (SBOM) | Generated automatically for every release, per service | `PLANNED` |
| Signed commits and releases | Required for any commit or release touching validation logic, the schema, or the curation workflow — the components whose compromise most directly threatens dataset integrity (§8.2.1) | `PLANNED` |
| CI/CD pipeline hardening | GitHub Actions workflows (Ch.3 §3.2) run with minimum required permissions (`permissions:` block scoped per-workflow, never a blanket `write-all`); secrets scoped to only the workflow steps that require them | `PLANNED` (current workflows reviewed and scoped as part of this chapter's adoption) |
| Third-party contribution review | Every code contribution (as distinct from a data Submission, Ch.4 §4.1) from an external contributor undergoes mandatory maintainer review before merge — no auto-merge path exists for code, ever, regardless of how minor the change appears | `OPERATIONAL` (standard GitHub branch-protection practice) |
| Reproducible builds | `FUTURE` — a longer-horizon goal ensuring a published release artifact can be independently verified to correspond exactly to its claimed source | `FUTURE` |

---

### 8.9  AI-Specific Security Considerations

Extending Chapter 4 §4.5's Zero Trust posture on AI output to full threat-model depth:

- **Prompt injection.** Free-text fields in a Submission (hypothesis statement, outcome narrative) are untrusted input to any future AI Service inference call (Ch.4 §4.5); the AI Service's system prompts and inference pipeline are designed so that content within a submission's free-text fields cannot alter the AI Service's own instructions or access scope, consistent with standard prompt-injection defense practice.
- **Data poisoning.** A pattern of coordinated, subtly falsified submissions designed specifically to bias a future embedding or classification model is a longer-horizon risk this platform's human-curation-gate design (Ch.2 §2.9) directly mitigates — no AI training or fine-tuning process is permitted to run against unreviewed submission data, only against the curator-approved published dataset.
- **Model output as a decision input, never a decision.** Restated from Ch.4 §4.5 and Ch.2 §2.9 because it is the single most important AI-security control in this architecture: an AI Service suggestion carries a confidence score and is logged, but it is never the entity that changes the canonical dataset's state — a human Review (Ch.5 §5.3.2) always is.

---

### 8.10  Federation Security (Detailed)

Extending Chapter 4 §4.12's design constraints to implementation-level specification:

1. **Node onboarding.** A new Federation Node is admitted to the network only through a governance-reviewed process (mirroring Ch.6 §6.5's term-lifecycle governance pattern), not a self-service registration — federation membership is itself a trust decision, not merely a technical handshake.
2. **Cryptographic identity.** Each node holds a unique signing keypair; the public key is registered in the `federation_nodes` table (Ch.4 §4.12) at onboarding and used to verify every subsequent sync message from that node.
3. **Mutual TLS** for the transport layer, independent of and in addition to message-level signature verification — a compromised TLS certificate alone is insufficient to forge a valid sync message, and a compromised signing key alone does not grant network-level access without also compromising the TLS layer.
4. **Scope-limited sync channel.** As noted in §8.2.3's STRIDE analysis, the federation sync channel structurally accepts only entry and metadata propagation — no administrative, role-management, or governance data type is ever a valid payload on this channel, closing off an entire class of elevation-of-privilege attack via a compromised node.
5. **Node revocation.** A compromised or misbehaving node's public key is revoked from the trust registry; all subsequent sync messages purportedly from that node are rejected; already-synchronized data from the compromised node prior to revocation is flagged for governance review rather than automatically purged, since automatic mass deletion is itself a destructive action subject to the dual-authorization rule (§8.4.4).

---

### 8.11  Incident Response

```
Detection
   (Monitoring Service alert, Ch.4 §4.17; external report; audit anomaly)
      |
      v
Triage & Severity Classification
   (Critical / High / Medium / Low — per the table below)
      |
      v
Containment
   (revoke compromised credentials/keys; isolate affected service;
    for federation incidents, revoke the affected node per §8.10.5)
      |
      v
Investigation
   (Audit Service, Ch.4 §4.16, as the primary evidence source —
    the reason every consequential action is non-repudiably logged)
      |
      v
Remediation
   (patch, credential rotation, dataset correction via a new
    versioned release if published data was affected — never a
    silent edit, per Ch.2 §2.9)
      |
      v
Disclosure
   (per §8.12's responsible-disclosure policy; public post-mortem
    for any incident affecting published data integrity, consistent
    with the Transparency principle, Ch.2 §2.9)
      |
      v
Post-Incident Review
   (governance-level review of whether this chapter's controls
    require revision — an incident is itself an input to this
    document's own change-control process, Ch.2 §2.6)
```

**Severity classification.**

| Severity | Example | Response Target |
|---|---|---|
| Critical | Dataset integrity compromised at scale; Administrator credential compromise | Immediate containment; public disclosure within 72 hours of confirmation |
| High | Single-entry falsification confirmed; individual curator account compromise | Containment within 24 hours; affected entries flagged pending correction |
| Medium | Federation node anomaly short of confirmed compromise; suspicious but unconfirmed submission pattern | Investigation within 5 business days |
| Low | Isolated failed-login patterns; minor dependency vulnerability with no known exploitation path | Standard patch/remediation cycle |

---

### 8.12  Vulnerability Management and Responsible Disclosure

Consistent with the platform's open-source nature, a public `SECURITY.md` policy (`PLANNED`) commits to: a dedicated, monitored reporting channel for security researchers, distinct from the general issue tracker; acknowledgment of a report within 5 business days; a coordinated disclosure timeline (target: 90 days, negotiable for complex issues) before public disclosure; and explicit good-faith safe-harbor language for researchers testing within the policy's defined scope. This is treated as a governance commitment on par with the funder-independence rule (Ch.2 §2.9) — a project asking institutional partners and funders to trust its data-integrity claims (Ch.2 §2.1) must be equally rigorous about how it handles being told, by an outsider, that something is wrong.

---

### 8.13  Compliance and Regulatory Alignment

**What does *not* apply, and why — stated plainly rather than glossed over.** Because the platform structurally excludes patient-identifiable data (Ch.2 §2.3.6, §8.3), it does not itself become a HIPAA-covered entity or business associate, and GDPR's special-category (health) data provisions do not attach to the dataset it publishes. This is a deliberate architectural choice, not an oversight or a loophole — the platform achieves its scientific mission (aggregate, study-level negative results) without ever needing individual-level health data in the first place.

**What does apply.** General GDPR obligations still attach to the platform's own operational data about EU-resident users — account information, IP-address-level access logs — handled per standard controller obligations (data minimization, right to erasure for account data specifically, distinct from the immutable published dataset per Ch.2 §2.9, which is public-domain scientific record rather than personal data once properly de-identified at the study level). Institutional partners remain independently responsible for their own regulatory compliance (their own IRB/ethics-committee clearance to share a given finding, their own funder data-sharing-policy compliance) — the platform's role, per its funding case, is to make that compliance easier, not to assume it on the partner's behalf.

---

### 8.14  Security Quality Scenarios (ATAM-style, extending Ch.3 §3.15)

**Confidentiality.** *Stimulus:* an attacker attempts to access curator-only internal notes on a Submission via a crafted API request. *Response:* field-level access control (§8.4.3) rejects the request at the API Gateway layer before it reaches the Metadata Service, independent of whether the entry itself is published. *Response Measure:* zero Restricted-classification field exposure in penetration-testing coverage, verified prior to each major release.

**Integrity.** *Stimulus:* an attacker with a compromised `Curator` credential attempts to approve a fabricated entry. *Response:* the action succeeds technically (the credential is valid) but is fully attributed and logged (§8.4.2, Ch.2 §2.9); anomaly detection (unusual approval velocity, domain mismatch from the curator's normal assignment) flags it for review; correction, once confirmed, occurs via a new versioned release, never a silent edit. *Response Measure:* time-to-detection for an anomalous approval pattern, tracked as an Analytics Service (Ch.4 §4.11) metric.

**Availability under attack.** *Stimulus:* a volumetric DDoS attack targets the public search endpoint. *Response:* the static-index fallback (Ch.3 §3.12) continues serving cached search results at the CDN edge even if the live Search Service backend is degraded — the same resilience property Chapter 3 identified for ordinary infrastructure failure applies equally to an adversarial denial-of-service scenario. *Response Measure:* public search availability maintained above a defined SLA threshold during a simulated volumetric attack, verified by periodic chaos/security testing.

**Non-repudiation.** *Stimulus:* a governance dispute arises over who approved a specific, now-contested entry two years prior. *Response:* the Audit Service's immutable log (Ch.4 §4.16) and the Review entity's permanent curator attribution (Ch.5 §5.3.2) together provide a verifiable answer without depending on any individual's memory or good faith. *Response Measure:* every published entry's full approval provenance is reconstructable from the audit trail alone, verified as part of the platform's standard governance-audit cycle.

---

### 8.15  Implementation Status Summary

| Control Area | Status |
|---|---|
| Zero Trust validation at every write path | `OPERATIONAL` (Submission Service today) / `PLANNED` (platform-wide as services move off `OPERATIONAL`-as-script status) |
| PII structural exclusion (schema-level) | `OPERATIONAL` |
| MFA for privileged roles | `PLANNED` (no live Authentication Service yet, Ch.4 §4.6) |
| Dual authorization for destructive actions | `PLANNED` |
| Encryption at rest/in transit | `PLANNED` (no live networked services yet requiring it beyond standard GitHub/HTTPS transport) |
| Secrets management | `PLANNED` |
| SAST/DAST in CI | `PLANNED` |
| SBOM, signed commits/releases | `PLANNED` |
| Federation node security model | `FUTURE` (Federation Service itself is `FUTURE`, Ch.4 §4.12) |
| Incident response process | `PLANNED` — documented here; not yet operationally tested via drill |
| Responsible disclosure policy (`SECURITY.md`) | `PLANNED` |

---

### 8.16  Summary and Handoff

This chapter has specified security not as an afterthought but as the load-bearing counterpart to the trust claims made throughout this entire series — a Zero Trust posture applied at implementation depth, a threat model specific to a negative-results registry's actual highest-value asset (dataset integrity, not confidential data), and a supply-chain security posture proportional to the platform's deliberate choice to be open and contribution-accepting rather than closed. The Deployment Architecture chapter's task is to specify exactly how these controls — the API Gateway boundary, the secrets management system, the encryption requirements, the CI/CD hardening — are realized in a concrete, staged infrastructure deployment, building directly on Chapter 3 §3.10's scaling stages and this chapter's requirement that every control be specified as a technology-independent guarantee (Ch.2 §2.8) rather than tied to one vendor's product from the outset.
