# Dark Data Medicine — Platform Architecture Series

## Chapter 13: Deployment Implementation Reference

*Document status: Normative / Reference. This chapter is explicitly downstream of Chapter 9 (Deployment Architecture), not a replacement for it. Chapter 9 specified the staged topology and the *why* behind each infrastructure decision; this chapter provides the concrete, runnable artifacts — Infrastructure-as-Code definitions, container specifications, CI/CD pipeline definitions — that realize each of Chapter 9's five stages. Where Chapter 9 says "declaratively defined," this chapter shows the declaration.*

*Version 0.1 — Draft for governance review*

---

### 13.0  Relationship to Chapter 9

A reader should come to this chapter already knowing *why* Stage 2 introduces containerization and *why* Stage 4 requires mutual TLS between federation nodes (Chapter 9 §9.2). This chapter does not re-argue those decisions. It answers the question Chapter 9 deliberately left at the diagram level: what does the actual file look like? Every artifact below is written to be directly usable — copied into the repository, adapted with environment-specific values, and run — not illustrative pseudocode.

**Status discipline, restated.** Every artifact below is `PLANNED` unless marked otherwise, exactly as its corresponding Chapter 9 stage is. Writing the Terraform module now, ahead of Stage 2's actual infrastructure need, is itself consistent with this series' practice (Chapter 10 §10.6) of specifying a component fully before implementation begins, so that implementation is "write the code the spec already describes," not "figure out the spec while writing the code."

---

### 13.1  Stage 1 Artifacts (`OPERATIONAL` — the only fully real section of this chapter)

The three GitHub Actions workflows referenced throughout this series are the actual, current infrastructure. Their structure, in outline (full source is reproduced in the platform's funding case, Appendix Q):

```yaml
# .github/workflows/validate-submissions.yml (structure)
name: Validate Submissions
on:
  pull_request:
    paths: ['data/**/*.json']
jobs:
  validate:
    runs-on: ubuntu-latest
    permissions:
      contents: read          # Ch.8 §8.8 — minimum required permissions,
      pull-requests: write    #   scoped per-workflow, never write-all
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: python scripts/validate_submission.py --changed-files
```

This is the entirety of Stage 1's "deployment infrastructure" — no servers, no orchestration, no secrets beyond GitHub's own token scoping. It is reproduced here specifically so a reader comparing this chapter's later, more elaborate stages does not lose sight of how much real, production value the simplest possible stage already delivers.

---

### 13.2  Stage 2 Artifacts: Containerization

#### 13.2.1  Dockerfile Pattern (applied uniformly across Chapter 4's services)

```dockerfile
# Applies to any Ch.4 service — shown for the Submission Service
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Non-root user — Ch.8 §8.5's secure-coding standard applied at the
# container layer, not only the application layer
RUN useradd --create-home appuser
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["python", "-m", "submission_service"]
```

Every service defined in Chapter 4 follows this identical pattern — a deliberate consistency choice (Chapter 2 §2.11, "prefer interoperability over local optimization") so that a new service's Dockerfile is a known quantity for any engineer already familiar with any other service's.

#### 13.2.2  Local Orchestration (`docker-compose.yml`, structure)

```yaml
version: "3.9"
services:
  api-gateway:
    build: ./services/gateway
    ports: ["8080:8080"]
    depends_on: [submission-service, auth-service]
  submission-service:
    build: ./services/submission
    environment:
      - DATABASE_URL=postgresql://ddm:${DB_PASSWORD}@postgres:5432/ddm
    depends_on: [postgres]
  auth-service:
    build: ./services/auth
    environment:
      - ORCID_CLIENT_ID=${ORCID_CLIENT_ID}   # from local .env, never committed —
      - ORCID_CLIENT_SECRET=${ORCID_CLIENT_SECRET}  # Ch.8 §8.6.2, Ch.9 §9.6
  postgres:
    image: postgres:16-alpine
    environment: [POSTGRES_DB=ddm, POSTGRES_USER=ddm]
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

This is the artifact Chapter 10 §10.1 anticipates as the "target-state setup" a new developer will eventually run locally — a single `docker-compose up` bringing up the full Stage 2 topology from Chapter 9 §9.2.2 on a laptop.

---

### 13.3  Stage 3 Artifacts: Kubernetes

#### 13.3.1  Deployment Manifest Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: search-service
  labels: { app: search-service, ddm-layer: application }
spec:
  replicas: 3   # baseline; HorizontalPodAutoscaler adjusts per Ch.9 §9.5
  selector: { matchLabels: { app: search-service } }
  template:
    metadata: { labels: { app: search-service } }
    spec:
      containers:
        - name: search-service
          image: ghcr.io/darkdatamedicine/search-service:{{ .Version }}
          ports: [{ containerPort: 8080 }]
          resources:
            requests: { cpu: "250m", memory: "256Mi" }
            limits: { cpu: "1", memory: "1Gi" }
          readinessProbe:
            httpGet: { path: /health, port: 8080 }
            initialDelaySeconds: 5
          livenessProbe:
            httpGet: { path: /health, port: 8080 }
            initialDelaySeconds: 15
          env:
            - name: OPENSEARCH_URL
              valueFrom: { secretKeyRef: { name: search-secrets, key: opensearch-url } }
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: search-service-hpa }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: search-service }
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
```

**Resource sizing rationale.** Requests/limits are set per-service based on the specific workload profile Chapter 4 assigned it — the Search Service is read-heavy and CPU-bound under query load (justifying autoscaling on CPU utilization), whereas the AI Service's GPU-backed pods (§13.3.2) autoscale on a queue-depth metric instead, since GPU utilization alone is a poor proxy for inference backlog.

#### 13.3.2  GPU Node Pool Configuration (AI Service, Chapter 12)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: ai-service }
spec:
  replicas: 2
  template:
    spec:
      nodeSelector: { workload-type: gpu-inference }
      tolerations:
        - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }
      containers:
        - name: ai-service
          image: ghcr.io/darkdatamedicine/ai-service:{{ .Version }}
          resources:
            limits: { nvidia.com/gpu: 1 }
