# Dark Data Medicine — Platform Architecture Series

## Chapter 12: AI Services Architecture

*Document status: Normative. Governed by Chapter 2 (AI First §2.3.4, Human Accountability §2.9, Zero Trust §2.3.7), Chapter 4 (AI Service stub, §4.5), Chapter 6 (Ontology, entity-linking targets), and Chapter 8 (§8.9, AI-specific security). This chapter expands the AI Service from a one-section stub into a fully specified subsystem — the most consequential expansion in this series to date, because it is the component most capable of quietly undermining the platform's central trust claim (Ch.2 §2.1) if built carelessly.*

*Version 0.1 — Draft for governance review*

---

### 12.0  Purpose and Scope

Chapter 4 §4.5 named the AI Service's responsibilities in one page: embeddings, semantic search support, RAG, summarization, classification, entity linking. This chapter specifies *how* each of those responsibilities is actually built, evaluated, and governed — because "AI First" (Ch.2 §2.3.4) is a principle that can be satisfied well or satisfied recklessly, and a negative-results registry has less room for the reckless version than almost any other kind of platform: an AI-generated summary that subtly mischaracterizes a negative finding, or an AI-suggested classification that quietly biases which findings surface in search, does direct damage to the exact scientific trust this project exists to build.

**The one sentence this entire chapter exists to enforce, restated from Chapter 2 §2.9 and Chapter 4 §4.5:** *AI proposes; a human, identifiable and accountable, disposes.* Every section below is a way of making that sentence true in practice rather than only in principle.

---

### 12.1  AI Design Philosophy

1. **Grounding over fluency.** Every AI-generated output that makes a claim about scientific content (a summary, a classification suggestion) must be traceable to specific source fields in the curated entry it describes — an ungrounded, fluent-sounding summary is a worse outcome than no summary at all for this platform specifically, because Chapter 1 of the platform's funding case is an extended argument that the scientific record already suffers from unreliable secondary characterization of primary findings.
2. **Confidence is a first-class output, not an implementation detail.** Every classification, entity-linking, or summarization output carries a numeric confidence score that is surfaced to the curator, not only logged internally — Chapter 4 §4.5 already established this; this chapter specifies exactly how that score is computed and calibrated (§12.9).
3. **No silent model changes.** Swapping the underlying embedding or language model is a versioned, governance-visible change (§12.10), not a transparent infrastructure upgrade — because a model swap can silently change which entries a semantic search surfaces as "similar," which is a scientifically consequential change even though it looks like a routine dependency bump.
4. **Train and evaluate only on curator-approved data.** Restated from Chapter 8 §8.9: no model in this architecture is fine-tuned or evaluated against unreviewed submission data, only against the published, curator-approved dataset — an unreviewed submission could itself be fabricated (the exact threat Chapter 8 §8.2.2 names), and a model trained on fabricated input degrades in a way that is far harder to detect after the fact than a single bad curatorial decision.

---

### 12.2  AI Capability Map

| Capability | Chapter 4 §4.5 Reference | Model Type | Status |
|---|---|---|---|
| Semantic embedding generation | Core responsibility | Embedding model (§12.3.1) | `FUTURE` |
| Semantic / hybrid search ranking | Supports Search Service (Ch.4 §4.3) | Same embedding model + reranking | `FUTURE` |
| Retrieval-augmented summarization | `/ai/summarize/{entryId}` | Embedding model + LLM (§12.5) | `FUTURE` |
| Cross-corpus RAG question answering | Implied by "AI Native" future evolution (Ch.3 §3.14) | Embedding model + LLM, Knowledge Graph-aware retrieval | `FUTURE`, longer horizon |
| Domain/classification suggestion | `/ai/classify` | Fine-tuned classifier or LLM-based classifier (§12.6) | `FUTURE` |
| Entity linking (free text → Ontology Term) | Supports Knowledge Graph Service (Ch.4 §4.4) | LLM-assisted + string-matching hybrid (§12.6) | `FUTURE` |
| Duplicate-submission proximity detection | Supports Review Service (Ch.4 §4.8) | Embedding-distance heuristic | `FUTURE` |
| Curator-facing "similar entries" recommendation | `/ai/similar/{entryId}` | Embedding nearest-neighbor | `FUTURE` |

