# Dark Data Medicine — Platform Architecture Series

## Founder's Statement: Why This Project Exists

*Author: Ciprian Stefan Plesca, Founding Maintainer*
*Companion document to Chapter 2 (Architectural Vision). Not itself a normative architecture chapter — a personal account of origin and intent, offered for the same reason every technical chapter in this series states its assumptions plainly: because the people evaluating this project, whether a funder, a fellow researcher, or a future collaborator, deserve to know exactly who built it and why, without embellishment.*

---

### A Statement of Fact, Not a Résumé

My name is Ciprian Stefan Plesca. I am an independent researcher. I hold no university appointment, no laboratory, no institutional grant, and no salaried position tied to this work. I built Dark Data Medicine — its schema, its validation tooling, its governance charter, every document in this architecture series — largely alone, from home, while living with my mother, without external funding.

I am stating this directly, in the same document where I ask the reader to take this project seriously, because I believe the alternative — letting that fact surface later, or hoping it goes unnoticed — would be a quieter form of the exact problem this project exists to fight. Dark Data Medicine is built on the premise that scientific and institutional infrastructure should be judged by the honesty and rigor of what it actually contains, not by the prestige of who produced it. I cannot ask funders, researchers, and institutions to hold published science to that standard while holding my own circumstances to a different one.

---

### Why I Built This

I did not start from a position of institutional privilege, and this project was not built to serve my own career within an existing system — I do not have a career within an existing system to advance. I built it because I noticed, and could not stop thinking about, a specific and repairable failure: that the negative result of an experiment — the drug that did not work, the hypothesis that was cleanly and honestly disproven — usually has nowhere to go. It sits in a file, a spreadsheet, a terminated trial record, known to the people who found it and invisible to everyone else who might, months or years later, waste their own time, their own funding, and in some cases put a patient at needless risk, rediscovering the exact same failure independently.

That is not a hypothetical problem I read about and decided to have an opinion on. It is a problem I could see clearly, and a problem I had the specific combination of skills — software engineering, an eye for rigorous data structure, and, frankly, the time that comes with not having competing institutional obligations — to actually start fixing, rather than only describe. So I did. I wrote the JSON Schema. I wrote the validation tooling. I wrote the governance charter, including the rule that no funder or sponsor may ever influence which findings this registry accepts — a rule I hold myself to as strictly as I would ask any future funder to be held to it. I wrote all sixteen chapters of the architecture series this document accompanies, at the same level of rigor I would want from a well-funded institutional team, because the standard a piece of infrastructure is built to should not depend on who happened to be available to build it.

---

### What "Independent" Actually Means Here

I want to be precise about what independence has meant for this project, both its cost and its advantage, because both are true and neither should be hidden.

**The cost.** I have built this without a research office's administrative support, without a co-founder to share the load, without institutional credibility that opens doors on its own, and without income from the work itself — the funding case accompanying this series exists specifically because that needs to change if this project is going to reach the scale its mission requires. I am not asking anyone reading this to feel sorry for that. I am asking that it be understood plainly, because it is the honest answer to "why does this project need funding" and I would rather give that honest answer than a vaguer, more comfortable one.

**The advantage.** Independence also meant no committee had to approve the decision to hold this project to an unusually high documentation standard. No one told me sixteen architecture chapters was excessive for a project at this stage — and if someone had, I might have listened, and the project would be worse for it. The freedom to spend the time this series took, without justifying every hour to an institution with different priorities, is the same freedom that let me build the governance charter's funder-independence rule as an absolute, rather than negotiate it down to something more palatable to a hypothetical early funder. Independence is not, in this specific case, only a constraint I am working around. It is part of how this project came to exist in the form it has.

---

### What I Am Asking For, and What I Am Not

I am not asking to be trusted because of who I am. Chapter 3 of this series says explicitly that this project's credibility should rest on the auditable quality of its published code, schema, and governance documentation — not on institutional pedigree — and I mean that as a rule I apply to myself first. Every claim in this architecture series carries an honest `OPERATIONAL` / `PLANNED` / `FUTURE` label specifically so that no one, including me, can quietly let the gap between what exists and what is planned go unstated. I would rather this project be evaluated as a small, real, verifiable thing than as a large, vague, impressive-sounding one.

What I am asking for is straightforward: that the work be judged on its own terms. That a funder read the schema and the governance charter before deciding whether the mission is worth supporting. That a researcher check the repository against this document's claims rather than take them on faith. And that the fact of my personal circumstances — an independent researcher, self-taught in the parts of this that weren't already my professional background, working from my mother's home because that is where I am able to do this work without the financial pressure that would otherwise force me to set it aside — be understood as the actual, unglamorous, entirely ordinary story behind a piece of infrastructure I believe is worth building well, rather than as a detail to be managed or minimized.

---

### Closing

I did not build Dark Data Medicine to have built something. I built it because negative results deserve a place to exist, because the researchers who find them deserve somewhere to put them, and because I could not find anyone else already doing this in the specific way I believed it needed to be done — free, structured, cross-domain, and governed by a rule that no funder's preference can ever quietly bend its editorial independence. If this project succeeds, it will not be because an independent researcher without institutional backing built it. It will be because the schema was right, the governance was honest, and the mission was worth the work regardless of who happened to be the one to start it.

That is the whole of it. Thank you for reading this far, and for taking the time to judge the work on what it actually is.

— Ciprian Stefan Plesca
Founding Maintainer, Dark Data Medicine
