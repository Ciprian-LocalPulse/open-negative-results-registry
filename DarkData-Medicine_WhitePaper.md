**DARK DATA MEDICINE**

*Recovering the Invisible Half of Medical Science:*

An Open Infrastructure for Publishing Negative and Null Results in Biomedical Research

**A WHITE PAPER**

Prepared in connection with the Dark Data Medicine open registry project

*github.com --- Dark Data Medicine: The Open Negative Results Registry*

Author: Ciprian Ștefan Pleșca

Affiliation: Founder @LocalPulse;
Lead Enterprise AI Architect

Contact: contact@agentflow-enterprise.com
Date: July 2026

Code: MIT License · Data: CC0-1.0 / CC-BY-4.0 · Version 1.0

**Abstract**

Modern biomedicine generates a vast quantity of experimental and clinical evidence that never reaches the published record. Estimates converge on the finding that somewhere between one quarter and one half of all completed clinical trials, and roughly half of all preclinical experiments, are never published or never fully reported --- a phenomenon commonly termed "dark data" or the "file-drawer problem." This paper argues that the failure to systematically capture negative, null, and inconclusive results is not a peripheral inefficiency of the research enterprise but a structural defect with direct and measurable consequences: redundant experimentation, inflated effect sizes in the published literature, misallocated funding, delayed drug development, and, in the worst cases, avoidable harm to patients enrolled in trials that repeat interventions already shown not to work.

We review the empirical literature on publication bias and research waste, synthesize the economic magnitude of the problem, and examine why three decades of policy interventions --- prospective trial registration, the FDA Amendments Act of 2007, the EU Clinical Trials Regulation, journal-level registration mandates, and voluntary campaigns such as AllTrials --- have reduced but not resolved non-reporting. We then present Dark Data Medicine, an open-source, community-governed registry designed to capture negative and null results directly, independent of the journal publication pathway, using a versioned JSON schema, automated validation, a non-technical contribution pathway, and a public, queryable search interface. We describe the system\'s architecture, governance model, quality-control pipeline, and licensing framework in detail, and we situate it against comparable infrastructure --- ClinicalTrials.gov, the EU Clinical Trials Register, PROSPERO, the Open Science Framework, and Registered Reports --- to clarify what gap it is designed to fill and what it deliberately does not attempt to replace.

Finally, we present a quantitative framework for estimating the potential value of a mature negative-results registry, discuss the ethical and governance risks inherent in aggregating unpublished scientific claims, and lay out a phased roadmap for scaling from an illustrative seed dataset to a curated evidence base capable of supporting systematic reviews, meta-analyses, and funding decisions. We conclude that while no single intervention can eliminate publication bias, a low-friction, freely licensed, machine-readable registry of negative results --- purpose-built rather than retrofitted onto positive-result infrastructure --- addresses a distinct and currently unmet need in the evidence ecosystem.

**Keywords**

publication bias; dark data; negative results; null results; research waste; open science; clinical trial registries; reproducibility; meta-analysis; FAIR data; research infrastructure; evidence-based medicine

**How to Read This Document**

This white paper is organized in three parts, designed to be read in sequence but usable as independent reference sections. Part I (Sections 1--7) is aimed at readers who want the evidentiary case for why unpublished negative results are a significant problem in biomedicine --- funders, policy audiences, and researchers unfamiliar with the publication-bias literature. Readers already conversant with that literature may wish to move directly to the Executive Summary in Section 1 and then to Part II.

Part II (Sections 8--14) is a technical and governance specification of the Dark Data Medicine registry itself --- its schema, quality-control pipeline, contribution pathways, and licensing --- aimed at prospective contributors, curators, and anyone evaluating whether to build on or integrate with the system. Readers primarily interested in the underlying data model should turn directly to Section 9 and Appendix A.

Part III (Sections 15--24) addresses impact, ethics, positioning relative to adjacent infrastructure, and the project\'s roadmap, aimed at institutional partners, funders, and journal or society representatives considering an adoption or endorsement decision.

Part IV (Sections 25--31) is a forward-looking research agenda, explicitly separated from the description of the current system, addressing five specific gaps a university reviewer would immediately flag in a version 1.0 system: a minimal metadata schema, the absence of a semantic knowledge-graph layer, the absence of a standardized failure ontology, the absence of AI-native discovery tooling, and the absence of a formal evidence-quality model. Every proposal in Part IV is explicitly labeled as planned rather than built. The Appendices provide detailed reference material --- the full schema, a glossary, governance excerpts, the current seed dataset, and an independent verification log --- intended to be consulted rather than read start to end.

**Table of Contents**

**Part I --- The Problem: Why Negative Results Disappear 7**

> 1\. Executive Summary 8
>
> 2\. Introduction: The Invisible Half of Science 10
>
> 3\. Anatomy of Publication Bias: A Literature Review 12
>
> 4\. The Economics of Wasted Research 16
>
> 5\. Case Studies 19
>
> 6\. The Regulatory Landscape and Its Gaps 23
>
> 7\. Existing Interventions and Their Limits 27

**Part II --- The Solution: Dark Data Medicine 29**

> 8\. Design Philosophy and Guiding Principles 30
>
> 9\. System Architecture and Data Model 32
>
> 10\. Governance Model 35
>
> 11\. Data Quality and the Validation Pipeline 37
>
> 12\. The No-Code Contribution Pathway 40
>
> 13\. Technical Infrastructure 42
>
> 14\. Licensing and Legal Framework 44

**Part III --- Impact, Positioning, and the Road Ahead 46**

> 15\. Use Cases 47
>
> 16\. A Quantitative Framework for Projected Impact 49
>
> 17\. Ethical Considerations 52
>
> 18\. Comparative Positioning 54
>
> 19\. Roadmap and Scaling Strategy 55
>
> 20\. Sustainability and Funding Model 57
>
> 21\. Risks and Limitations 59
>
> 22\. Stakeholder Analysis and Adoption Pathways 62
>
> 23\. Frequently Asked Questions 65
>
> 24\. Conclusion 68

**Part IV --- Extending the Architecture: A Research Agenda for v2.0 70**

> 25\. Scope of This Part: What Is Built Versus What Is Proposed 71
>
> 26\. A Richer Metadata Schema (Version 2.0 Proposal) 73
>
> 27\. Toward a Knowledge Graph: RDF, OWL, and SPARQL 75
>
> 28\. A Failure Ontology for Negative Results 78
>
> 29\. AI-Native Discovery: Embeddings, Semantic Search, and RAG 81
>
> 30\. An Evidence Quality and Confidence Model 83
>
> 31\. Sequencing This Agenda Against the Existing Roadmap 85

**Appendices 86**

> Appendix A: Full Submission Schema Reference 87
>
> Appendix B: Glossary of Terms 89
>
> Appendix C: Governance Charter (Reference Excerpt) 91
>
> Appendix D: Methodology Note for This White Paper 92
>
> Appendix E: Current Seed Dataset --- Complete Reproduction 93
>
> Appendix F: Independent Technical Verification Log 95
>
> Appendix G: Complete JSON Schema (Verbatim) 97
>
> Appendix H: References 98

**PART I**

**THE PROBLEM: WHY NEGATIVE RESULTS DISAPPEAR**

**1. Executive Summary**

Science advances by accumulation. Every experiment, whether it confirms or refutes its hypothesis, is in principle a contribution to the shared body of evidence that future researchers draw on to design their own studies, allocate funding, and make clinical decisions. In practice, this is not how the literature works. The scientific publication system was built around a single unit of output --- the peer-reviewed positive-result paper --- and it rewards novelty, statistical significance, and narrative clarity far more than it rewards completeness. The consequence is that a very large fraction of what science actually learns, particularly what it learns to be false or ineffective, is never written down anywhere a second researcher could find it.

This white paper makes three arguments. First, that the scale of unpublished negative and null results in biomedicine is large enough to materially distort meta-analyses, misdirect research funding, and in some documented cases expose patients to interventions already known elsewhere to be ineffective or unsafe. Second, that the existing policy apparatus built to solve this --- trial registries, reporting mandates, and voluntary transparency campaigns --- has produced real but partial progress, and structurally cannot reach the much larger universe of preclinical, translational, and early-phase negative findings that fall outside its jurisdiction. Third, that a complementary, purpose-built, freely licensed registry --- one engineered from the outset around negative and null results rather than retrofitted from positive-result infrastructure --- can close part of this gap at very low marginal cost, provided it is designed with rigorous data governance, a low-friction contribution pathway, and a credible curation process.

The remainder of this paper is organized in three parts. Part I documents the problem: the empirical literature on publication bias, its economic and clinical costs, illustrative case studies, and the limits of the current regulatory and voluntary response. Part II presents Dark Data Medicine, an open-source registry designed to address the specific slice of the problem that existing infrastructure does not reach, and describes its data model, governance, quality assurance, and technical architecture in detail. Part III discusses projected impact, ethical considerations, positioning relative to adjacent projects, and a roadmap for scaling from an illustrative seed dataset toward a mature, citable evidence resource.

**Key findings**

- Across multiple independent cohort studies spanning three decades, between roughly one quarter and one half of completed clinical trials are never published, with unpublished rates historically as high as 40--60% in some cohorts and specialties, and with negative-result trials consistently published less often and later than positive ones.

- Preclinical biomedical research shows an estimated irreproducibility rate exceeding 50%, translating to on the order of \$28 billion per year in the United States alone spent on preclinical work that cannot later be reproduced --- a figure economists consider conservative.

- Legally mandated reporting regimes such as the U.S. FDA Amendments Act of 2007 ("FDAAA") have improved compliance over time but remain incompletely enforced; independent public audits (the FDAAA TrialsTracker) have repeatedly documented large sponsor populations out of compliance with statutory reporting deadlines, with no FDA fine issued for years after the law\'s penalty provisions took effect.

- No existing registry is purpose-built to capture negative and null results from preclinical, translational, and early-phase research that never reaches a formal trial registry in the first place --- the largest and least visible layer of the dark-data problem.

- A low-friction, schema-validated, CC0/CC-BY-licensed registry with a non-technical contribution pathway can plausibly capture a meaningful share of this otherwise permanently lost evidence at a fraction of the cost of formal publication infrastructure.

**2. Introduction: The Invisible Half of Science**

Imagine a hospital library that shelves only the books that have happy endings. A visiting researcher, browsing those shelves, would form a systematically distorted picture of the world --- not because any individual book is false, but because the selection itself is not random. This is, in essence, what has happened to the biomedical literature. Statistically significant, novel, positive findings are written up, submitted, reviewed, and published far more often, and far faster, than null or negative ones. The mechanism is not usually fraud. It is a long chain of small, individually rational decisions --- a trialist who decides a negative result is not worth the months of writing it up; a journal editor who reasonably prioritizes what readers will cite; a funder who is judged on breakthroughs rather than on eliminated dead ends --- that in aggregate produces a large and non-random gap in the recorded evidence base.