Every row is `FUTURE` — this is stated once, plainly, rather than repeated after every subsection: nothing in this chapter is running in production today. This chapter specifies the architecture the AI Service will be built to, not a system that exists.

---

### 12.3  Model Architecture and Selection Strategy

#### 12.3.1  Selection Criteria

Per Chapter 2 §2.8 (Technology Independence), no specific model or vendor is architecturally load-bearing — the AI Service's contract (embeddings in, classifications out, confidence scores attached) is what downstream services depend on, not any particular model's internals. Selection criteria, applied at each model-choice decision point:

1. **Open-weight preference where viable**, consistent with Chapter 2 §2.3.5 (Open Science First) and §2.11 ("open formats over proprietary ones") — an open-weight embedding or classification model can be self-hosted, audited, and reproduced by a federation mirror node (Ch.4 §4.12) without depending on a third-party API's continued availability, pricing, or terms.
2. **Domain-appropriateness over general benchmark performance.** A biomedical-literature-pretrained embedding model is preferred over a higher-general-benchmark general-purpose model where the former demonstrably performs better on the platform's actual retrieval task (negative-result entries, clinical/scientific terminology) — evaluated against the retrieval-quality metrics in §12.9, not against a generic leaderboard.
3. **Cost-to-serve at projected scale**, since the platform's funding case explicitly frames the AI Service as a `FUTURE` capability introduced once curation and partnership fundamentals are established, not a first-dollar priority — model selection accounts for realistic inference cost at the entry volumes projected in the platform's roadmap.
4. **Reproducibility of the specific model version**, so that a summary generated in 2027 can, in principle, be regenerated and compared years later — a direct extension of Chapter 2 §2.6's versioning discipline to model artifacts, not only to code and data.

#### 12.3.2  Self-Hosted vs. API-Based Inference

Both are architecturally permitted, chosen per capability based on the criteria in §12.3.1, and both are required to satisfy the same confidence-scoring, grounding, and audit-logging contract (§12.1) regardless of which is used — the AI Service's internal Application Layer (Ch.3 §3.2) abstracts this choice away from every consuming service, so that a future switch between self-hosted and API-based inference for a given capability is confined to the AI Service's own Infrastructure Layer, per the layering discipline established in Chapter 3 §3.2.

---

### 12.4  Embedding Pipeline

```
MetadataGenerated event received (Ch.3 §3.7)
      |
      v
Construct embedding input
   (concatenation of: hypothesis statement, outcome narrative summary,
    methodology summary, structured fields rendered as text —
    NOT the full submission JSON verbatim, since structured fields
    benefit from natural-language rendering before embedding)
      |
      v
Chunking (if input exceeds model context window — rare at entry-level
   granularity, but methodology summaries on complex multi-arm trials
   may require it)
      |
      v
Generate embedding vector  (versioned: embedding_model_version tagged
      |                     on every stored vector, per §12.1 principle 3)
      v
Write to Vector Database (Ch.3 §3.8)
      |
      v
Emit EmbeddingGenerated (Ch.3 §3.7)
      |
      v
On subsequent entry correction/versioning (Ch.2 §2.9): re-embed and
   store as a new vector version, never overwrite — the prior version's
   embedding remains associated with the prior Dataset Release
   (Ch.5 §5.4.2) it was generated against
```

**Design note on what gets embedded.** Embedding the AI-rendered natural-language form of an entry, rather than raw JSON, is a deliberate choice: embedding models are trained on natural language, and a raw JSON blob's embedding quality for semantic-similarity purposes is measurably worse than a well-rendered textual summary's — a concrete, checkable claim the evaluation framework in §12.9 is expected to verify empirically before this pipeline is finalized, not merely assume.

---

### 12.5  Retrieval-Augmented Generation (RAG) Architecture

