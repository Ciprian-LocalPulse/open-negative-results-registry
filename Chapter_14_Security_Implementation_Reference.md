# Dark Data Medicine — Platform Architecture Series

## Chapter 14: Security Implementation Reference

*Document status: Normative / Reference. Explicitly downstream of Chapter 8 (Security Architecture), the same relationship Chapter 13 holds to Chapter 9. Chapter 8 specified the threat model, principles, and controls at three representative flows; this chapter provides the concrete policy-as-code artifacts and completes the STRIDE analysis across all nineteen Chapter 4 services rather than a representative subset.*

*Version 0.1 — Draft for governance review*

---

### 14.0  Relationship to Chapter 8

Chapter 8 answered *what* must be true (Zero Trust, least privilege, dual authorization) and *why* (a threat model specific to dataset-integrity risk, not confidential-data risk). This chapter answers *how it is encoded* — the actual RBAC policy document, the actual network policy, the actual per-service threat table Chapter 8 sampled from three flows. Nothing here introduces a new principle; everything here is an artifact a security engineer would actually author, review, and check into version control.

---

### 14.1  Complete Per-Service STRIDE Analysis

Chapter 8 §8.2.3 analyzed three representative flows (submission/curation, federation sync, AI-assisted curation). This section completes the analysis across the remaining sixteen Chapter 4 services, at the same rigor, so that no service in the platform lacks a documented threat analysis.

| Service (Ch.4 ref) | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation of Privilege |
|---|---|---|---|---|---|---|
| Metadata (§4.2) | N/A — event-triggered, no external identity to spoof | Metadata record altered post-generation | Mitigated: event-sourced, re-derivable from source Submission | Public by design (Ch.2 §2.3.5); risk only in premature exposure before curator approval | Export endpoint flooding | N/A — no privileged write path |
| Search (§4.3) | N/A — public read | Index poisoned via a compromised upstream Metadata record | N/A — read-only | None (public data only) | Query flooding (§7.8 rate limits) | N/A |
| Knowledge Graph (§4.4) | Spoofed entity-linking via compromised AI Service output | Graph edge injected without legitimate provenance | Mitigated: every edge traces to a `MetadataGenerated` event | Graph traversal could reveal unpublished entry existence if not scoped to published data only | Expensive traversal-query flooding | Unauthorized edge creation bypassing Review Service |
| Authentication (§4.6) | Credential stuffing, ORCID token replay | Session/token tampering | Mitigated: every auth event logged (Ch.8 §8.4.2) | Token leakage via improper storage/transport | Login endpoint flooding | Privilege escalation via role-claim tampering in a forged token |
| Notification (§4.7) | Spoofed sender on outbound email | Notification content altered in transit | N/A — delivery receipts logged | Entry content leaked via a notification channel weaker than the API (Ch.8 §8.6.1) | Notification-bombing a user | N/A |
| DOI (§4.9) | Spoofed release-trigger request | Release metadata altered before Zenodo submission | Mitigated: release-trigger requires attributed `admin:write` | Premature disclosure of an unpublished release's DOI | N/A (low-frequency operation) | Unauthorized release trigger — mitigated by role restriction |
| Replication (§4.10) | Spoofed replication attribution | Replication result altered post-recording | Mitigated: routed through standard Review Service | None beyond standard entry disclosure rules | N/A | N/A — same path as standard submission |
| Analytics (§4.11) | N/A — internal consumer | Metric tampering could mask an ongoing incident | Mitigated: metrics are derived, re-computable | Internal dashboards exposing operational detail publicly (Ch.8 §8.4.3) | Dashboard query flooding | Unauthorized access to internal/funder-specific reports |
| Ontology (§4.13) | Spoofed vocabulary-change proposal | Term definition altered without governance review | Mitigated: governance review required, logged (Ch.6 §6.5) | N/A — public by design | N/A | Unauthorized term publication bypassing governance |
| Export (§4.14) | N/A — public/authenticated read | N/A — read-only, derived data | Export events logged for audit | Bulk export exposing Restricted-classification fields if scoping is misconfigured (Ch.8 §8.3) | Large-export resource exhaustion | N/A |
| Import (§4.15) | Spoofed external-source data | Draft submission altered before reaching curation | Mitigated: system-account attribution (Ch.4 §4.15) | External API credentials leaked | External-source API quota exhaustion | Import job bypassing standard curation queue |
| Audit (§4.16) | N/A — internal, universal subscriber | **Highest-severity target**: tampering with the audit log itself undermines every other control's evidentiary value | N/A by design (this service exists to prevent repudiation elsewhere) | Audit log access itself must be logged (Ch.8 §8.4, self-referential control) | Log-write flooding degrading write latency for legitimate events | Unauthorized audit-log deletion — mitigated by append-only enforcement |
| Monitoring (§4.17) | Spoofed health-check results masking a real incident | Alert-threshold tampering to suppress legitimate alerts | Alert history logged | Internal diagnostic detail exposed publicly | Alerting system itself DoS'd during an actual incident (worst-case compounding failure) | Unauthorized access to detailed service health |
| Backup (§4.18) | N/A — internal scheduled process | Backup artifact tampered with pre- or post-encryption | Restoration test results logged | Backup artifact exposure if encryption (Ch.8 §8.6.1) is misconfigured | Backup job resource contention with production workload | Unauthorized restoration — mitigated by dual authorization (Ch.8 §8.4.4) |
| Administration (§4.19) | Spoofed administrative request | Configuration tampering | Mitigated: every action logged without exception (Ch.4 §4.19) | System configuration disclosure | N/A (low-frequency, privileged-only) | **Highest-severity target**: this service's own elevation-of-privilege risk is why dual authorization exists at all |
| Federation (§4.12) | *(Fully covered in Ch.8 §8.2.3 and §8.10 — not repeated here)* | | | | | |