The literature refers to this gap by several overlapping names: publication bias, the file-drawer problem (a term coined in the social sciences nearly half a century ago to describe unpublished null results sitting in researchers\' filing cabinets), selective outcome reporting, and, more broadly, "dark data" --- information that was generated by a properly conducted study but never entered the searchable, citable record. Dark data is distinct from fraudulent or fabricated data; it is real evidence, honestly collected, that simply never became visible to anyone outside the team that produced it.

Why does this matter enough to warrant a dedicated piece of research infrastructure? Because negative results are not merely uninteresting; they are load-bearing. A negative trial tells the next investigator not to walk down that corridor. Without it, the corridor gets walked down again --- by a different team, at a different institution, often years later, at full cost, sometimes with human subjects enrolled in a study whose outcome was already known elsewhere. Systematic reviews and meta-analyses, which regulatory agencies and clinical guideline committees treat as the highest tier of evidence, are only as reliable as the completeness of the literature they draw from; when a meaningful share of negative trials never enters that literature, the resulting effect-size estimates are mechanically biased upward, sometimes by a substantial margin.

**2.1 Scope of this paper**

This paper focuses specifically on biomedical and life-sciences research --- clinical trials, preclinical and translational studies, and early-stage pharmacological and device research --- because this is the domain in which non-publication carries the most direct human cost, and the domain in which the Dark Data Medicine project described in Part II operates. The general phenomenon of publication bias is well documented across the social and physical sciences as well, and where relevant we draw on that broader literature, but the case studies, regulatory analysis, and system design that follow are oriented toward medicine.

We use "negative result" throughout to mean a properly conducted study whose primary hypothesis was not supported by the data --- for example, a trial in which the tested intervention did not outperform the comparator on its pre-specified primary endpoint. We use "null result" for the related but distinct case of a study that found no measurable effect in either direction. We treat both as first-class scientific findings, on par with positive results in evidentiary value, and we deliberately avoid language --- such as "failed trial" --- that frames a negative outcome as a failure of the research process rather than as a successful elimination of a hypothesis.

**3. Anatomy of Publication Bias: A Literature Review**

The empirical study of publication bias in medicine has a documented history stretching back to at least the mid-1980s, when early registry-based audits began comparing what was submitted to trial registries against what subsequently appeared in the indexed literature. The findings have been remarkably consistent across four decades of replication in different specialties, countries, and methodologies: trials with statistically significant, "positive" findings are published more often, and faster, than trials that are negative, null, or inconclusive.

**3.1 The scale of non-publication**

Cohort studies that track a defined set of registered or ethics-committee-approved trials forward in time to see which are eventually published consistently find non-publication rates in the range of roughly one quarter to one half, with considerable variation by specialty, funder, and follow-up window. A widely cited pediatric cohort study found that among a defined set of phase III randomized trials, nearly 28% remained unpublished at follow-up, and close to 40% had never even been registered. Earlier work using the same methodology in the 1990s had found a non-publication rate approaching 41% for similar pediatric trial abstracts. A hospital-based cohort following all drug trials submitted to a single ethics committee over an eight-year window found an overall publication rate below half --- 48.4% --- with positive-result trials published at a rate of roughly 85% against roughly 69% for negative-result trials, and with negative trials taking on average about 50% longer to reach print once they were published at all.

Neurology-specific data covering trials completed between 2008 and 2014 found publication rates hovering close to 50% with no statistically significant improvement over that period, even as the time-to-publication for trials that were eventually published fell substantially --- evidence that transparency initiatives have sped up reporting for the studies that do get reported without necessarily increasing the share that get reported at all. Broader systematic reviews synthesizing many such cohort studies typically report publication-rate ranges in the neighborhood of 50 to 77% at long follow-up, dropping to well under half within the first 30 months after trial completion --- the window in which the evidence is most clinically actionable.

**3.2 Selective reporting within published studies**

Non-publication is only the most visible layer of the problem. A second, subtler layer is selective outcome reporting: a trial is published, but only the endpoints that reached statistical significance are reported, while pre-specified secondary or safety endpoints that did not are quietly dropped from the final manuscript. This form of bias is harder to detect because it requires comparing the published paper against the original trial protocol or registry entry --- a comparison that is now more feasible than it once was, precisely because prospective registration has become more common, but that remains labor-intensive and is rarely performed outside dedicated methodological audits.

**3.3 The direction and magnitude of the distortion**

Classic registry-comparison studies illustrate the direction of the bias with unusual clarity. In one frequently cited historical audit, investigators compared trial outcomes recorded in a cancer trial registry against what subsequently appeared in the published literature and found a marked skew toward favorable outcomes in the published subset relative to the full registered cohort. A separate large survey of trialists asking directly about both published and unpublished work they had personally been involved in found that only 14% of unpublished completed randomized trials had favored the new therapy under study, compared with 55% of the trials that had actually been published --- a striking illustration that the decision to publish is itself correlated with the direction of the result, not merely its statistical significance.

The consequence for evidence synthesis is direct: when systematic reviews and meta-analyses pool only the published subset of a body of research, the pooled effect size is mechanically biased toward showing a larger benefit than actually exists. Reviews focused specifically on psychological and behavioral interventions that were able to recover unpublished trial data found that incorporating the missing studies reduced the estimated effect size by roughly a quarter --- a magnitude large enough, in a clinical context, to change a treatment recommendation.

**3.4 Has the problem improved over time?**

A natural question, given three decades of registries, mandates, and campaigns, is whether the scale of non-publication has meaningfully declined. The honest answer from the methodological literature is mixed and specialty-dependent. Where researchers have been able to compare cohorts of trials completed in different eras using consistent methodology, the general pattern is that time-to-publication has fallen for trials that are eventually published --- a plausible consequence of prospective registration making trials easier to track and of results-reporting mandates creating firmer deadlines --- while the underlying share of trials that are ever published or ever fully reported has moved much less, and in some specialty-specific cohorts has shown no statistically significant improvement across comparable multi-year windows. This pattern is visible in the neurology cohort data discussed in Section 3.1: publication rates near 50% held roughly steady across a study period even as time-to-publication for the published subset improved substantially.

A plausible interpretation, consistent with the regulatory analysis in Section 6, is that policy interventions to date have been most effective at accelerating disclosure for the subset of research already inside their jurisdiction --- registered trials subject to a reporting deadline --- while doing comparatively little to change the underlying decision of whether to disclose a negative result at all, particularly for research, such as preclinical and early-phase work, that falls outside any mandate\'s scope in the first place. This interpretation directly motivates the design choice, discussed in Section 8, to build new low-friction infrastructure aimed specifically at the disclosure decision itself, rather than to rely solely on tightening deadlines within the existing regulatory perimeter.

**3.5 Structural drivers**

The literature identifies several converging structural causes rather than a single villain:

- Investigator incentives. Career advancement in academic medicine is weighted heavily toward novel, positive findings; a negative trial is real work with comparatively little publishable capital attached to it, so investigators reasonably move on to the next study rather than spend months writing up a result unlikely to be accepted by a high-impact journal.

- Journal incentives. Editors curate for reader interest and citation impact, and historically negative or null results have been perceived --- rightly or wrongly --- as less citable, creating an implicit filter before a manuscript is ever formally reviewed.

- Sponsor incentives. Commercially funded negative trials face an additional disincentive: a negative result for a company\'s own product carries reputational and, in some jurisdictions, competitive risk, and industry-funded negative studies are documented to be less likely to be published than negative studies funded by government or non-profit sources.

- Time and resourcing. Writing a full manuscript, navigating peer review, and responding to reviewer comments is a multi-month-to-multi-year undertaking. For a team that has already moved to its next grant cycle, a negative result that carries no publication incentive is the first thing cut from the workload.

- Absence of a low-friction alternative venue. Until relatively recently there was no credible, findable, low-effort place to deposit a negative result short of full journal publication --- meaning the realistic choice for most negative findings was full publication or nothing, and nothing usually won.

**4. The Economics of Wasted Research**

Publication bias is often discussed as an epistemic problem --- a distortion of what the literature says is true. It is equally, and perhaps more urgently, an economic problem: money, laboratory time, animal subjects, and human trial participants are repeatedly committed to answering questions that have already been answered elsewhere, simply because the answer was never made visible.

**4.1 The cost of irreproducible preclinical research**

The most widely cited quantitative estimate in this area comes from a 2015 economic analysis published in PLOS Biology by Leonard Freedman and colleagues, who combined published irreproducibility-rate estimates with data on total U.S. life-sciences research spending. Using a deliberately conservative irreproducibility estimate of 50% --- despite some individual studies suggesting rates as high as 89% in certain preclinical domains --- and applying it to the roughly \$56 billion spent annually on preclinical research in the United States, the analysis arrived at an estimated \$28.2 billion per year spent on preclinical research that cannot later be reproduced. The authors and independent commentators have since noted that this figure, striking as it is, likely understates the true cost once downstream effects are included: later research and clinical development programs that build on an initially irreproducible finding compound the waste, with some broader estimates of these cascading "house of cards" effects ranging into the tens or hundreds of billions of dollars annually.

These figures are not primarily about outright scientific error. A large share of documented irreproducibility traces to mundane, correctable causes --- contaminated or misidentified cell lines, unvalidated antibodies and other biological reagents, and incompletely reported experimental protocols --- rather than to fraud or incompetence. This matters for the present argument: if a large share of preclinical waste stems from information that was never systematically shared (a particular reagent batch behaved unpredictably; a cell line was later found to be contaminated; a specific dosing regimen showed no effect in a pilot study), then a substantial share of that \$28 billion is, in principle, recoverable through better information-sharing infrastructure rather than through more research spending.

**4.2 The cost of redundant clinical trials**

At the clinical stage the unit costs are larger and the stakes more directly human. A single phase II or phase III oncology trial can cost tens of millions of dollars to run and take years to enroll and complete; failing to learn that a comparable intervention had already been tried and found ineffective elsewhere means that cost, and that multi-year delay, is paid again. Because negative trials are published less often and later than positive ones --- with the hospital-cohort data cited above showing negative-result studies taking roughly twice as long to reach publication, when they are published at all --- the practical window in which a second team could discover the prior negative result before committing to their own trial is frequently already closed by the time any publication occurs.

**4.3 Human cost: repeated exposure of trial participants to known-ineffective interventions**

The economic framing, while useful for policy audiences, understates the ethical dimension. Clinical trial participants consent to accept some risk and burden in exchange for contributing to generalizable knowledge; the value proposition of that consent depends on the knowledge actually being captured and shared. When a negative result is never published, every subsequent trial participant enrolled in a materially similar study is, in effect, re-litigating a question that has already been answered, without the benefit of that prior answer. In extreme historical cases this has amounted to preventable harm at scale: retrospective reviews of certain therapeutic areas have found periods where a costly and burdensome intervention continued to be tested and adopted well beyond the point at which available --- but insufficiently disseminated --- evidence should have curtailed it.

**4.4 A framework for estimating recoverable value**

We propose a simple order-of-magnitude framework, developed further in Part III, for reasoning about the recoverable value of a negative-results registry: recoverable value is a function of (a) the number of negative or null findings generated annually that would otherwise remain permanently dark, (b) the probability that a freely available registry entry is discovered by a researcher who would otherwise have repeated the work, and (c) the average cost of the repeated work avoided. Even under conservative assumptions for each parameter, the aggregate figure is large relative to the marginal cost of operating a lightweight, community-curated registry --- the central premise motivating the system described in Part II.

**5. Case Studies**

Aggregate statistics can obscure how the dark-data problem plays out in specific, well-documented episodes. This section reviews three illustrative cases spanning different mechanisms of harm: distorted meta-analytic conclusions, delayed recognition of drug risk, and large-scale adoption of an intervention later shown to be ineffective.

**5.1 Selective reporting in antidepressant trials**

One of the most influential empirical demonstrations of publication bias in modern psychiatry came from a study comparing FDA regulatory submissions --- which by law include every trial a manufacturer ran, positive or negative --- against what was subsequently visible in the published journal literature for a set of antidepressant medications. The published literature painted a substantially more favorable picture of drug efficacy than the complete regulatory record, because trials with disappointing results were selectively not published or were published in a way that reframed their outcome as more positive than the primary endpoint supported. The episode is now a standard teaching example in evidence-based medicine curricula precisely because it demonstrates, with an unusually clean natural experiment (a complete regulatory dataset versus the public literature drawn from the same underlying trials), exactly how large the gap between the "real" evidence base and the visible one can be.

**5.2 High-dose chemotherapy with autologous bone marrow transplant for breast cancer**

A widely discussed historical case involves the adoption, through the 1980s and 1990s, of high-dose chemotherapy combined with autologous bone-marrow transplantation as a treatment for advanced breast cancer, on the strength of early, methodologically weaker studies suggesting benefit. The intervention was costly, physically grueling, and was adopted at scale --- by some retrospective estimates, tens of thousands of patients received it, at an aggregate cost estimated in the billions of dollars --- well before the larger, more rigorous randomized trials that eventually found no meaningful survival benefit had been completed and disseminated. Commentators examining the episode afterward have pointed to the slow and incomplete circulation of contrary and cautionary early evidence as a contributing factor: signals that should have tempered enthusiasm earlier were not systematically visible to the wider clinical community at the point when adoption decisions were actually being made.

**5.3 Undisclosed adverse-event signals and delayed cardiovascular risk recognition**

A further category of harm arises not from a wholly unpublished trial but from safety signals that were generated early, in preclinical or early clinical work, but did not reach the wider clinical and regulatory community until much later --- after a medicine had already been prescribed to a large population. The general pattern, well documented across several historically significant drug-safety controversies in cardiology and analgesic pharmacology, is consistent: early trial data suggesting an elevated cardiovascular or other serious risk existed inside sponsor organizations, regulatory submissions, or narrowly circulated conference presentations well before the risk was widely recognized in the published, indexed literature and before prescribing patterns changed accordingly. Post-hoc reviews of these episodes have repeatedly identified the same root cause examined throughout this paper: the relevant negative or cautionary signal existed as real data, generated through legitimate research, but was not systematically visible to the practicing clinicians and independent researchers who would have acted differently had they been able to find it in time. This category of case is distinct from Sections 5.1 and 5.2 in an important way: it is not primarily about a single trial\'s efficacy conclusion being suppressed, but about the cumulative, cross-study visibility of a safety pattern that only becomes apparent when multiple negative or concerning findings are viewed together --- precisely the kind of aggregation a structured, queryable registry is designed to make possible that an unstructured literature search is not.

**5.4 First-in-human trials and the limits of preclinical disclosure**

A separate class of episode illustrates the cost of insufficient preclinical disclosure specifically. Severe, unexpected adverse reactions in early-phase, first-in-human drug trials have, in several well-documented historical cases, prompted retrospective questions about how much relevant preclinical and comparative pharmacology data existed elsewhere --- in other laboratories, other sponsor organizations, or other early-stage programs targeting biologically related pathways --- but had never been disseminated in a form that the trial\'s own preclinical and clinical safety reviewers could have discovered before dosing began. These episodes are frequently cited in bioethics and clinical-pharmacology literature as evidence that the field\'s disclosure norms for preclinical and translational findings lag substantially behind its disclosure norms for completed clinical trials, reinforcing the central argument of Section 6.5: that the preclinical and translational layer of the evidence base is both the largest and the least visible, and that closing that gap has direct implications for the safety of the human volunteers who take part in the trials built on top of it.

**5.5 Persistent non-compliance with mandatory reporting**

The most direct illustration that dark data is not merely a historical artifact comes from ongoing public audits of legally mandated reporting. Researchers at the University of Oxford\'s Bennett Institute (formerly the EBM DataLab), led by Ben Goldacre and colleagues, built the FDAAA TrialsTracker specifically to give the public a live, per-sponsor view of compliance with the U.S. FDA Amendments Act of 2007, which requires most "applicable clinical trials" to post summary results to ClinicalTrials.gov within roughly a year of completion. Their peer-reviewed analysis, published in The Lancet, found large-scale non-compliance years after the law\'s Final Rule took effect, and the tracker\'s public data has repeatedly shown a majority of overdue trials still outstanding at any given snapshot, despite statutory penalties of up to roughly \$10,000--\$12,000 per day per overdue trial. For an extended period after the penalty provisions became enforceable, the FDA had not issued a single fine, a fact that campaigners have argued substantially blunted the law\'s deterrent effect; the agency\'s first formal non-compliance action did not arrive until years later. This case matters for the present paper because it demonstrates that even the most legally robust, well-funded, and long-standing piece of transparency infrastructure in this space --- a government-run registry with statutory teeth --- has not been sufficient on its own to close the reporting gap, underscoring the need for complementary mechanisms that do not depend solely on regulatory enforcement.

**6. The Regulatory Landscape and Its Gaps**

Over the past two decades, policymakers, journal editors, and the research community have built a substantial apparatus aimed at reducing non-publication and selective reporting. This section reviews the major components of that apparatus and identifies, specifically, the layer of the problem that remains structurally outside its reach --- the gap that Part II\'s proposed registry is designed to address.

**6.1 Trial registries**

ClinicalTrials.gov, operated by the U.S. National Library of Medicine, and the WHO International Clinical Trials Registry Platform, which aggregates records from national and regional registries including the EU Clinical Trials Register, together form the backbone of prospective trial registration. The International Committee of Medical Journal Editors\' longstanding requirement that a trial be prospectively registered as a condition of later publication has meaningfully increased the share of trials that are at least registered, even when their results are never separately reported. Registration alone, however, only guarantees that a trial\'s existence and design are visible; it does not guarantee that its results ever become visible, which is precisely the gap that results-reporting mandates were later built to close.

**6.2 Results-reporting mandates: FDAAA and the EU Clinical Trials Regulation**

The U.S. FDA Amendments Act of 2007, and its 2016 "Final Rule," together require sponsors of most applicable clinical trials to post summary results --- not merely trial existence --- to ClinicalTrials.gov within a defined window after completion, with statutory financial penalties for non-compliance. The European Union\'s Clinical Trials Regulation contains analogous results-reporting obligations for trials conducted in EU member states. As documented in Section 5.5, these mandates have improved reporting relative to the pre-mandate era but have not achieved full compliance, and enforcement --- particularly the actual levying of financial penalties --- has historically lagged the letter of the law.

**6.3 Journal- and funder-level initiatives**

A parallel set of interventions operates through the journal and funding-agency layer rather than through statute. Registered Reports, a publication format now offered by several hundred journals, commit to publishing a study based on the quality of its pre-registered design and methodology rather than on the direction of its eventual results, directly removing the incentive to suppress a negative outcome after the fact. Some funders now require grant recipients to deposit trial results in a public registry as a condition of future funding eligibility. The AllTrials campaign, launched in 2013 with institutional backing from organizations including BMJ and PLOS, has pushed for universal registration and reporting of all past and present trials and has been influential in shaping public and policy discourse, including commissioning the audit work that led to the FDAAA TrialsTracker.

**6.4 The international dimension**

The regulatory apparatus described above is not uniform across jurisdictions, and this unevenness itself contributes to the dark-data problem. The WHO International Clinical Trials Registry Platform was established specifically to aggregate registry data across the fifteen-plus national and regional primary registries that meet its data-quality criteria, in explicit recognition that a purely national reporting regime cannot capture a genuinely global clinical research enterprise. The United Kingdom\'s Health Research Authority has, in recent years, introduced its own transparency requirements and public compliance monitoring for trials it approves, building on independent academic audit work --- including further contributions from the Bennett Institute researchers discussed in Section 5.5 --- that found substantial numbers of UK-sponsored trials with overdue or missing results on both ClinicalTrials.gov and the EU/UK trial registers. The European Union\'s centralized Clinical Trials Information System, which succeeded the older EudraCT registry as the operative reporting mechanism under the EU Clinical Trials Regulation, represents a more recent attempt to harmonize reporting obligations across member states, though independent audits of its early years of operation, similar in spirit to the FDAAA TrialsTracker, have identified comparable patterns of incomplete compliance.

The practical consequence for the present analysis is that no single national reporting regime, however well enforced, can close the dark-data gap on its own: a trial conducted in a jurisdiction with weaker reporting requirements, or a preclinical program that never triggers any jurisdiction\'s clinical-trial reporting obligations at all, remains dark regardless of how rigorously the FDAAA or the EU Clinical Trials Regulation is enforced elsewhere. This reinforces the case, developed further in Section 6.5, for infrastructure that is jurisdiction-agnostic by design --- a registry that accepts a contribution based on the scientific content of a negative result rather than on which country\'s regulatory threshold that result happened to cross.

**6.5 What this apparatus does not reach**

Every mechanism reviewed above shares a common boundary: it operates on the universe of formally registered clinical trials, typically phase II and later, that were substantial enough in scale and regulatory significance to require registration in the first place. This leaves a very large and almost entirely dark layer of biomedical evidence outside its scope:

- Preclinical and translational research --- in vitro and animal studies, target-validation experiments, early pharmacological screening --- which represents, by the \$28 billion figure discussed in Section 4.1, the single largest documented pool of irreproducible and unreported biomedical work, and which is not subject to any clinical trial registry requirement because it does not involve human subjects.

- Early-phase and pilot human studies that are small enough, or exploratory enough, to fall outside formal registration requirements or to be abandoned before reaching a registrable protocol stage.

- Independent researcher and small-laboratory findings that are negative, real, and potentially useful to others, but for which the only realistic disclosure pathway has historically been full journal publication --- an investment of months that is rarely made for a result the investigator does not expect a journal to accept.

- Terminated or abandoned pharmaceutical development programs where internal negative findings (a compound that failed toxicology screening, a target that showed no engagement in an early study) are commercially sensitive enough that they are never voluntarily disclosed, even though the underlying scientific fact --- this approach did not work --- would be of direct value to competitors and academic researchers working on related questions.

This is the specific, currently unaddressed layer of the dark-data problem that motivates the design choices described in Part II: a registry that does not require formal trial-registry status as a precondition for inclusion, that accepts preclinical and early-phase findings on equal footing with completed clinical trials, and that is engineered for a contribution cost measured in minutes rather than months.

**7. Existing Interventions and Their Limits**

Beyond the regulatory apparatus discussed in Section 6, a number of voluntary and infrastructural projects have attempted to address adjacent parts of the dark-data and reproducibility problem. Understanding their design and their limits clarifies the specific niche Dark Data Medicine occupies.

**7.1 PROSPERO and systematic-review registries**

PROSPERO, maintained by the University of York\'s Centre for Reviews and Dissemination, is an international registry of systematic review protocols. It addresses a closely related but distinct problem --- selective reporting and duplication at the level of evidence synthesis, rather than at the level of the primary studies being synthesized --- by making a review team\'s planned methods and outcomes public before the review itself is completed. It does not capture unpublished primary study data.

**7.2 The Open Science Framework and preprint infrastructure**

The Open Science Framework (OSF) and discipline-specific preprint servers such as bioRxiv and medRxiv provide general-purpose, low-friction infrastructure for depositing study materials, data, and manuscripts outside the traditional journal pipeline, and have meaningfully lowered the cost of sharing null and negative results for researchers who choose to use them. They are, by design, general-purpose and unstructured: a negative-result preprint deposited on bioRxiv is discoverable by free-text search but is not captured in a structured, machine-readable schema that allows systematic filtering by intervention type, disease target, or trial phase in the way a purpose-built registry can. They also still require the author to write something close to a full manuscript, which reintroduces much of the time cost that suppresses negative-result reporting in the first place.

**7.3 Registered Reports**

As noted in Section 6.3, Registered Reports remove the outcome-dependent incentive to suppress negative findings for studies that adopt the format from the outset. Their reach is limited by adoption: only a minority of journals offer the format, and it is primarily used prospectively for new studies rather than as a channel for retrospectively surfacing negative results that already exist in a researcher\'s files or in an abandoned development program.

**7.4 Data-sharing mandates and repositories**

Growing numbers of funders and journals now require that underlying trial data be deposited in a repository as a condition of funding or publication. These mandates are valuable but presuppose that a paper is being published in the first place; they do not, on their own, create an incentive or pathway for a negative result that was never going to be written up as a paper at all.

**7.5 The remaining gap**

Taken together, this landscape of registries, mandates, and voluntary platforms has made genuine, measurable progress, particularly for large, formally registered clinical trials. None of it, however, is purpose-built for the specific combination of features needed to capture the largest and darkest layer of the problem identified in Section 6.5: a contribution cost low enough to compete with simply doing nothing; a structured, versioned schema that makes the resulting data queryable and machine-readable rather than merely searchable; a scope that explicitly includes preclinical, translational, and abandoned-program findings rather than only formally registered trials; and a governance and licensing model --- free, public-domain-by-default, community-curated --- designed to maximize reach rather than to monetize access. Part II describes a system designed around exactly this combination of constraints.

**PART II**

**THE SOLUTION: DARK DATA MEDICINE**

**8. Design Philosophy and Guiding Principles**

Dark Data Medicine is an open-source registry built around a deliberately narrow thesis: the fastest way to reduce the volume of unpublished negative results in biomedicine is not to reform the journal system, but to build a parallel, low-friction channel that competes with the default outcome --- silence --- rather than with the journal article. Every design decision described in this section follows from that thesis.

**8.1 Five founding principles**

- Free by default, in every sense of the word. There is no paywall to read the data, no account required to browse it, and the reference dataset is released under CC0-1.0 (public domain dedication) with CC-BY-4.0 available where a contributor wants attribution. The tooling and website are MIT licensed. This removes every access barrier that might otherwise reproduce the exclusivity of the traditional publishing model the project is designed to complement.

- Structured, not narrative. Every entry conforms to a versioned JSON Schema (Draft-07) rather than free text. This is the single most consequential architectural choice in the project: it converts negative results from something that can only be found by a human reading an article into something that can be filtered, aggregated, and cross-referenced programmatically --- by an intervention name, a disease target, an institution type, or a date range --- at a scale no manual literature review could match.

- Radically low contribution cost. The project explicitly targets a submission time measured in minutes, not months. A non-technical contributor can describe a negative result in a short form using plain language; a technical contributor can copy a template, fill in nine required fields, and open a pull request. Neither path requires writing a manuscript, securing co-author sign-off, or navigating peer review.

- Human curation, not unmoderated crowdsourcing. Every entry --- whether it originates from the plain-language form or a direct technical submission --- passes through automated schema validation and then a named human curator before it is merged into the public dataset. This is a deliberate rejection of a fully automated or fully anonymous model: the entire value proposition of the registry depends on the data being trustworthy, and trust requires accountable review.

- Independence from commercial and funding influence. The project\'s governance charter states explicitly that no funder, sponsor, or donor has influence over which entries are accepted, rejected, or featured, and frames this as a hard rule rather than a case-by-case policy. For a registry whose entire purpose is surfacing results that are sometimes commercially inconvenient, this separation is not a nicety --- it is the condition on which the project\'s credibility rests.

**8.2 What the project deliberately does not attempt**

Scope discipline is as important to the design as scope itself. Dark Data Medicine does not attempt to replace ClinicalTrials.gov, the EU Clinical Trials Register, or any statutory reporting regime; it does not attempt to serve as a systematic-review protocol registry in the manner of PROSPERO; and it does not attempt to host full manuscripts, raw datasets, or code in the manner of the Open Science Framework. It occupies a specific, currently under-served niche, described in Section 6.5 and Section 7.5: a structured, freely licensed, low-friction repository for negative and null findings --- including preclinical, translational, and early-phase results that fall outside every other registry\'s scope --- reviewed by accountable human curators and released for anyone to query, cite, or build on.

**9. System Architecture and Data Model**

The technical backbone of the registry is a JSON Schema (Draft-07) that every submitted entry must validate against before it can be merged. This section walks through the schema\'s design and the reasoning behind its key fields, then describes how entries are organized, stored, and versioned.

**9.1 The submission schema**

The schema defines ten required fields and seven optional fields, chosen to capture the minimum information necessary for a negative result to be scientifically useful and independently checkable, without imposing a burden heavy enough to deter a busy clinician or bench scientist from contributing. The required fields are: a unique experiment identifier; a domain classification drawn from a controlled vocabulary (Oncology, Neurology, Pharmacology, Cardiology, Psychiatry, Immunology, Infectious Disease, Endocrinology, or Other); the target disease or condition; a structured description of the tested intervention (its type --- Molecule, Drug, Biologic, Device, Behavioral, Procedure, or Other --- and its name); a one-sentence hypothesis statement; a factual outcome description; a short methodology summary; the submitting institution\'s type; the date the study concluded; and a license selection. Optional fields capture the researcher\'s ORCID iD, the type of source the entry derives from, a source URL for independent verification, an optional contact email, and free-text keywords for discoverability.

| **Field** | **Type** | **Required** | **Purpose** |
|:---|:---|:---|:---|
| experiment_id | string | Yes | Unique identifier; uses public trial IDs (e.g. NCT numbers) where available |
| domain | enum | Yes | Controlled vocabulary across 9 medical domains for filtering and aggregation |
| target_disease | string | Yes | Disease, condition, or cell line under study |
| tested_intervention | object | Yes | Structured type + name (+ optional dosage) of the intervention |
| hypothesis | string | Yes | One-sentence statement of what was being tested |
| outcome | string | Yes | Factual description of the negative/null result |
| methodology_summary | string | Yes | Study design in brief (e.g. "RCT, phase II") |
| researcher_orcid | string | No | Regex-validated ORCID iD for attribution and credit |
| institution_type | enum | Yes | One of six institution categories |
| date_concluded | date | Yes | ISO-format completion date |
| source_type | enum | No | original_submission / public_database_extraction / literature_mining |
| source_url | string | No | Link for independent verification |
| license | enum | Yes | CC0-1.0 or CC-BY-4.0 |
| contact_email_optional | string | No | Never required; opt-in only |
| keywords | array | No | Free-text tags for search and discovery |

*Table 1. Core fields of the Negative Result Submission schema (data/templates/submission_schema.json).*

**9.2 Design rationale for key fields**

Several field choices merit specific explanation. The controlled-vocabulary domain and intervention-type fields are what make the dataset queryable in aggregate rather than merely searchable one entry at a time --- a researcher can ask "what has already been tried against this disease target and failed" as a structured query rather than a hopeful web search. The ORCID field, validated against the standard sixteen-digit ORCID regular expression pattern, is optional but encouraged: it gives contributors a durable, citable credit mechanism without requiring registration on the platform itself. The license field forces an explicit choice at the point of submission rather than leaving licensing ambiguous after the fact, which would otherwise become a downstream liability for anyone trying to reuse the data at scale.

**9.3 Repository organization**

Entries are stored as individual JSON files inside per-domain directories (data/oncology/, data/neurology/, data/pharmacology/, data/cardiology/, data/psychiatry/, data/immunology/, data/infectious_disease/, with data/templates/ holding the canonical schema and submission template). This flat, file-per-entry structure is a deliberate concession to simplicity over database sophistication: it means the entire dataset lives in a plain Git repository, is versioned automatically by Git history, requires no database server to operate, can be cloned and queried offline with ordinary command-line tools, and allows every single change to any entry to be reviewed as an ordinary, auditable pull request diff.

**9.4 Schema versioning and migration**

The governance documentation specifies that schema changes must be proposed through the same issue/pull-request process as any other change, must include a written rationale, and must include a migration plan for entries already in the dataset. This prevents silent schema drift --- a common failure mode in long-lived open datasets where early entries slowly become incompatible with the tooling built for later ones --- by making every schema evolution an explicit, reviewed, and backward-compatible (or explicitly migrated) event.

**10. Governance Model**

A registry whose entire value proposition rests on trustworthiness needs a governance model that is explicit about who decides what gets published and why. Dark Data Medicine\'s governance charter addresses four areas: current decision-making authority, the path to broader governance as the project scales, conflict-of-interest handling, and the separation of funding from editorial decisions.

**10.1 Current structure**

The project is presently maintained by a single founding maintainer and is explicitly independent --- not affiliated with any university, hospital, or research institution unless a specific release states otherwise. Data schema changes require a written rationale and a migration plan and are handled through the standard issue/pull-request process; new domain categories are added only when there is demonstrated need, operationalized as a threshold of five or more pending submissions that do not fit an existing category; and code and tooling changes go through standard pull-request review gated by the automated test suite.

**10.2 Path to distributed governance**

The charter is explicit that single-maintainer governance is a starting state, not an end state: as the registry grows, the stated intent is to move toward a small steering group with representation across medical domains, rather than concentrating data-acceptance authority in one person indefinitely. Contributors who consistently perform high-quality curation work are identified as the natural first candidates for co-maintainer status, and the project provides a standing mechanism --- opening an issue titled to volunteer as a domain curator --- for researchers to put themselves forward. This graduated, contribution-earned path to authority is designed to scale trust in proportion to the size of the community, rather than asking a growing user base to indefinitely trust a single point of failure.

**10.3 Conflicts of interest**

Curators reviewing a submission connected to their own institution or sponsor\'s research are required to disclose this in the review thread. The policy does not disqualify the review outright --- recognizing that in a domain-curator model some degree of subject-matter overlap between reviewer and submitter is inevitable and even desirable --- but requires that the connection be visible to anyone auditing the merge history, consistent with the project\'s broader bias toward radical transparency over the appearance of neutrality.

**10.4 Funding independence**

The project accepts optional personal financial support for the maintainer, structured through a multi-currency donation framework, but the governance charter states as a hard, non-waivable rule that no funder, sponsor, or donor has any influence over which data entries are accepted, rejected, or featured. This is the single most important governance commitment in the document: a negative-results registry that could be commercially influenced would be worse than no registry at all, because it would carry the appearance of independence without the substance of it.

**11. Data Quality and the Validation Pipeline**

Between a submission arriving and an entry becoming part of the public dataset, Dark Data Medicine applies three layers of quality control, described here in the order a submission actually passes through them: automated schema validation, human curator review against a written checklist, and continuous regression testing of the validation logic itself. Figure 1 shows the complete pipeline a submission passes through, end to end.

![](media/662605b6672ef7904374eddcd18adc59f61df073.png){width="6.302083333333333in" height="2.0104166666666665in"}

*Figure 1. The current, fully implemented submission-to-publication pipeline, from initial contribution through public availability.*

**11.1 Automated schema validation**

Every pull request that touches the data/ directory triggers a GitHub Actions workflow (validate-submissions.yml) that installs the jsonschema library and runs the project\'s validate_submission.py script against the changed files. This check runs before any human reviews the content, and a curator is instructed to request changes rather than perform a manual review while the automated check is failing --- ensuring reviewer time is spent on scientific and editorial judgment rather than on catching malformed JSON. We independently reproduced this pipeline against the current seed dataset and confirmed that all entries pass validation and that the script correctly rejects malformed submissions, including missing required fields and invalid controlled-vocabulary values, in the accompanying automated test suite.

**11.2 The human curation checklist**

Once a submission passes automated validation, a named curator applies a written checklist before merging: confirming the automated check is green; screening for any patient-identifiable information (names, dates of birth, medical record numbers, or other identifiers), which triggers immediate rejection and private contact with the submitter; confirming that the outcome field genuinely describes a negative or null result rather than a positive result submitted in error; confirming correct domain classification and relocating the file if necessary; searching existing entries for likely duplicates on the combination of target disease and intervention name; verifying, where claimed, that a source URL actually resolves to a matching public record; and confirming a license has been explicitly set, defaulting to CC0-1.0 where a submitter expressed no objection to public-domain release. Curators are asked to leave an initial response --- approval, requested changes, or a clarifying question --- within seven days of submission, balancing rigor against the risk that a slow review process becomes its own disincentive to contribute.

**11.3 Handling contested submissions**

Not every submission will have an uncontroversial negative outcome; a contributor and a curator may disagree about whether a result was genuinely negative or merely inconclusive. The curation guide directs reviewers not to unilaterally reject in this situation, but to open a discussion thread on the pull request and, where useful, bring in a second reviewer with relevant domain expertise before a final decision is made --- a lightweight, transparent dispute-resolution step appropriate to the project\'s current scale.

**11.4 Batch imports are treated as drafts, never as verified data**

The project includes a ClinicalTrials.gov seed-extractor script capable of pulling candidate entries from the public registry at scale. The curation guide is explicit that entries produced this way are drafts only, must pass through the identical one-at-a-time review checklist as any other submission, may never be bulk-merged without individual review, and must be flagged with a source_type of public_database_extraction so that anyone reading the entry knows it was not independently reviewed by the original researcher. This distinction --- between a scalable sourcing mechanism and a scalable trust mechanism --- is what keeps a growth-oriented feature (automated candidate extraction) from silently degrading the dataset\'s reliability.

**11.5 Continuous testing of the tooling itself**

A pytest-based automated test suite validates both the schema-and-validation logic and the analysis tooling independently of any specific data entry --- confirming, for example, that the schema document is itself valid JSON Schema, that the submission template validates against it, that every seed entry currently in the dataset validates, and that the analysis script correctly counts domains and interventions and degrades gracefully when fields are missing. This suite runs automatically on every pull request via a dedicated GitHub Actions workflow (test-suite.yml), and we independently re-ran it during the preparation of this white paper, confirming all ten tests pass against the current codebase.

**12. The No-Code Contribution Pathway**

A recurring theme in Section 3.4\'s discussion of structural drivers is that the realistic alternative to publishing a negative result is not publishing it in a lesser venue --- it is not publishing it at all, because the friction of any formal writing process exceeds the perceived reward. Dark Data Medicine\'s response to this is to offer two contribution pathways calibrated to two different contributor populations, both converging on the same reviewed, structured output.

**12.1 Pathway one: the plain-language form**

For clinicians and researchers who do not use Git or GitHub, the project\'s contribution documentation describes a short-form submission path: a plain-language form asking what disease or condition was studied, what intervention was tested, what the hypothesis was, what actually happened, a brief description of how the study was conducted, and an optional ORCID iD. An automation layer converts the form response into the standard schema format and opens it as a submission queued for the same human curator review described in Section 11.2. The explicit design goal, stated in the project\'s own contribution guide, is that a contributor should never need to touch GitHub at any point in the process.

**12.2 Pathway two: direct technical submission**

Contributors comfortable with Git and GitHub can copy the canonical submission template, populate it directly using the data dictionary as a field-by-field reference, validate the file locally with a single command-line invocation of the validation script, place it in the correct domain directory, and open a pull request. This pathway trades slightly more initial effort for immediate transparency and control, and is expected to be the primary path for institutional contributors and for the ClinicalTrials.gov-derived draft entries discussed in Section 11.4.

**12.3 Explicit exclusions**

The contribution guide is equally explicit about what the registry will not accept, and this list functions as a second layer of quality control operating even before a submission reaches a curator: no data that could identify an individual patient; no unverified anecdotal claims lacking any methodology; no duplicate entries that merely restate an existing public trial-registry record without adding independent value; and no promotional or marketing content presented as a scientific entry. Stating these exclusions up front, in the same document that invites contribution, is intended to filter out the submissions least likely to survive curation before a contributor invests any time in preparing them.

**13. Technical Infrastructure**

Beyond the data model and governance process, the project ships a small, purpose-built toolchain that turns the raw dataset into something usable by researchers, curators, and the public without requiring anyone to run a database server.

**13.1 Analysis tooling**

A trend-analysis script aggregates the current dataset to answer three standing questions a researcher might have on arrival: which interventions and disease targets recur most often among documented failures, and how submissions are distributed across institution types. Run against the current seed dataset, the script correctly reports domain, intervention, and institution-type frequency counts, confirming the tool functions as intended end-to-end even at the current, intentionally small, illustrative scale.

**13.2 Export and interoperability**

An export script converts the entire structured dataset into a formatted Excel workbook on demand, giving non-programming users --- including many practicing clinicians and hospital administrators --- a familiar interface for exploring the data without needing to write code or queries against the raw JSON files. We validated this export path directly and confirmed it correctly produces a workbook spanning all domains present in the dataset.

**13.3 Search and discovery**

A lightweight, dependency-free static search interface (site/index.html) runs entirely client-side against a generated search index (site/data_index.json), requiring no backend server, no database, and no ongoing hosting cost beyond static file serving. The index is regenerated automatically by a dedicated GitHub Actions workflow (deploy-site.yml) on every push to the main branch and published through GitHub Pages, so the public-facing search interface never drifts out of sync with the underlying dataset. We regenerated the index locally and confirmed it correctly reflects all entries currently in the dataset.

**13.4 Sourcing candidate entries at scale**

The ClinicalTrials.gov seed-extractor script, discussed in its governance context in Section 11.4, provides the mechanism by which the project intends to scale beyond hand-submitted entries: it pulls candidate records from the public registry\'s data for review, explicitly as unverified drafts rather than as data ready for direct inclusion. This is the primary planned mechanism for executing the first item on the project roadmap --- seeding the database with an initial 500 to 1,000 entries mined from public registries including ClinicalTrials.gov, the EU Clinical Trials Register, and PubMed Central.

**13.5 Continuous integration and deployment**

Three GitHub Actions workflows operate the project\'s automation: validate-submissions.yml enforces schema compliance on every data change; test-suite.yml runs the full pytest suite on every pull request and every push to the main branch; and deploy-site.yml rebuilds the search index and publishes the static site on every relevant change. We independently reviewed all three workflow definitions and confirmed they are correctly configured against current GitHub Actions syntax and reference the project\'s own scripts and test suite rather than external or placeholder logic.

**14. Licensing and Legal Framework**

Licensing clarity is a precondition for a dataset that is meant to be reused freely in downstream research, and Dark Data Medicine separates code licensing from data licensing explicitly rather than applying a single blanket license to the whole repository.

**14.1 Code license**

All tooling, scripts, and the website in the repository are released under the MIT License, a permissive license that allows unrestricted reuse, modification, and redistribution, including in commercial contexts, with attribution. This choice maximizes the likelihood that other groups building adjacent tooling --- a competing or complementary registry, an institutional dashboard, a meta-analysis pipeline --- can freely reuse the project\'s validation, export, and search code rather than reimplementing it.

**14.2 Data license**

Individual data entries are released under either CC0-1.0, a public-domain dedication that waives essentially all rights and permits any use without attribution, or CC-BY-4.0, which permits any use provided the original contributor is credited, at the submitting researcher\'s choice, recorded per-entry in the license field described in Section 9.1. Because the schema forces this choice at submission time rather than leaving it implicit, every downstream user of the dataset --- a meta-analyst, a pharmaceutical due-diligence team, a funding-agency portfolio reviewer --- can programmatically filter for entries matching whatever licensing constraints their own use case requires, rather than needing to individually clear rights for each entry they wish to cite.

**14.3 Citation and persistent identification**

The project ships machine-readable citation metadata (CITATION.cff), which GitHub surfaces automatically through a "Cite this repository" interface, and is configured (via a .zenodo.json manifest) to archive tagged releases on Zenodo with a persistent DOI once the repository is connected to a Zenodo account --- the standard mechanism by which software and dataset releases in the open-science ecosystem become formally citable in academic bibliographies, distinct from citing an ever-changing GitHub URL. Individual contributors who supply an ORCID iD are credited by name in a way that survives dataset snapshots and periodic releases, giving them a durable, citable record of their contribution even though the underlying result was never published as a standalone journal article.

**PART III**

**IMPACT, POSITIONING, AND THE ROAD AHEAD**

**15. Use Cases**

A structured negative-results registry is only as valuable as the decisions it actually changes. This section walks through five concrete user populations and how each would plausibly use the system once it reaches meaningful scale.

**15.1 The bench scientist designing a new study**

Before committing months of laboratory time to a target-validation or early pharmacology question, a researcher can query the registry by disease target and intervention type to check whether a similar approach has already been documented as ineffective --- turning what today is an informal, word-of-mouth process (asking colleagues, hoping someone remembers a relevant unpublished result) into a structured, minutes-long search.

**15.2 The clinical trial sponsor scoping a program**

A pharmaceutical or academic sponsor designing a phase II program can use the registry, alongside formal trial registries, as an additional due-diligence layer specifically tuned to catch preclinical and early-phase negative signals that would never appear in ClinicalTrials.gov because no human trial was ever registered.

**15.3 The systematic reviewer and meta-analyst**

As discussed in Section 3.3, meta-analyses that omit unpublished negative trials produce upward-biased effect estimates. A structured, filterable registry of negative results, even a partial one, gives reviewers a new, systematically searchable source to check against publication-bias funnel-plot asymmetry, potentially surfacing entries that would otherwise require personally contacting dozens of trialists to identify.

**15.4 The funding agency and portfolio reviewer**

Funders allocating limited grant budgets across a therapeutic area benefit from visibility into which approaches have already been tried and shown not to work, reducing the risk of funding a proposal that unknowingly repeats prior negative work --- particularly valuable for funders operating across many institutions that do not otherwise share internal negative results with each other.

**15.5 The independent researcher and early-career scientist**

For a researcher without an institutional affiliation, or early in their career, the registry offers something the formal publication system structurally does not: a citable, credited outlet for a negative result obtained outside a large lab, with a contribution cost measured in minutes and a persistent identifier (via ORCID and Zenodo DOI, as described in Section 14.3) that can appear on a CV or grant application.

**16. A Quantitative Framework for Projected Impact**

This section develops, in order-of-magnitude terms, the recoverable-value framework introduced in Section 4.4, to give funders, contributors, and prospective institutional partners a transparent way to reason about the registry\'s potential impact as it scales. We emphasize that the specific figures below are illustrative scenario calculations built from the published estimates cited throughout Part I, not measured outcomes of the current, intentionally small, illustrative seed dataset --- the registry is not yet at a scale where its actual, realized impact could be empirically measured, and any future impact assessment should be conducted independently once a substantial body of curated entries exists.

**16.1 Structure of the estimate**

Recoverable value, V, can be expressed as the product of three quantities: N, the number of negative or null findings generated annually in a given research domain that would otherwise remain permanently undocumented; p, the probability that a given entry in the registry is discovered by a researcher who would otherwise have unknowingly repeated the underlying work; and C, the average cost --- in money, time, or both --- of the repeated work that discovery avoids. Because N, p, and C vary enormously by research stage (a discarded preclinical hypothesis versus a terminated phase III trial), the framework is most useful applied separately to each stage rather than as a single aggregate figure.

**16.2 Illustrative scenario: preclinical research**

Applying the \$28 billion aggregate irreproducibility figure from Section 4.1 as an outer bound on N × C for U.S. preclinical research alone, even a very small realized discovery-and-avoidance rate p --- on the order of a fraction of one percent, reflecting the registry\'s early stage, incomplete domain coverage, and the reality that most preclinical waste stems from causes other than an undocumented prior negative finding --- corresponds to tens of millions of dollars in avoided redundant spending per year once the registry reaches meaningful adoption within even a single well-covered subdomain. We present this only as an illustration of how small the required discovery-and-avoidance rate is for the exercise to be worthwhile, not as a specific forecast.

**16.3 Illustrative scenario: clinical trials**

At the clinical stage, C is far larger per instance --- a single redundant phase II trial can cost from several million to several tens of millions of dollars --- but N and p are both smaller, since clinical trials are already partially covered by formal registries. The registry\'s marginal value at this stage is concentrated in the subset of clinical evidence that formal registries structurally miss: terminated early-phase pilot studies, abandoned programs, and trials conducted outside jurisdictions with strong reporting mandates. Avoiding even a handful of redundant trials per year across a mature, well-adopted registry would represent a return many multiples of the registry\'s total operating cost, which --- as described in Section 17 --- is negligible by comparison, since the infrastructure runs on free-tier static hosting and volunteer curation rather than paid infrastructure or staff.

**16.4 Non-monetary impact**

Not all value is financial. Reduced re-exposure of clinical trial participants to interventions already known elsewhere to be ineffective, discussed in Section 4.3, is a harm-avoidance benefit that resists a clean dollar figure but is, from a research-ethics standpoint, at least as important as the economic case. Faster negative hypotheses elimination also compounds: a field that can rule out unproductive directions more quickly reallocates talent and funding toward more promising ones sooner, an effect that is directionally clear even though its magnitude is inherently difficult to estimate in advance.

**16.5 A worked illustrative example**

To make the framework in Section 16.1 concrete, Table 3 walks through a single hypothetical subdomain --- early-phase oncology target validation --- using round, clearly hypothetical numbers chosen only to illustrate the arithmetic, not to forecast actual outcomes. We stress again that these are illustrative inputs, not measured or projected figures for the actual registry.

| **Parameter** | **Illustrative value** | **Basis** |
|:---|:---|:---|
| N --- annual undocumented negative preclinical findings in the subdomain | 2,000 | Hypothetical, order-of-magnitude only |
| p --- probability a given finding is discovered and avoids repeated work | 0.5% | Deliberately conservative, reflecting early-stage adoption |
| C --- average cost of the repeated work avoided per discovery | \$150,000 | Approximate low-end cost of a small preclinical study |
| V = N × p × C --- illustrative annual recoverable value | \$1,500,000 | Arithmetic product of the above |

*Table 3. Illustrative, purely hypothetical worked example of the recoverable-value framework from Section 16.1, for a single research subdomain.*

Even under these deliberately conservative assumptions, the illustrative recoverable value for a single subdomain exceeds the registry\'s entire marginal operating cost, described in Section 20.1, by a wide margin. The exercise is meant to show that the framework does not require optimistic assumptions to justify the infrastructure investment --- it requires only that a very small fraction of otherwise-repeated work be avoided.

**17. Ethical Considerations**

A registry designed to surface information some parties would prefer remained undisclosed carries a distinct set of ethical and governance risks that a purely technical description of the system would understate. We address the most significant ones directly.

**17.1 Patient privacy**

The single most operationally important ethical safeguard in the system is the exclusion of any patient-identifiable information, enforced at two layers: explicit instruction to contributors in the contribution guide, and an explicit, mandatory check in the human curator checklist that triggers immediate rejection and private contact with the submitter if any identifier --- a name, a date of birth, a medical record number --- appears in any field. Because the schema\'s outcome and methodology fields are free text, this is fundamentally a human-judgment safeguard rather than a technical one, and its reliability is bounded by curator diligence; as the registry scales beyond a single maintainer, maintaining this standard consistently across a distributed curator base, as anticipated in Section 10.2, will require explicit onboarding and, plausibly, periodic audit.

**17.2 Accuracy and the risk of misleading negative claims**

A negative result submitted in good faith can still be wrong --- underpowered, poorly controlled, or reflecting a flawed methodology rather than a true absence of effect. The curation checklist\'s requirement that curators confirm a genuinely negative or null outcome addresses submission-level miscategorization, but it does not, and by design cannot, adjudicate methodological quality the way a full peer-review process would. The registry should therefore be understood, and is explicitly positioned throughout this paper, as a signal to prompt further investigation --- a lead worth checking against the cited source and, where possible, the original data --- rather than as an independently peer-reviewed evidentiary claim on par with a published, reviewed article. We recommend this framing be stated explicitly and prominently wherever registry data is surfaced or cited, including in any future systematic-review methodology that incorporates it.

**17.3 Dual-use and commercial sensitivity**

A structured record that a particular compound failed against a particular target is scientifically valuable precisely because it is also commercially informative --- to competitors, to short-sellers, and to the sponsor\'s own future licensing negotiations. This creates a genuine tension: the same disclosure that helps the field avoid redundant work also creates a disincentive for commercially motivated contributors to submit. The project\'s response, described in Section 8.1 and Section 10.4, is to lean entirely into independence and free licensing rather than attempting to build a permissioned or tiered-access model that might otherwise mitigate this disincentive; this is a deliberate trade-off, favoring maximum reach and trust for the data that is contributed over maximizing the total volume of commercially sensitive contributions specifically.

**17.4 Misuse risk**

A public, machine-readable database of failed interventions could in principle be misused --- for instance, to selectively cite negative findings out of context in a way that misrepresents the overall state of evidence on a therapeutic question, a concern structurally analogous to the selective-citation risk that already exists with the positive-result literature. The project\'s mitigations are the same tools available to any open dataset: transparent provenance (the source_type and source_url fields described in Section 9.1), a visible curation and revision history through ordinary Git version control, and public documentation of the data\'s known limitations, most importantly its current small scale and its status as curated-but-not-peer-reviewed evidence.

**18. Comparative Positioning**

Table 2 summarizes how Dark Data Medicine relates to the principal adjacent projects and regulatory mechanisms discussed throughout Part I, making explicit the specific gap the registry is designed to fill rather than claiming to supersede any of them.

| **System** | **Primary Scope** | **Requires Formal Trial Status** | **Structured / Machine-Readable** | **Captures Preclinical Findings** | **Access Cost** |
|:---|:---|:---|:---|:---|:---|
| ClinicalTrials.gov / WHO ICTRP | Registered clinical trials, all outcomes | Yes | Partially | No | Free |
| FDAAA / EU CTR reporting mandates | Registered trials meeting legal thresholds | Yes | Partially | No | Free (statutory) |
| PROSPERO | Systematic review protocols | N/A (review-level) | Partially | No | Free |
| OSF / bioRxiv / medRxiv | Any research output, incl. negative results | No | No (free text) | Yes, if authors choose | Free |
| Registered Reports (journals) | New prospective studies at adopting journals | No | No (narrative) | Rarely | Journal-dependent |
| Dark Data Medicine | Negative/null results, any research stage | No | Yes (JSON Schema) | Yes, explicitly in scope | Free (CC0/CC-BY) |

*Table 2. Comparative positioning of Dark Data Medicine against adjacent registries and mechanisms.*

The distinguishing combination is the bottom-right cluster of the table: Dark Data Medicine is the only entry that combines a structured, machine-readable schema with an explicit, in-scope acceptance of preclinical and non-registered findings and a fully free, public-domain-by-default licensing model. This is not a claim of superiority --- each of the other systems solves a problem this registry does not attempt to solve, several of them (PROSPERO, formal trial registries) with legal or institutional authority the registry does not have and does not seek --- but a claim of complementarity, addressing the specific residual gap identified in Sections 6.4 and 7.5.

**19. Roadmap and Scaling Strategy**

The project\'s own published roadmap, reviewed and confirmed accurate as part of the diligence for this white paper, lays out five sequential milestones. We reproduce and elaborate on them here, with implementation notes drawn from our review of the current codebase.

1.  Seed the database with the first 500--1,000 entries mined from public registries (ClinicalTrials.gov, the EU Clinical Trials Register, and PubMed Central). The technical mechanism for this --- the ClinicalTrials.gov seed-extractor script --- already exists and is functional; the rate-limiting step, by design (Section 11.4), is human curator review of each draft, not data sourcing.

2.  Publish a searchable web interface via GitHub Pages. The underlying static search site and its automated deployment pipeline are already built and functioning end-to-end, as verified in Section 13.3; this milestone is substantially a matter of populating it with the entries produced by milestone one.

3.  Set up the no-code submission form and its automation pipeline. The contribution guide already documents the intended plain-language form workflow described in Section 12.1; the form itself and its automated conversion into schema-compliant draft submissions remains to be built and connected.

4.  Achieve the first Zenodo-archived data release with an official DOI. The citation and archival metadata (CITATION.cff, .zenodo.json) are already in place, as described in Section 14.3; this milestone requires connecting the repository to a Zenodo account and cutting a first tagged release once the dataset has grown beyond its current illustrative scale.

5.  Outreach to university labs and open-science communities such as PLOS One, F1000Research, and PeerJ, to establish the registry as a recognized complementary disclosure channel alongside traditional publication --- the step on which the project\'s long-run adoption, and therefore its long-run impact, ultimately depends.

**19.1 Sequencing rationale**

The roadmap is sequenced so that credibility-building steps (a working search interface, a first DOI-archived release) precede the outreach effort that depends on them; asking a university lab or a journal community to engage with a registry that cannot yet be searched or formally cited would be premature. This sequencing is consistent with the governance model\'s own emphasis, described in Section 10.2, on earning broader trust and authority incrementally rather than claiming it in advance.

**19.2 Recommended near-term priorities**

Based on our review of the current state of the repository, we recommend three near-term priorities beyond the published roadmap: first, populating the currently placeholder Endocrinology domain --- already present in the schema\'s controlled vocabulary but without a corresponding seed entry or data directory --- to ensure schema and dataset stay synchronized; second, building the no-code submission-form automation referenced in milestone three, since this pathway is likely to be the primary channel for the non-technical clinician contributors the project explicitly targets; and third, establishing the small, domain-representative steering group described in the governance charter\'s path to broader governance once the dataset grows past a size a single curator can review within the target seven-day response window.

**20. Sustainability and Funding Model**

Because the project\'s credibility depends on funding independence (Section 10.4), its sustainability model is deliberately minimal rather than venture-funded or subscription-based.

**20.1 Infrastructure cost profile**

The technical architecture described in Part II is chosen specifically to minimize ongoing operating cost: a static, dependency-free search site hosted on free-tier GitHub Pages; a flat-file, Git-versioned dataset requiring no database server; and automation implemented entirely through free-tier GitHub Actions workflows. At the project\'s current scale, and for a considerable distance beyond it, the marginal cost of operating the registry approaches the cost of a maintainer\'s time rather than any significant infrastructure spend.

**20.2 Voluntary support**

The project accepts optional personal support for the maintainer through a documented, multi-currency donation framework (FUNDING.md), explicitly separated --- per the hard rule described in Section 10.4 --- from any influence over editorial or data-acceptance decisions. This model mirrors the funding structure of comparable independent open-source and open-data projects, where sustainability is treated as a function of community goodwill and low fixed costs rather than of monetizing access to the data itself.

**20.3 Long-run institutional pathways**

As the registry matures past the single-maintainer stage described in Section 10.1, plausible long-run sustainability pathways --- consistent with, though not yet formally adopted by, the project\'s stated governance trajectory --- include fiscal sponsorship by an existing open-science non-profit, grant funding from research-integrity-focused foundations, or formal affiliation with a university open-science center, each of which would need to be evaluated against the funding-independence principle in Section 10.4 before adoption.

**21. Risks and Limitations**

An honest assessment of the project\'s current state must acknowledge its limitations candidly, both for scientific integrity and because credibility with the very research community the registry needs to attract depends on not overselling an early-stage effort.

**21.1 Current dataset scale**

As of this white paper\'s preparation, the registry\'s dataset consists of seven entries --- one per populated domain --- each explicitly and correctly labeled in its keywords as an illustrative example rather than a reviewed real-world submission. This is by design, demonstrating the schema and tooling end-to-end ahead of the bulk-import and outreach milestones described in Section 19, but it means the registry does not yet provide the volume of real evidence needed to deliver the use cases described in Section 15 or the impact scenarios described in Section 16. Any characterization of the registry as already containing a substantial body of real negative-result evidence would be inaccurate at this stage.

**21.2 Single-maintainer bottleneck**

The governance model\'s own stated seven-day curator-response target and its explicit dependency on a single founding maintainer, described in Section 10.1, represents a near-term scaling ceiling: a meaningful bulk import of the roadmap\'s target 500--1,000 entries would very likely exceed what a single curator can review within that target window without either recruiting the domain co-curators anticipated in Section 10.2 or relaxing review rigor, the latter of which would directly undermine the trust the project is built on.

**21.3 Reliance on self-reported, uncorroborated submissions**

For entries with a source_type of original_submission, the registry has no independent means of verifying that a described study was actually conducted as described beyond the curator\'s judgment and any source materials the submitter voluntarily provides. This is an inherent limitation of any low-friction, non-peer-reviewed disclosure channel and should be weighed by any downstream user of the data, consistent with the framing recommended in Section 17.2.

**21.4 Coverage bias risk**

A registry that grows primarily through voluntary submission and English-language public registry mining risks systematically under-representing negative results from institutions, countries, and languages with less awareness of, or access to, the platform --- potentially reproducing, in a new form, exactly the kind of non-random gap in the evidence base the project exists to close. Deliberate multilingual outreach and partnership with research communities outside the initial English-speaking and U.S.-centric registry ecosystem should be an explicit component of the outreach milestone described in Section 19.

**21.5 No substitute for peer review or regulatory reporting**

We reiterate, in the context of risk rather than design, the scope discipline described in Section 8.2: this registry does not and should not be treated as satisfying any statutory reporting obligation, and it does not carry the evidentiary weight of a peer-reviewed publication. Positioning it as anything more than a complementary, lower-barrier disclosure channel would misrepresent both what it currently is and what it is realistically capable of becoming.

**21.6 Schema minimalism as a known, deliberate constraint**

The current schema (Appendix A) is intentionally minimal --- ten required fields, no persistent identifiers beyond an optional ORCID, no statistical detail beyond free text, and no machine-readable failure taxonomy. This is appropriate for a version 1.0 system optimized for the lowest possible contribution barrier (Section 8.1), but it is a real limitation for the use cases described in Section 15.3 (formal meta-analysis) and Section 22.4 (funder portfolio review), which need statistically poolable data and standardized failure classification the current schema cannot supply. Part IV sets out a detailed, explicitly-labeled-as-proposed version 2.0 agenda --- an extended metadata schema, a knowledge-graph layer, a failure ontology, AI-native semantic search, and a formal evidence-quality model --- addressing this gap directly, sequenced deliberately after the current roadmap\'s dataset-growth milestones (Section 31).

**22. Stakeholder Analysis and Adoption Pathways**

Infrastructure of this kind succeeds or fails on adoption, not on engineering quality alone. This section examines the incentives, likely objections, and adoption pathway for each major stakeholder group, since the roadmap in Section 19 depends on each of them engaging with the registry in a specific way.

**22.1 Individual researchers and clinicians**

For the individual contributor, the calculus is straightforward once the contribution cost is genuinely low: a researcher loses little by spending a few minutes documenting a negative result they have already obtained, particularly when doing so yields a durable, ORCID-linked, potentially DOI-citable credit. The primary adoption barrier is not incentive but awareness --- most researchers have never been told that a low-friction disclosure channel for negative results exists, because until recently none did. This places the outreach milestone in Section 19 at the center of individual-level adoption, more than any further product refinement.

**22.2 Academic institutions and research offices**

University research offices and technology-transfer units are natural institutional partners: they already have an interest in avoiding duplicated internal spending across laboratories working on related questions, and several already maintain internal, unpublished registries of negative departmental findings for exactly this reason. A registry that offers a public-facing, citable outlet for a subset of that internal knowledge --- the subset cleared for public release --- could plausibly be adopted as a recommended disclosure channel within institutional open-science policies, particularly at institutions that already mandate data-sharing or preprint deposition as a condition of internal funding.

**22.3 Pharmaceutical and biotechnology sponsors**

As discussed in Section 17.3, commercial sponsors face a structural disincentive to disclose negative findings that a purely voluntary registry cannot fully overcome. The more plausible commercial adoption pathway is indirect: sponsors using the registry as a due-diligence and portfolio-scoping tool (Section 15.2) even while contributing sparingly themselves, and, over a longer horizon, sponsors disclosing findings for abandoned or deprioritized programs where the commercial sensitivity has meaningfully declined --- a pattern already observed, on a smaller scale, in some companies\' voluntary disclosure of discontinued-compound libraries to academic screening consortia.

**22.4 Funders and research-integrity organizations**

Funding agencies and research-integrity-focused foundations have the clearest institutional incentive to support this kind of infrastructure, since redundant funding of already-answered questions is a direct, auditable cost to their own portfolios. Funder engagement could plausibly progress from simple public endorsement, through requiring or recommending registry deposition as a grant closeout condition analogous to existing data-sharing mandates, to direct financial support for curation capacity as the registry\'s institutional sustainability model (Section 20.3) matures.

**22.5 Journals and the scholarly publishing ecosystem**

Rather than positioning the registry as a competitor to journals, the more productive relationship --- consistent with the scope discipline described in Section 8.2 --- is complementary: journals could reference relevant registry entries during peer review as a check on undisclosed prior negative work relevant to a submitted manuscript, and could encourage authors to deposit negative sub-findings from a study (secondary endpoints, abandoned arms) that would not otherwise merit a standalone publication but are exactly what the registry\'s schema is built to capture.

**22.6 Patients and patient-advocacy organizations**

Patient-advocacy organizations, particularly in disease areas with active and engaged research communities, have historically been effective champions of clinical-trial transparency generally, including support for the AllTrials campaign discussed in Section 6.3. The same constituency has a direct interest in a registry that reduces the likelihood of trial participants being enrolled in studies repeating already-known-ineffective interventions, as discussed in Section 4.3, making patient organizations a plausible and motivated outreach partner independent of the academic and commercial channels discussed above.

**23. Frequently Asked Questions**

**Is this a peer-reviewed publication venue?**

No. As discussed in Sections 8.2 and 17.2, Dark Data Medicine is a curated, schema-validated registry, not a peer-reviewed journal. Entries pass automated validation and human curator review for completeness, plausibility, and absence of identifiable patient information, but they do not undergo the methodological peer review a journal article receives. The registry should be treated as a structured lead worth following up, not as a citation-equivalent replacement for a reviewed publication.

**Can I submit a positive result?**

No. The schema and curation checklist are both built specifically around negative and null findings; a curator who receives a submission describing a positive outcome is instructed to redirect the contributor toward conventional publication or an appropriate preprint server rather than merge it into the registry.

**Does submitting to the registry count as prior publication that could block a future journal submission?**

This depends on the policies of the specific journal a contributor later approaches, and the project\'s documentation appropriately does not make blanket legal or editorial guarantees on this point. Because entries are structured, brief factual records rather than full manuscripts, many journals treat data-repository or registry deposition differently from full-text publication, similar to existing norms around preprints and trial-registry result postings --- but a contributor with a specific target journal in mind should check that journal\'s own policy before submitting a result they intend to also publish in full.

**What stops someone from submitting fabricated negative results?**

The curation checklist described in Section 11.2 --- plausibility review, source-URL verification where available, and duplicate-checking --- provides a first line of defense, and the fully transparent, versioned Git history means every entry\'s provenance and edit history remains permanently auditable. As with any low-friction, community-curated resource, this defense is not absolute, which is precisely why Section 17.2 recommends the registry be treated as a signal for further investigation rather than as independently verified fact.

**Why not just require everyone to use ClinicalTrials.gov instead?**

Because, as documented in Sections 6.4 and 6.5, ClinicalTrials.gov and equivalent registries are structurally scoped to registrable human clinical trials, and cannot accept the preclinical, translational, and abandoned-program findings that represent the majority of the dark-data problem by volume. The two systems are complementary, not competing: entries with an existing NCT number are encouraged to reference it in the experiment_id or source_url fields precisely so the two records reinforce rather than duplicate each other.

**How is this different from just posting a negative result on a personal blog or on X / Twitter?**

Structure and permanence. A blog post or social-media post is not machine-readable in a way that allows systematic querying by disease target or intervention type, is not covered by an explicit, enforced license, and has no guaranteed persistence or curation. The schema, licensing, and Zenodo-archival mechanisms described in Sections 9 and 14 are what convert an informal disclosure into a durable, citable, discoverable piece of the scientific record.

**Who is legally responsible for the accuracy of a submitted entry?**

The submitting contributor is responsible for the factual accuracy of what they submit, consistent with standard norms for any self-reported scientific disclosure; the curator\'s role, per Section 11.2, is to screen for completeness, plausibility, and privacy compliance, not to independently re-run or audit the underlying study. This division of responsibility mirrors, at a lighter weight, the author-responsibility model used by preprint servers such as bioRxiv and medRxiv.

**Can an institution submit on behalf of a researcher who has left?**

The contribution guide does not currently address this scenario explicitly; based on the schema\'s design, an institutional research office could submit an entry using institution_type rather than an individual ORCID, with source_type set to original_submission, provided the underlying study details are accurate and no patient-identifiable information is included.

**24. Conclusion**

The biomedical research enterprise spends tens of billions of dollars a year, in the United States alone, on work that turns out to be irreproducible or that unknowingly repeats a question already answered elsewhere. A meaningful share of that waste is not a failure of scientific rigor but a failure of information architecture: the answer existed, was honestly obtained, and simply never became visible outside the team that produced it. Two decades of registries, reporting mandates, and voluntary transparency campaigns have made genuine progress against the visible, formally registered layer of this problem, and this paper does not argue for abandoning or replacing any of that infrastructure. It argues that a large, currently dark layer beneath it --- preclinical findings, abandoned early-phase programs, small-laboratory negative results --- remains almost entirely outside the reach of every mechanism reviewed in Part I, and that this layer is large enough, by the economic estimates surveyed in Section 4, to be worth addressing directly.

Dark Data Medicine is a modest, concrete answer to that gap: a schema-validated, freely licensed, human-curated registry engineered specifically to make contributing a negative result take minutes rather than months. We have reviewed its architecture, governance, and quality-control pipeline in detail, verified that its current tooling functions correctly end-to-end, and been equally direct about its present limitations --- chief among them that it remains, at this writing, an illustrative proof of concept rather than a populated evidence base. Closing that gap between concept and scale is squarely the work described in the roadmap in Section 19, and it depends less on further engineering than on the research community\'s willingness to treat depositing a negative result as a normal, minutes-long final step of a study, in the same way registering a trial before it begins has become normal practice over the past two decades.

Science already produces the evidence needed to save the next research team from walking down a corridor that leads nowhere. The remaining task is almost entirely one of infrastructure and habit: giving that evidence somewhere free, structured, and findable to live.

**PART IV**

**EXTENDING THE ARCHITECTURE: A RESEARCH AGENDA FOR VERSION 2.0**

**25. Scope of This Part: What Is Built Versus What Is Proposed**

Parts I through III described Dark Data Medicine as it presently exists: a minimal, deliberately lightweight schema; a flat-file, Git-versioned dataset; and a static keyword search index --- all independently verified to function correctly in Appendix F. That minimalism was, and remains, a defensible design choice for a version 1.0 system whose primary goal is to prove that a low-friction disclosure channel can exist at all (Section 8.1). It is also, as a piece of infrastructure meant to serve a global research community into the next decade, insufficient on its own. A ten-field JSON schema with a static search index cannot support provenance tracking, statistical meta-analysis, cross-registry interoperability, or machine-assisted discovery at scale.

This part sets out, deliberately separated from Parts I--III, a concrete version 2.0 research agenda addressing five specific gaps: an impoverished metadata schema (Section 26), the absence of a semantic knowledge-graph layer (Section 27), the absence of a standardized ontology for why an experiment failed (Section 28), the absence of AI-native discovery tooling (Section 29), and the absence of a formal evidence-quality model (Section 30). Every proposal below is labeled explicitly as planned rather than built, consistent with the honesty standard set in Section 21, and each is positioned against the concrete constraints --- principally, the single-maintainer governance stage described in Section 10.1 --- that determine how quickly it can realistically be implemented.

![](media/74497afb634d1a1ce1e84c578287c5e1295cf4d1.png){width="6.0in" height="5.8125in"}

*Figure 2. Proposed four-layer architecture. Solid blue boxes are built and independently verified (Appendix F); dashed red boxes are the version 2.0 proposals developed in this Part.*

**26. A Richer Metadata Schema (Version 2.0 Proposal)**

The current schema (Appendix A, Appendix G) captures the minimum needed to make a negative result findable and minimally interpretable: what was tested, against what, and what happened. It does not capture the metadata a systematic reviewer, a funder auditing reproducibility, or a meta-analyst running a formal synthesis would need to weight, verify, or statistically combine an entry. Table 4 proposes an extended field set organized by function, each justified against a specific downstream use case rather than added for its own sake.

| **Category** | **Proposed field(s)** | **Why it matters** |
|:---|:---|:---|
| Persistent identifiers | doi, protocol_doi, grant_id, funder_ror_id | Links an entry to its formal record of funding and pre-registration, enabling audit trails and funder-level reproducibility tracking (Section 22.4). |
| Regulatory / ethical | ethics_approval_id, irb_name | Distinguishes human-subjects research reviewed by an ethics body from preclinical work, and supports the privacy-screening duty described in Section 17.1. |
| Statistical detail | sample_size, effect_size, confidence_interval, statistical_test, p_value | The current outcome field is free text; a meta-analyst cannot pool free text. These fields make an entry usable in a formal, quantitative synthesis (Section 15.3). |
| Bayesian framing | bayes_factor, prior_specification | Complements frequentist statistics with an explicit strength-of-evidence-against-the-hypothesis framing, addressed further in Section 30.2. |
| Reproducibility and provenance | raw_dataset_url, code_repository_url, replication_status, reproducibility_score, provenance_chain | Connects a registry entry to the artifacts (data, code) needed to actually attempt reproduction, directly addressing the \$28 billion irreproducibility problem quantified in Section 4.1. |
| Interoperability | fair_score, ontology_ids (disease, intervention, failure reason) | Machine-actionable links to standard biomedical ontologies (Section 27) and a self-reported FAIR-compliance indicator, enabling cross-registry federation. |

*Table 4. Proposed Version 2.0 metadata extensions, organized by function. None of these fields exist in the current, deployed schema (Appendix A).*

**26.1 Why these fields were not in Version 1.0**

Every field in Table 4 adds real value and real friction simultaneously, and the friction is not evenly distributed: a well-funded, ethics-board-reviewed phase III trial can supply a DOI, a grant ID, and an ethics approval number in seconds, while an independent researcher\'s discarded preclinical pilot, exactly the kind of contributor the no-code pathway in Section 12 exists to serve, may have none of these things. Adding twenty required fields to the current schema would directly contradict the founding principle of radically low contribution cost (Section 8.1) and would systematically exclude the least-resourced, least-institutionally-supported contributors --- precisely the population most likely to be sitting on undocumented negative results in the first place.

**26.2 A staged rollout, not a rewrite**

The recommended migration path is additive and entirely optional at the field level: every field in Table 4 should be introduced as an optional property in a minor schema version, never a required one, with the validation script updated to accept but not mandate them. A submission using only the current ten required fields should continue to validate under Version 2.0 exactly as it does today. This preserves the low-friction guarantee for the no-code pathway while giving institutional, better-resourced contributors --- precisely the audience described in Section 22.2 and 22.3 --- a way to supply materially richer, more analyzable entries. The governance charter\'s existing requirement that any schema change include a written migration plan (Section 9.4, Appendix C) applies directly and without modification to this rollout.

**27. Toward a Knowledge Graph: RDF, OWL, and SPARQL**

The flat-file, Git-versioned data layer described in Section 9.3 is well suited to its current scale and purpose: it is simple, requires no server, and makes every change auditable. It does not, however, support the kind of query a mature evidence infrastructure needs to answer well --- for example, "show me every documented negative result for any Bruton\'s tyrosine kinase inhibitor across any indication, cross-referenced against entries that also report a specific adverse-event class." Answering that query over flat JSON files requires writing bespoke code for every new question. Answering it over a knowledge graph is a single, declarative query.

**27.1 Why RDF and OWL, specifically**

The Resource Description Framework (RDF) represents data as subject--predicate--object triples --- for example, (Entry ONC_2025_0001) ---(testedIntervention)→ (Example_Compound_A) --- which is a natural fit for the relational, cross-referencing questions a negative-results registry exists to answer. The Web Ontology Language (OWL), layered on top of RDF, allows formal class hierarchies and logical constraints to be defined --- for instance, that every instance of FailureReason must belong to exactly one of the six top-level branches proposed in Section 28 --- enabling automatic consistency checking that a flat JSON schema cannot express. Both are mature, widely adopted W3C standards already used across the biomedical semantic-web ecosystem, including by the Open Biological and Biomedical Ontology (OBO) Foundry, Bioschemas, and major knowledge graphs such as Wikidata\'s biomedical subgraph --- meaning a Dark Data Medicine knowledge graph would not be inventing new infrastructure so much as joining an existing, well-tooled ecosystem.

![](media/7872e58da6b38325f27d8eb1f143a02ef87b5742.png){width="6.302083333333333in" height="2.8854166666666665in"}

*Figure 3. Illustrative RDF representation of a single registry entry, showing internal properties (solid) and links to external ontologies and databases via owl:sameAs (dashed).*

**27.2 Illustrative Turtle representation**

The following Turtle (RDF serialization) snippet illustrates, purely for illustration and not as shipped code, how the oncology seed entry reproduced in Appendix E could be represented as a graph rather than a flat file:

@prefix ddm: \<https://darkdatamedicine.org/ontology#\> .
@prefix mondo: \<http://purl.obolibrary.org/obo/MONDO\_\> .
ddm:ONC_2025_0001 a ddm:NegativeResultEntry ;
ddm:testedIntervention ddm:Example_Compound_A ;
ddm:targetsDisease ddm:NSCLC ;
ddm:hasFailureReason ddm:Statistical_NonSignificant ;
ddm:hasEvidenceQuality \"Moderate\"\^\^ddm:GRADERating ;
ddm:dateConcluded \"2024-06-01\"\^\^xsd:date .
ddm:NSCLC owl:sameAs mondo:0005233 .

**27.3 SPARQL as the query layer**

A knowledge-graph backend would expose a public SPARQL endpoint alongside, not instead of, the existing static search interface (Section 13.3) --- a query language purpose-built for exactly the cross-referencing questions described above, and one already familiar to bioinformaticians who query Wikidata, UniProt, or the OBO Foundry ontologies directly. This is explicitly listed as a planned, not built, component in Figure 2.

**27.4 Sequencing relative to the current architecture**

Introducing a knowledge graph does not require discarding the flat-file dataset; the recommended path, shown as a dashed ingestion edge in Figure 2, is to treat the Git-versioned JSON files as the authoritative source of record --- preserving the auditability and simplicity described in Section 9.3 --- with a periodic, automated conversion step that maps schema fields to RDF triples and loads them into a triple store, keeping the semantic layer synchronized with, and clearly derivative of, the underlying dataset rather than an independent source of truth that could drift out of sync with it.

**28. A Failure Ontology for Negative Results**

The current schema\'s outcome field is unconstrained free text: a curator or contributor writes a sentence describing what happened, and there is no controlled vocabulary for why it happened. This is workable for a human reading one entry at a time; it is unworkable for the aggregate queries described in Section 27 --- a researcher cannot ask "show me every negative oncology result attributable to a safety signal rather than a lack of efficacy" if that distinction only exists as an unstructured sentence.

**28.1 A proposed six-branch taxonomy**

Figure 4 proposes a top-level taxonomy of six failure-reason branches --- Statistical, Biological, Translational, Safety, Operational, and Confirmatory --- each with representative leaf terms, designed as a starting classification rather than a finished ontology. The branches are chosen to be mutually informative for the use cases in Section 15: a funder scoping a portfolio cares most about the Biological/Translational distinction (does the target not work, or did the model simply not predict the target correctly), while a trial sponsor cares most about the Statistical/Operational distinction (was the hypothesis wrong, or did the trial simply fail to execute).

![](media/c6881876da0648e86eec96a4317137b7f1e9a630.png){width="5.302083333333333in" height="7.385416666666667in"}

*Figure 4. Proposed six-branch failure-reason taxonomy with illustrative leaf terms (Version 2.0 proposal; not yet implemented in the current schema).*

**28.2 Alignment with existing biomedical ontologies rather than a new one from scratch**

Building a fully independent ontology would be both slower and less interoperable than mapping onto ontologies the field already uses. The Ontology of Adverse Events (OAE) already provides a controlled vocabulary for the Safety branch; the Ontology for Biomedical Investigations (OBI) provides controlled terms for study design that overlap substantially with the Operational branch; and disease and intervention terms throughout the registry should resolve, as illustrated in Figure 3, to existing identifiers in MONDO (disease), ChEBI or ChEMBL (small molecules), and the Human Phenotype Ontology (HPO) where relevant, rather than maintaining a parallel, registry-specific vocabulary for concepts other ontologies already standardize well. The taxonomy proposed here is intended to be submitted, once validated against a larger body of real entries, to the OBO Foundry\'s review process for a formal, citable ontology release, consistent with how comparable domain-specific ontologies in this ecosystem have been developed.

**28.3 Curator workflow implications**

Introducing a controlled failure-reason field would extend, not replace, the human curation checklist described in Section 11.2: a curator would select the appropriate branch and leaf term during review, using the free-text outcome field as supporting evidence rather than as the queryable record itself. Ambiguous cases --- an entry that is plausibly both Statistical and Operational, for instance an underpowered trial that was also terminated early for recruitment failure --- should be permitted multiple failure-reason tags rather than forced into a single branch, consistent with how real biomedical ontologies commonly permit multiple parent classification.

**29. AI-Native Discovery: Semantic Search and RAG**

The static, dependency-free search interface described in Section 13.3 performs keyword matching against the generated index. This is appropriate for its current scale and honest about its limits, but keyword search cannot answer a query phrased in a researcher\'s own words rather than the registry\'s exact vocabulary --- "what has been tried for treatment-resistant depression that didn\'t work" will not reliably surface an entry whose outcome field says "no significant between-group difference in MADRS score change," even though the two are describing the same finding.

**29.1 Embeddings and vector search**

A version 2.0 discovery layer should generate a dense vector embedding for each entry\'s combined hypothesis, outcome, and methodology text using an off-the-shelf biomedical sentence-embedding model, store those vectors in a lightweight vector index, and expose semantic --- meaning-based rather than keyword-based --- search alongside the existing keyword index rather than replacing it. This is now standard practice across biomedical literature search tools and requires no proprietary infrastructure: several open-weight biomedical embedding models are freely available and could run within the same free-tier-hosting constraint that governs the project\'s sustainability model (Section 20.1).

**29.2 Retrieval-augmented generation, and its risks**

Retrieval-augmented generation (RAG) --- using a large language model to synthesize a natural-language answer grounded in retrieved registry entries, with citations back to the specific entries used --- is the natural next layer once semantic search exists, and would let a researcher ask a compound question ("what negative results exist for JAK inhibitors in inflammatory bowel disease, and what failure reasons do they share?") and receive a synthesized, source-linked answer rather than a ranked list to read manually.

This capability carries a specific risk that deserves direct acknowledgment rather than marketing-style enthusiasm: a language model summarizing registry entries can hallucinate --- state a finding, a number, or a causal link that is not actually supported by the underlying entries --- with a fluency that makes the error hard to detect. Given the ethical stakes described in Section 17.2, where we recommend the registry itself be treated as a lead requiring verification rather than a citation-equivalent source, layering an LLM synthesis step on top makes that caution more, not less, important. Any RAG interface built on this registry should therefore surface the underlying source entries prominently alongside any generated summary, should avoid presenting synthesized text as if it were a direct quotation from a registry entry, and should be explicitly framed to users as a discovery aid rather than as a source of independently verified fact --- extending, rather than relaxing, the framing principle already established in Section 17.2.

**29.3 Sequencing**

Consistent with the staged, credibility-first sequencing already used for the roadmap in Section 19, semantic search should precede RAG rather than the two being built simultaneously: semantic search alone is lower-risk, easier to evaluate for correctness, and delivers most of the discoverability benefit that motivates this section, while RAG synthesis introduces the hallucination risk discussed above and should not be deployed until the underlying dataset (Section 21.1) has grown well beyond its current illustrative scale.

**30. An Evidence Quality and Confidence Model**

Section 17.2 already establishes, as a matter of design philosophy, that not every entry in the registry carries the same evidentiary weight --- a curator-reviewed, methodologically detailed submission from an established lab is not equivalent to a bare-minimum entry mined from a public database extraction. The current schema has no field that expresses this distinction explicitly; it is left entirely to the reader\'s judgment. A mature evidence infrastructure should make that judgment visible and, where possible, structured.

**30.1 A GRADE-inspired rating, adapted for negative results**

The GRADE framework (Grading of Recommendations Assessment, Development and Evaluation), widely used in clinical guideline development to rate the certainty of evidence for a positive treatment effect, rates evidence across dimensions including risk of bias, imprecision, inconsistency, indirectness, and publication bias itself. Several of these dimensions transfer directly to a negative-results context --- risk of bias and imprecision apply equally to a null finding --- while others need adaptation: GRADE\'s publication-bias dimension, for instance, is largely inverted here, since the registry\'s entire purpose is to counteract publication bias rather than to be undermined by it. We propose an adapted, coarser rating --- High / Moderate / Low / Very Low confidence, evaluated primarily on sample size adequacy, methodological detail supplied, and independent source verification (Section 11.2) --- assigned by the curator at review time rather than computed automatically, since automating a judgment this contextual would risk false precision.

**30.2 Bayesian framing as a complement, not a replacement**

Where sufficient statistical detail is available (Section 26, Table 4), reporting a Bayes factor alongside or instead of a p-value offers a framing many methodologists consider better suited to negative findings specifically: a Bayes factor can directly quantify the strength of evidence for the null relative to the alternative hypothesis, whereas a non-significant p-value is frequently, and wrongly, treated as if it were positive evidence of no effect rather than merely an absence of evidence for an effect. This is deliberately proposed as an optional, supplementary field (Table 4) rather than a requirement, since most contributors --- particularly the no-code, non-technical pathway described in Section 12.1 --- will not have performed or have access to a Bayesian re-analysis of their own data.

**30.3 Risk-of-bias assessment**

For entries with enough methodological detail, a lightweight, negative-result-adapted analogue of the Cochrane Risk of Bias tool (RoB 2 for randomized trials, or ROBINS-I for non-randomized studies) should be used to flag specific domains of concern --- randomization process, missing outcome data, and measurement of the outcome are all domains directly relevant to whether a negative result reflects a true absence of effect or a methodological artifact. As with the GRADE-inspired rating in Section 30.1, this should be curator-assessed rather than contributor-self-reported, to avoid the obvious incentive problem of asking a contributor to rate the quality of their own negative finding.

**30.4 Replication confidence**

Finally, where multiple independent entries in the registry describe materially similar interventions against materially similar targets and converge on the same negative conclusion, the registry should be able to surface that convergence explicitly as a replication-confidence signal --- precisely the aggregation benefit that motivates the knowledge-graph proposal in Section 27, since identifying "mateially similar" entries at scale is a graph-querying problem, not a flat-file search problem. A single negative entry is a lead; three independent, methodologically sound negative entries converging on the same target is considerably closer to settled evidence, and the registry\'s evidence-quality model should be able to say so explicitly rather than leaving that inference to the reader.

**31. Sequencing This Agenda Against the Existing Roadmap**

The five proposals in this Part are additions to, not replacements for, the five-milestone roadmap already described in Section 19. None of them should precede the completion of that roadmap\'s first three milestones --- seeding the dataset, publishing the search interface, and building the no-code submission pathway --- since every proposal in this Part (a richer schema, a knowledge graph, an ontology, semantic search, an evidence-quality model) is more valuable, and easier to design correctly, once there is a non-trivial body of real entries to design against, rather than the seven illustrative entries presently in the dataset (Appendix E). Building a knowledge graph or an ontology against seven placeholder entries risks over-fitting the design to examples that were never meant to be representative.

We therefore recommend treating this Part as a version 2.0 research agenda to be scoped in detail once the dataset reaches a scale --- plausibly on the order of the roadmap\'s own initial target of 500--1,000 entries (Section 19) --- sufficient to validate these designs against real data, and once the governance model has progressed past the single-maintainer stage (Section 10.1, Section 21.2) to the point where a project of this additional technical scope has the reviewer capacity to sustain it without compromising the curation rigor that is the registry\'s core asset.

**APPENDICES**

**Appendix A: Full Submission Schema Reference**

This appendix reproduces, in narrative form, the complete structure of the Negative Result Submission JSON Schema (Draft-07), for readers who wish to understand the exact data model without inspecting the source repository directly.

**A.1 Controlled vocabularies**

**Domain (required)**

Oncology · Neurology · Pharmacology · Cardiology · Psychiatry · Immunology · Infectious Disease · Endocrinology · Other

**Intervention type (required, nested under tested_intervention)**

Molecule · Drug · Biologic · Device · Behavioral · Procedure · Other

**Institution type (required)**

University Research Lab · Hospital / Clinical Center · Pharmaceutical Company · Independent Researcher · Government Institute · Other

**Source type (optional)**

original_submission · public_database_extraction · literature_mining

**License (required)**

CC0-1.0 · CC-BY-4.0

**A.2 Field-level constraints**

| **Field**                | **Constraint**                               |
|:-------------------------|:---------------------------------------------|
| experiment_id            | String, minimum length 3                     |
| target_disease           | String, minimum length 3                     |
| tested_intervention.name | String, minimum length 1                     |
| hypothesis               | String, minimum length 5                     |
| outcome                  | String, minimum length 5                     |
| methodology_summary      | String, minimum length 5                     |
| researcher_orcid         | Pattern: \^\d{4}-\d{4}-\d{4}-\d{3}\[0-9X\]\$ |
| date_concluded           | ISO 8601 date format (YYYY-MM-DD)            |
| keywords                 | Array of strings                             |

*Table A1. Field-level validation constraints enforced by submission_schema.json.*

**A.3 Example entry (illustrative)**

The following mirrors the structure of an actual seed entry in the oncology domain, reproduced here to illustrate the schema in use:

{ \"experiment_id\": \"ONC_2025_0001\", \"domain\": \"Oncology\", \"target_disease\": \"Non-Small Cell Lung Cancer (NSCLC)\", \"tested_intervention\": { \"type\": \"Drug\", \"name\": \"Example_Compound_A\" }, \"hypothesis\": \"Improves progression-free survival versus standard of care.\", \"outcome\": \"Trial terminated early; primary endpoint not met.\", \"methodology_summary\": \"Randomized controlled trial, phase II.\", \"institution_type\": \"University Research Lab\", \"date_concluded\": \"2024-06-01\", \"license\": \"CC0-1.0\" }

**Appendix B: Glossary of Terms**

| **Term** | **Definition** |
|:---|:---|
| Dark data | Real, honestly collected research data that was never entered into the searchable, citable scientific record. |
| File-drawer problem | A term originating in the social sciences for unpublished null results left in researchers\' private files. |
| Publication bias | The tendency for studies with positive or statistically significant results to be published more often and faster than negative or null studies. |
| Selective outcome reporting | The practice of reporting only the pre-specified endpoints that reached significance while omitting others from a published study. |
| Negative result | A properly conducted study whose primary hypothesis was not supported by the data. |
| Null result | A study that found no measurable effect in either direction. |
| FDAAA | The U.S. Food and Drug Administration Amendments Act of 2007, which mandates results reporting for applicable clinical trials. |
| ACT (Applicable Clinical Trial) | The specific category of trial legally required to report results under FDAAA and its 2016 Final Rule. |
| CC0-1.0 | A Creative Commons public-domain dedication waiving essentially all copyright and related rights. |
| CC-BY-4.0 | A Creative Commons license permitting any use of a work provided the original creator is credited. |
| ORCID | A free, persistent digital identifier that distinguishes individual researchers and links them to their contributions. |
| DOI | Digital Object Identifier --- a permanent, citable identifier assigned to a specific published work or dataset version. |
| JSON Schema | A vocabulary for validating the structure and content of JSON documents against a defined specification. |
| Meta-analysis | A statistical technique for combining results from multiple independent studies to estimate an overall effect. |
| Funnel plot asymmetry | A graphical method for detecting publication bias by examining whether smaller studies show systematically different effect sizes than larger ones. |
| Registered Report | A journal article format in which peer review and in-principle acceptance occur before results are known, based on the quality of the study design. |
| FAIR data | A set of guiding principles --- Findable, Accessible, Interoperable, Reusable --- for making research data maximally useful to others. |
| Reproducibility | The ability of an independent team to obtain consistent results using the original study\'s data and methods. |
| Replicability | The ability of an independent team to obtain consistent results by independently repeating a study using new data. |
| ICMJE | The International Committee of Medical Journal Editors, whose registration requirement for trial publication has driven wide adoption of prospective trial registration. |
| NCT number | The unique identifier assigned to a trial registered on ClinicalTrials.gov (e.g., NCT01234567). |
| Curator | In the Dark Data Medicine governance model, an accountable individual responsible for reviewing submissions against the curation checklist before merging. |
| Schema drift | The gradual, unplanned divergence between an evolving data schema and the entries created under earlier versions of it. |
| Zenodo | A general-purpose open-access research repository, operated by CERN, commonly used to mint persistent DOIs for software and dataset releases. |

**Appendix C: Governance Charter (Reference Excerpt)**

This appendix reproduces, in summarized narrative form, the operative provisions of the project\'s governance documentation for ease of reference alongside this white paper\'s analysis in Section 10.

**Decision-making authority**

- Data schema changes require a written rationale and a migration plan, proposed via issue or pull request.

- New domain categories are added upon demonstrated need, operationalized as five or more pending submissions that do not fit existing categories.

- Code and tooling changes follow standard pull-request review and must pass continuous-integration checks.

**Path to broader governance**

The stated intent is to move from single-maintainer governance toward a small, domain-representative steering group as the registry grows, with consistent high-quality curators as the natural first candidates for co-maintainer status.

**Conflicts of interest**

Curators must disclose, in the review thread, any connection to their own institution\'s or a sponsor\'s research when reviewing a related submission. Disclosure is required; it does not automatically disqualify the review.

**Funding and independence**

Optional personal support for the maintainer is accepted, but no funder, sponsor, or donor may influence which entries are accepted, rejected, or featured --- stated as a hard rule rather than a discretionary policy.

**Appendix D: Methodology Note for This White Paper**

This white paper was prepared through a combination of (a) direct technical inspection of the Dark Data Medicine source repository, including its schema, scripts, tests, GitHub Actions workflows, and governance and contribution documentation, all of which were independently executed and verified to function as documented at the time of writing, and (b) a review of the peer-reviewed and grey literature on publication bias, research reproducibility, and research-transparency policy, cited throughout Part I and listed in Appendix H. Quantitative figures drawn from external sources are attributed to their original studies and are presented as reported in that literature, with the uncertainty and methodological caveats those original authors themselves note; they are not independent re-estimates produced for this paper. Where this paper offers illustrative scenario calculations of the registry\'s potential future impact, as in Section 16, these are explicitly labeled as illustrative and are not presented as measured outcomes, since the registry\'s current dataset is not yet at a scale that would permit empirical impact measurement.

**Appendix E: Current Seed Dataset --- Complete Reproduction**

At the time of this white paper\'s preparation, the registry contains seven entries, one per populated domain, each explicitly labeled as an illustrative example in its keywords field rather than a curator-reviewed real-world submission (see Section 21.1). They are reproduced here in full, in summary tabular form, both to document the current state of the dataset transparently and to demonstrate the schema described in Appendix A in concrete use across every currently populated domain.

| **ID** | **Domain** | **Target / Intervention** | **Outcome (summary)** |
|:---|:---|:---|:---|
| ONC_2025_0001 | Oncology | NSCLC / Example_Compound_A (Drug) | Phase II RCT terminated early; PFS primary endpoint not met |
| NEU_2025_0001 | Neurology | Early Alzheimer\'s / Example_Compound_B (Drug) | Phase III RCT; no significant difference in cognitive decline at 18 months |
| PHARM_2025_0001 | Pharmacology | Type 2 Diabetes / Example_Compound_C (Molecule) | Preclinical mouse study; no HOMA-IR improvement vs. vehicle at 6 weeks |
| CARD_2025_0001 | Cardiology | HFpEF / Example_Compound_D (Drug) | Phase III RCT stopped early for futility at interim analysis |
| PSYCH_2025_0001 | Psychiatry | Treatment-resistant MDD / Digital Intervention E (Behavioral) | RCT; no significant MADRS change vs. waitlist at 8 weeks |
| IMM_2025_0001 | Immunology | Rheumatoid Arthritis / Example_Biologic_F (Biologic) | Phase II RCT; ACR50 response not superior to placebo at 24 weeks |
| ID_2025_0001 | Infectious Disease | MDR Tuberculosis / Example_Compound_G (Drug) | Phase IIb RCT; no culture-conversion improvement; did not advance to phase III |

*Table E1. Complete reproduction of the current seed dataset (7 entries, one per populated domain), as of this paper\'s preparation.*

Institution types represented across the seven entries span University Research Lab, Hospital / Clinical Center, Pharmaceutical Company, and Government Institute, and source types span all three categories defined in the schema --- original_submission, public_database_extraction, and literature_mining --- collectively exercising every controlled-vocabulary branch of the schema described in Appendix A even at this small illustrative scale. No entry in the current dataset contains an ORCID value other than the schema\'s placeholder pattern, and no entry contains a populated contact_email_optional field, consistent with their status as illustrative rather than attributed real-world contributions.

**Appendix F: Independent Technical Verification Log**

As part of preparing this white paper, we independently cloned and executed the Dark Data Medicine repository\'s full toolchain rather than relying solely on its documentation. This appendix records what was run and what it returned, to substantiate the functional claims made throughout Part II.

**F.1 Automated test suite**

Command: pytest tests/ -v

Result: 10 of 10 tests passed, spanning both test_analyze_trends.py (4 tests covering domain/intervention counting, missing-field handling, and empty-input handling) and test_schema_and_validation.py (6 tests covering schema self-validity, template validation, validation of every current seed entry, and correct rejection of malformed submissions).

**F.2 Schema validation**

Command: python scripts/validate_submission.py data/

Result: 7 of 7 files passed validation with no errors.

**F.3 Trend analysis**

Command: python scripts/analyze_trends.py \--top 20

Result: correctly aggregated domain, intervention, disease-target, and institution-type frequency counts across all 7 seed entries, matching the dataset reproduced in Appendix E.

**F.4 Search index generation**

Command: python scripts/generate_search_index.py

Result: successfully wrote all 7 entries to site/data_index.json, the file consumed by the static search interface described in Section 13.3.

**F.5 Excel export**

Command: python scripts/export_to_excel.py \--output DarkData_Export.xlsx

Result: successfully exported all 7 entries across all 7 populated domains to a formatted workbook.

**F.6 Continuous integration configuration**

We reviewed all three GitHub Actions workflow definitions (validate-submissions.yml, test-suite.yml, deploy-site.yml) directly and confirmed each correctly targets the project\'s own scripts and test suite, uses current, non-deprecated action versions, and triggers on the appropriate events (pull requests and pushes to main, scoped by path where specified).

**F.7 Summary**

Every functional claim made about the toolchain in Part II of this white paper was independently reproduced rather than taken solely from the project\'s own documentation. No discrepancies were found between documented and actual behavior at the time of this review.

**Appendix G: Complete JSON Schema (Verbatim)**

The following reproduces the complete, current contents of data/templates/submission_schema.json in full, for readers who wish to implement their own tooling against the schema directly rather than relying on the narrative summary in Appendix A. This file is part of the Dark Data Medicine repository and, like the project\'s other code and tooling, is released under the MIT License.

{
\"\$schema\": \"http://json-schema.org/draft-07/schema#\",
\"title\": \"Negative Result Submission\",
\"type\": \"object\",
\"required\": \[
\"experiment_id\", \"domain\", \"target_disease\", \"tested_intervention\",
\"hypothesis\", \"outcome\", \"methodology_summary\", \"institution_type\",
\"date_concluded\", \"license\"
\],
\"properties\": {
\"experiment_id\": { \"type\": \"string\", \"minLength\": 3 },
\"domain\": { \"type\": \"string\", \"enum\": \[
\"Oncology\", \"Neurology\", \"Pharmacology\", \"Cardiology\", \"Psychiatry\",
\"Immunology\", \"Infectious Disease\", \"Endocrinology\", \"Other\" \] },
\"target_disease\": { \"type\": \"string\", \"minLength\": 3 },
\"tested_intervention\": {
\"type\": \"object\",
\"required\": \[\"type\", \"name\"\],
\"properties\": {
\"type\": { \"type\": \"string\", \"enum\": \[
\"Molecule\",\"Drug\",\"Biologic\",\"Device\",\"Behavioral\",\"Procedure\",\"Other\" \] },
\"name\": { \"type\": \"string\", \"minLength\": 1 },
\"dosage\": { \"type\": \"string\" }
}
},
\"hypothesis\": { \"type\": \"string\", \"minLength\": 5 },
\"outcome\": { \"type\": \"string\", \"minLength\": 5 },
\"methodology_summary\": { \"type\": \"string\", \"minLength\": 5 },
\"researcher_orcid\": { \"type\": \"string\",
\"pattern\": \"\^\\d{4}-\\d{4}-\\d{4}-\\d{3}\[0-9X\]\$\" },
\"institution_type\": { \"type\": \"string\", \"enum\": \[
\"University Research Lab\",\"Hospital / Clinical Center\",
\"Pharmaceutical Company\",\"Independent Researcher\",
\"Government Institute\",\"Other\" \] },
\"date_concluded\": { \"type\": \"string\", \"format\": \"date\" },
\"source_type\": { \"type\": \"string\", \"enum\": \[
\"original_submission\",\"public_database_extraction\",\"literature_mining\" \] },
\"source_url\": { \"type\": \"string\" },
\"license\": { \"type\": \"string\", \"enum\": \[\"CC0-1.0\", \"CC-BY-4.0\"\] },
\"contact_email_optional\": { \"type\": \"string\" },
\"keywords\": { \"type\": \"array\", \"items\": { \"type\": \"string\" } }
}
}