RAG is the architecture behind `/ai/summarize/{entryId}` and any future cross-corpus question-answering capability (Ch.3 §3.14). It exists specifically to solve the grounding problem named in §12.1's first design principle: an LLM asked to "summarize this negative result" without retrieval-constrained context is free to hallucinate plausible-sounding but unsupported detail, which is unacceptable for a platform whose entire value proposition is trustworthy negative-result reporting.

```
Request: summarize entry {id}
      |
      v
Retrieval step:
   - Fetch the entry's own structured fields directly (not via
     semantic search — the entry's own data is retrieved exactly,
     not approximately, since it is already known by ID)
   - (Optional, for contextual summaries) Retrieve the entry's
     Knowledge Graph neighbors (Ch.4 §4.4) — e.g., related
     replication attempts, same-drug-class entries — via exact
     graph traversal, not semantic approximation
      |
      v
Context assembly:
   Prompt = [system prompt, versioned per §12.8] +
            [retrieved structured fields, verbatim] +
            [retrieved graph context, if applicable]
      |
      v
Generation step (LLM inference)
      |
      v
Grounding verification (PLANNED, longer horizon):
   automated check that every factual claim in the generated summary
   is traceable to a specific retrieved field — flagging, not
   silently correcting, any claim that fails this check
      |
      v
Return summary + confidence score + "generated from" field citations
   (the specific structured fields the summary drew from, exposed
   to the caller — not merely asserted internally)
```

**Why retrieval is exact, not semantic, for an entry's own data.** A summarization RAG pipeline that retrieves an entry's own content via semantic search, rather than direct lookup by ID, introduces an unnecessary failure mode (imperfect retrieval of the very data being summarized) for no benefit — semantic retrieval is reserved for genuinely open-ended queries (§12.2's cross-corpus RAG capability), not for the trivial case of "summarize the thing I already have the ID for."

---

### 12.6  Classification and Entity-Linking Pipeline

```
Input: free-text field from a Submission (e.g., a hypothesis statement
       naming a disease not yet mapped to a controlled Ontology Term)
      |
      v
Hybrid matching:
   1. Exact/fuzzy string match against existing Ontology Terms
      and their Synonyms (Ch.6 §6.3, §6.6) — fast, deterministic,
      tried first
   2. If no confident string match: LLM-assisted candidate
      generation — propose the 3-5 most plausible Ontology Term
      matches, each with a confidence score
      |
      v
Confidence thresholding:
   - High confidence (above a governance-set threshold): surfaced
     to the curator as a pre-filled suggestion, one click to accept
   - Low confidence: surfaced as "no confident match — human
     classification required," never silently guessed
      |
      v
Curator decision (accept / reject / manually classify)
      |
      v
Decision recorded as a labeled training example  (§12.7's feedback loop)
      |
      v
If entity is genuinely novel and recurring: flagged to Curation Lead
   as a candidate new Ontology Term proposal (Ch.6 §6.5's governance
   process — the AI Service proposes the *need* for a new term;
   it never creates one unilaterally)
```

**The load-bearing distinction in this pipeline.** String-matching is preferred and tried first specifically because it is deterministic and auditable in a way LLM-based matching is not; the LLM is reserved for the harder cases string-matching cannot resolve, and even there, its role is confined to *candidate generation*, never *final classification* — the actual classification decision is always either a high-confidence pre-fill the curator explicitly accepts, or a human judgment call, never an unreviewed model output.

---

### 12.7  Human-in-the-Loop Workflow and Feedback

```
AI suggestion generated (classification, entity link, duplicate flag)
      |
      v
Presented to curator within the Review Service UI (Ch.4 §4.8),
   visually and structurally distinguished from curator-entered
   data — never rendered in a way indistinguishable from a
   human-confirmed field
      |
      v
Curator accepts / rejects / modifies
      |
      v
Outcome logged:
   - Accept: positive training signal, and — critically — the
     suggestion is now curator-attributed data (Ch.2 §2.9), not
     AI-attributed data, in the published entry
   - Reject: negative training signal; reason optionally captured
   - Modify: the curator's correction is the training signal,
     of higher value than a simple accept/reject since it shows
     *what the correct answer actually was*
      |
      v
Aggregated into the suggestion-acceptance-rate metric (Ch.4 §4.5) —
   the platform's primary AI-quality signal, reviewed at the cadence
   defined in the Operations Manual (Ch.11 §11.5)
      |
      v
Periodically (not continuously, per §12.10's controlled-release
   discipline): accumulated feedback informs a model
   fine-tuning/recalibration cycle
```

**Why acceptance is re-attributed to the curator, not left as an AI credit.** This is a direct, specific application of Chapter 2 §2.9's Human Accountability principle: once a curator accepts an AI-suggested classification, the published entry records that classification as the curator's own decision — auditable back to the fact that AI assistance was involved (the Audit Service, Ch.4 §4.16, retains that detail), but not surfaced in a way that could let a future dispute be deflected onto "the AI decided this" rather than "the accountable curator confirmed this."

---

### 12.8  Prompt Engineering and Governance

Every system prompt used by the AI Service — for summarization, classification, entity-linking candidate generation — is treated as a **versioned artifact under the same change-control discipline as code** (Chapter 2 §2.6), not as an informal, freely-edited string:

- Prompts are stored in version control, reviewed via the standard pull-request process (Chapter 10 §10.3.2).
- A prompt change that materially affects output behavior is evaluated against the quality metrics in §12.9 before being promoted to production, exactly as a model version change is (§12.10).
- **Prompt injection defense** (extending Chapter 8 §8.9): the system prompt's instructions are architecturally separated from user/submission-supplied content at the API level (using the underlying model provider's role-separation mechanism, where available, rather than simple string concatenation), and any submission free-text field is treated as untrusted data within the prompt context, never as an instruction the model should follow — restated here because it is as much a prompt-engineering discipline as a security control.