**Reading this table.** Two services — Audit (§4.16) and Administration (§4.19) — are flagged as the highest-severity targets in the entire platform, and this is not incidental: they are, respectively, the service that makes every other control's evidence trustworthy and the service with the platform's broadest privilege surface. Any security review prioritizing limited engineering time (Chapter 11 §11.10's quarterly governance cadence) should weight these two services above the others in this table by default.

---

### 14.2  RBAC Policy as Code

Concrete implementation of the permission matrix in Chapter 8 §8.4.1:

```yaml
# rbac-policy.yaml — the canonical, version-controlled source of truth
# for every role's grants (Ch.8 §8.4.1), consumed by the Authentication
# Service (Ch.4 §4.6) and enforced independently by every other service
# per the least-privilege principle (Ch.8 §8.1)

roles:
  anonymous:
    grants: ["entries:read", "search:read", "ontology:read", "submit:write:no-git"]
    mfa_required: false

  contributor:
    grants: ["entries:read", "search:read", "ontology:read", "submit:write", "submission:read:own"]
    mfa_required: false

  curator:
    inherits: contributor
    grants: ["review:read:assigned-domain", "review:write:assigned-domain"]
    mfa_required: true
    scope: domain   # enforced per-domain, not global — Ch.4 §4.8

  curation_lead:
    inherits: curator
    grants: ["review:write:all-domains", "ontology:propose", "curator:assign"]
    mfa_required: true
    scope: global

  administrator:
    inherits: curation_lead
    grants: ["admin:*", "backup:restore", "release:trigger", "user:manage"]
    mfa_required: true
    mfa_method: hardware_key_recommended
    dual_authorization_required_for: ["backup:restore", "user:role-grant:administrator", "release:trigger"]

  system_account:
    grants: []  # explicitly scoped per-account, never a default grant set —
                # e.g., import-service account gets only ["submit:write:system"]
    mfa_required: false
    auth_method: signed_service_token

  federation_node:
    grants: ["federation:sync"]
    auth_method: mutual_tls + signing_key
```

**Enforcement note.** This policy file is the source of truth, but — per Chapter 8 §8.1's least-privilege principle — every service independently re-validates a caller's grants against its own required scope rather than trusting a single upstream check; the API Gateway checking `submit:write` does not exempt the Submission Service from checking it again.

---

### 14.3  Network Policy (Kubernetes, Stage 3+)

Operationalizing Chapter 8 §8.7's network segmentation requirement:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: storage-layer-isolation }
spec:
  podSelector: { matchLabels: { ddm-layer: storage } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector: { matchLabels: { ddm-layer: infrastructure } }
      # No other layer (presentation, api, application, domain) may
      # reach the storage layer directly — Ch.3 §3.2's layering
      # discipline enforced at the network level, not only by
      # code-review convention
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  # Default-deny baseline (Zero Trust, Ch.2 §2.3.7, applied at the
  # network layer) — every legitimate path is an explicit allow rule
  # layered on top of this, never an implicit one
```

---

### 14.4  Secrets Management Configuration Pattern

```yaml
# External Secrets Operator pattern (or equivalent, per Ch.2 §2.8
# Technology Independence — any conformant secrets-manager integration
# satisfies this contract)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: auth-service-secrets }
spec:
  secretStoreRef: { name: ddm-secrets-store, kind: SecretStore }
  target: { name: auth-service-secrets }
  data:
    - secretKey: orcid-client-secret
      remoteRef: { key: "ddm/production/orcid-client-secret" }
    - secretKey: jwt-signing-key
      remoteRef: { key: "ddm/production/jwt-signing-key" }
```

No secret value ever appears in a Kubernetes manifest, a Dockerfile, or the infrastructure-as-code repository (Chapter 13 §13.6) — only a *reference* to where the secrets-management system holds it, satisfying Chapter 8 §8.6.2 concretely.

---

### 14.5  Dual-Authorization Implementation Pattern

Operationalizing Chapter 8 §8.4.4:

```
POST /v1/backup/restore
      |
      v
Request recorded as PENDING_APPROVAL, not executed
      |
      v
Notification sent to all Administrators except the requester
      |
      v
A second, distinct Administrator calls
   POST /v1/backup/restore/{requestId}/approve
      |
      v
Only once a second, different Administrator's approval is recorded:
   execution proceeds
      |
      v
Both approvals permanently logged to Audit Service (Ch.4 §4.16),
   including any case where the same individual attempts to approve
   their own request (rejected, logged as a policy-violation attempt
   in itself — a signal worth security review even though no actual
   restoration occurred)
```

---

### 14.6  Vulnerability Scanning Pipeline Configuration

Extending Chapter 8 §8.5 and Chapter 9 §9.4's CI stages with a concrete pipeline step:

```yaml
# .github/workflows/security-scan.yml (structure, PLANNED)
name: Security Scan
on: [pull_request, schedule]
jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency vulnerability scan
        run: pip-audit -r requirements.txt --fail-on high
      - name: SAST
        uses: github/codeql-action/analyze@v3
      - name: Secret scan
        run: trufflehog filesystem . --fail
      - name: Container image scan (for services with a Dockerfile)
        run: trivy image --exit-code 1 --severity HIGH,CRITICAL ${{ env.IMAGE_TAG }}
```

A high- or critical-severity finding in any of these steps fails the CI pipeline (Chapter 9 §9.4), meaning a vulnerable dependency or an accidentally committed secret cannot reach the merge-to-main step regardless of how the code review itself goes.

---

### 14.7  Implementation Status Summary

| Artifact | Status |
|---|---|
| Full per-service STRIDE table (§14.1) | `PLANNED` (analysis complete as documentation; not yet validated by live penetration testing) |
| RBAC policy file (§14.2) | `PLANNED` |
| Network policies (§14.3) | `PLANNED`, requires Stage 3 (Kubernetes) |
| Secrets management integration (§14.4) | `PLANNED` |
| Dual-authorization workflow (§14.5) | `PLANNED` |
| Automated security-scan CI pipeline (§14.6) | `PLANNED` |

---

### 14.8  Summary

This chapter completed Chapter 8's threat analysis across every one of the nineteen Chapter 4 services and converted its principles into version-controllable artifacts: an RBAC policy file, Kubernetes network policies, a secrets-reference pattern, a dual-authorization state machine, and an automated scanning pipeline. Combined with Chapter 13, the deployment and security architectures specified narratively in Chapters 8–9 now have a complete, concrete implementation counterpart. Chapter 15's task — Testing Architecture — is to specify how every artifact across this entire series, from the Domain Model's entities to this chapter's RBAC policy, is actually verified before it is trusted.