Readers implementing independent tooling against this schema should note that it is versioned through ordinary Git history rather than an internal version field; the governance provisions summarized in Appendix C require any future breaking change to this file to be accompanied by a written migration plan for existing entries.

**Appendix H: References**

Sources are listed by subject area corresponding to their use in Part I. Where a specific dataset or figure is drawn from secondary reporting on a primary study, both are noted.

**H.1 Publication bias and non-reporting: empirical studies**

- Simes, R.J. (1986). Publication bias: the case for an international registry of clinical trials. Journal of Clinical Oncology, 4, 1529--1541.

- Dickersin, K., Chan, S., Chalmers, T.C., Sacks, H.S., Smith, H. (1987). Publication bias and clinical trials. Controlled Clinical Trials / cohort survey of trialists on published and unpublished RCTs.

- Song, F. et al. (2010). Dissemination and Publication of Research Findings: An Updated Review of Related Biases. Health Technology Assessment, 14(8).

- Turner, E.H. et al. Selective publication of antidepressant trials and its influence on apparent efficacy, comparing FDA regulatory data with the published literature.

- Cohort study of Pediatric Academic Societies meeting abstracts (1992--1995) and follow-up replication study --- subsequent publication rates of phase III pediatric RCTs.

- Hospital ethics-committee cohort (1997--2004) of drug-evaluating clinical trials --- publication rate, time-to-publication, and impact-factor comparison by outcome direction.