```

Isolated onto a dedicated node pool per Chapter 9 §9.5 — the general-purpose compute pool serving Chapter 4's other eighteen services never competes for GPU resources with the AI Service, and the AI Service's GPU pods are never scheduled onto general-purpose nodes where a GPU would sit idle and unbillable-for-value.

#### 13.3.3  GitOps Reconciliation

Per Chapter 9 §9.2.3's GitOps commitment, the actual deployment mechanism is a reconciliation loop (e.g., an Argo CD or Flux `Application`/`Kustomization` resource) watching a Git path, not a human running `kubectl apply` — reproduced here as the concrete mechanism behind Chapter 9 §9.9's "configuration drift detection" quality scenario:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: ddm-production }
spec:
  source: { repoURL: 'https://github.com/Ciprian-LocalPulse/DarkData-Medicine-Infra', path: 'environments/production' }
  destination: { server: 'https://kubernetes.default.svc', namespace: 'ddm-prod' }
  syncPolicy:
    automated: { prune: true, selfHeal: true }   # selfHeal = automatic drift correction
```

---

### 13.4  Stage 4 Artifacts: Federation Node Deployment

Extending Chapter 9 §9.7's outline to an actual node-onboarding script structure:

```bash
#!/usr/bin/env bash
# ddm-federation-node-init.sh — run once by a partner institution's
# technical team, per Ch.9 §9.7 and Ch.8 §8.10.1's governance-reviewed
# onboarding process

set -euo pipefail

echo "Generating node signing keypair (Ch.8 §8.10.2)..."
openssl genpkey -algorithm ed25519 -out node-signing-key.pem
openssl pkey -in node-signing-key.pem -pubout -out node-signing-key.pub

echo "Public key generated. Submit node-signing-key.pub through the"
echo "federation governance onboarding process before proceeding —"
echo "do NOT activate sync until the primary node's governance review"
echo "(Ch.8 §8.10.1) has approved this node's registration."

# Deploys the identical Stage 3 manifests (§13.3), parameterized only
# with this institution's own infrastructure details — no forked code,
# per Ch.9 §9.7's "no institution-specific code branch" requirement
kubectl apply -k environments/federation-node/
```

---

### 13.5  Backup and Restore Artifacts

Operationalizing Chapter 4 §4.18 and Chapter 11 §11.6.5's runbook with an actual scheduled job definition:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: ddm-backup }
spec:
  schedule: "0 3 * * *"   # daily, 03:00 — low-traffic window
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: ghcr.io/darkdatamedicine/backup-service:{{ .Version }}
              command: ["/app/run-backup.sh"]
              env:
                - name: RESTORE_TEST_ENABLED
                  value: "true"   # Ch.4 §4.18 — never counted as a
                                   # backup without a passing restore test
          restartPolicy: OnFailure
```

---

### 13.6  Environment Configuration Management

```
environments/
├── local/          # docker-compose.yml (§13.2.2), .env.example
├── staging/         # Kubernetes overlay (Kustomize), reduced replica
│                     # counts, synthetic-scale data (Ch.9 §9.1)
├── production/       # Full manifests (§13.3), production secret refs
└── federation-node/   # Parameterized overlay for partner-hosted mirrors
                        # (§13.4) — same base manifests, institution-
                        # specific values only, per Ch.9 §9.7
```

Kustomize-style overlays (a base manifest set, environment-specific patches) are the chosen mechanism specifically because they keep the base definition — the thing every environment has in common — as the single source of truth, with environment differences expressed as minimal, reviewable diffs rather than four independently-maintained, silently-diverging copies of the same manifests.

---

### 13.7  Implementation Status Summary

| Artifact Category | Status |
|---|---|
| GitHub Actions workflows (§13.1) | `OPERATIONAL` |
| Dockerfiles per service (§13.2.1) | `PLANNED` |
| `docker-compose.yml` local stack (§13.2.2) | `PLANNED` |
| Kubernetes manifests + HPA (§13.3.1) | `PLANNED`, longer horizon |
| GPU node pool config (§13.3.2) | `FUTURE` (depends on AI Service, Ch.12) |
| GitOps reconciliation (§13.3.3) | `PLANNED`, longer horizon |
| Federation node onboarding script (§13.4) | `FUTURE` |
| Backup CronJob (§13.5) | `PLANNED` |

---

### 13.8  Summary

This chapter has provided the concrete, runnable counterpart to every staged topology Chapter 9 described in diagram form — Dockerfiles, Kubernetes manifests, a GitOps reconciliation definition, a federation onboarding script, and a backup schedule, each explicitly tied back to the Chapter 9 section and Chapter 8 security control it implements. Chapter 14's task, on the same principle, is to provide the equivalent concrete, runnable counterpart to Chapter 8's Security Architecture — policy-as-code, IAM definitions, and a full per-service STRIDE pass beyond the three representative flows Chapter 8 covered.