---

### 12.9  Evaluation and Quality Metrics

| Metric | What It Measures | Applies To |
|---|---|---|
| Suggestion-acceptance rate | Do curators actually find AI suggestions useful? (Ch.4 §4.5's headline metric) | Classification, entity linking |
| Retrieval precision@k | Of the top-k semantically retrieved entries, how many are genuinely relevant? | Embedding/semantic search |
| Grounding pass rate | What fraction of generated summaries pass the automated grounding-verification check (§12.5)? | RAG summarization |
| Confidence calibration | Do entries the model scores at 90% confidence turn out correct roughly 90% of the time? | All confidence-scored outputs |
| False-positive duplicate-flag rate | How often does the duplicate-proximity heuristic (Ch.4 §4.4, §4.8) flag genuinely distinct entries as possible duplicates? | Duplicate detection |
| Curator override/modification rate | Of accepted-then-later-corrected suggestions, how often was the original suggestion actually wrong? | Classification, entity linking |

**Evaluation cadence and gating.** No model, prompt, or pipeline change is promoted from Staging to Production (Chapter 9 §9.4) without passing an evaluation run against this metric set on a held-out, curator-verified test set — a direct extension of Chapter 9's general release-gating discipline to AI components specifically, since AI output quality does not fail loudly the way a broken API endpoint does; it degrades quietly, and only a deliberate evaluation step catches that.

---

### 12.10  Model Lifecycle Management (MLOps)

```
Candidate model/prompt version proposed
      |
      v
Evaluated against §12.9's metric set on a held-out test set
      |
      v
Shadow deployment (PLANNED, longer horizon):
   candidate runs alongside the production model, its outputs
   logged but never shown to curators, for a defined evaluation
   window — a direct analogue of the canary/rolling-deployment
   discipline in Chapter 9 §9.9, applied to model quality rather
   than infrastructure health
      |
      v
Governance review of shadow-deployment results
   (Curation Lead, per the same authority structure as an
   ontology change, Ch.6 §6.5)
      |
      v
Promotion to production (versioned, per §12.1 principle 3) OR
   rejection with documented rationale
      |
      v
Rollback capability retained: the prior model version remains
   available and can be reactivated without a full redeployment
   cycle, per the same rollback discipline as any other service
   (Ch.9 §9.4)
```

**Fine-tuning data policy, restated with operational specificity from §12.1 principle 4.** Any fine-tuning run draws exclusively from the published, curator-approved dataset (Ch.5's `Dataset Release`, immutable per Ch.2 §2.9) — never from the live curation queue, never from rejected submissions, and never from AI-generated synthetic data layered on top of real entries without explicit governance sign-off, since each of those sources carries a distinct contamination risk the published-dataset-only policy is designed to avoid entirely rather than mitigate partially.

---

### 12.11  Cost and Resource Management

Extending Chapter 4 §4.5's Scaling notes and Chapter 9 §9.5's GPU node-pool provisioning: inference workloads are split into **real-time** (curator-facing classification suggestions, summarization-on-demand — latency-sensitive, lower per-request cost tolerance) and **batch** (embedding generation for newly published entries, periodic re-evaluation runs — latency-tolerant, schedulable during lower-cost or lower-contention windows). This split allows the majority of AI Service compute cost — bulk embedding generation across a growing corpus — to be scheduled economically, reserving the more expensive always-available capacity for the smaller volume of genuinely real-time curator-facing requests.

---

### 12.12  Bias, Fairness, and Scientific Integrity

This platform's AI components carry a specific integrity risk beyond generic AI-fairness concerns: a classification or ranking bias here does not merely produce an unfair user experience — it can systematically make certain kinds of negative results *harder to find*, which is a direct, if unintentional, reproduction of the exact publication-bias problem this entire platform exists to counteract (per the funding case's Part I). Consequently:

- Classification and ranking models are evaluated (§12.9) for differential performance across `institution_type` and `domain` categories specifically, not only in aggregate — a model that classifies industry-funded submissions systematically less accurately than academic ones, for instance, would be a scientific-integrity failure even if its aggregate accuracy looked acceptable.
- No AI Service output is permitted to affect Search Service ranking (Ch.4 §4.3) in a way that a curator or reader cannot inspect and understand — "why did this appear above that" must remain answerable, consistent with the Transparency principle (Ch.2 §2.9) applied to the AI layer specifically, not only to governance decisions.
- Per Chapter 2 §2.9's "No editorial bias" principle, restated here at the AI layer: AI-assisted classification is evaluated on methodological/factual grounds only, and any evidence of the model favoring or disfavoring entries based on outcome direction, sponsor type, or institution type is treated as a critical defect requiring immediate model rollback (§12.10), not a tunable parameter.

---

### 12.13  Security (Cross-Reference)

The full AI-specific threat model — prompt injection, data poisoning, model output as advisory-only — is specified in Chapter 8 §8.9 and is not repeated here; this chapter's §12.1, §12.6, §12.8, and §12.10 are the architectural mechanisms that satisfy Chapter 8's security requirements, and any future revision to either chapter should keep the two synchronized rather than letting security posture and AI architecture drift apart.

---

### 12.14  Implementation Status Summary

| Component | Status |
|---|---|
| Embedding pipeline | `FUTURE` |
| Vector Database | `FUTURE` (Ch.3 §3.8) |
| RAG summarization | `FUTURE` |
| Classification / entity-linking pipeline | `FUTURE` |
| Human-in-the-loop feedback capture | `FUTURE` |
| Prompt version control and governance | `PLANNED` (as a process, ahead of any live model — the discipline in §12.8 applies from the first prompt ever written, ideally before, not after, the AI Service's first production deployment) |
| Evaluation/gating pipeline (§12.9–§12.10) | `FUTURE` |
| Shadow deployment capability | `FUTURE`, longer horizon |

---

### 12.15  Summary and Handoff

This chapter has taken the AI Service from a one-page Chapter 4 stub to a fully specified subsystem, built around a single non-negotiable constraint restated in nearly every section: AI output is confidence-scored, grounded, logged, and always subject to human confirmation before it affects the canonical dataset. The next document in this series — Testing Architecture — inherits a specific obligation from this chapter: the evaluation and gating discipline specified in §12.9–§12.10 is not a separate concern from the platform's general testing strategy, and the Testing chapter's treatment of AI-component testing should extend this chapter's metrics rather than inventing a parallel framework.