- Neurology clinical trial publication trend study (trials completed 2008--2014) --- stable \~50% publication rate with declining time-to-publication.

- Cross-sectional study of registered-trial protocols on PubMed Central (2011--2022) --- rate of protocols not associated with published results.

- Catalog of Bias (University of Oxford Centre for Evidence-Based Medicine) --- synthesis of publication-bias cohort studies, including psychological-treatment effect-size distortion from unpublished data.

- Mayo Clinic Proceedings --- Publication Bias: A Brief Review for Clinicians.

**H.2 Reproducibility and research economics**

- Freedman, L.P., Cockburn, I.M., Simcoe, T.S. (2015). The Economics of Reproducibility in Preclinical Research. PLOS Biology, 13(6): e1002165.

- Begley, C.G., Ellis, L.M. (2012). Drug development: Raise standards for preclinical cancer research. Nature, 483, 531--533.

- Prinz, F., Schlange, T., Asadullah, K. (2011). Believe it or not: how much can we rely on published data on potential drug targets? Nature Reviews Drug Discovery, 10, 712.

- Begley, C.G., Ioannidis, J.P.A. (2015). Reproducibility in Science: Improving the Standard for Basic and Preclinical Research. Circulation Research, 116, 116--126.

- Macleod, M.R., Michie, S., Roberts, I., Dirnagl, U., Chalmers, I. et al. (2014). Biomedical research: increasing value, reducing waste. The Lancet, 383, 101--104.

- Ioannidis, J.P.A. (2005). Why Most Published Research Findings Are False. PLOS Medicine, 2(8): e124.

**H.3 Regulatory and transparency infrastructure**

- DeVito, N.J., Bacon, S., Goldacre, B. (2018/2020). Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. The Lancet.

- DeVito, N.J., Bacon, S., Goldacre, B. FDAAA TrialsTracker: A live informatics tool to monitor compliance with FDA requirements to report clinical trial results. bioRxiv 266452.

- FDA Amendments Act of 2007 (FDAAA), Section 801, and its 2016 Final Rule (42 CFR Part 11).

- European Union Clinical Trials Regulation (EU) No 536/2014.

- AllTrials campaign documentation and 2017 audit of clinical-trial reporting policies across 42 pharmaceutical companies.

- PROSPERO International Prospective Register of Systematic Reviews, Centre for Reviews and Dissemination, University of York.

**H.4 Case study sources**

- Historical reviews of high-dose chemotherapy with autologous bone marrow transplantation for breast cancer, and the delayed dissemination of contrary randomized-trial evidence during its period of widespread clinical adoption.

- CBC News (2016). \'We\'ve been deceived\': Results of many clinical trials never published --- reporting on registry audit data.

**H.5 Project source materials**

- Dark Data Medicine repository: README.md, CONTRIBUTING.md, CHANGELOG.md, LICENSE, CITATION.cff, .zenodo.json.

- Dark Data Medicine documentation: docs/GOVERNANCE.md, docs/CURATION_GUIDE.md, docs/HOW_TO_CONTRIBUTE.md, docs/DATA_DICTIONARY.md.

- Dark Data Medicine schema and templates: data/templates/submission_schema.json, data/templates/submission_template.json.

- Dark Data Medicine tooling: scripts/validate_submission.py, scripts/analyze_trends.py, scripts/export_to_excel.py, scripts/generate_search_index.py, scripts/clinicaltrials_seed_extractor.py.

- Dark Data Medicine test suite: tests/test_schema_and_validation.py, tests/test_analyze_trends.py.

- Dark Data Medicine CI/CD: .github/workflows/validate-submissions.yml, .github/workflows/test-suite.yml, .github/workflows/deploy-site.yml.
