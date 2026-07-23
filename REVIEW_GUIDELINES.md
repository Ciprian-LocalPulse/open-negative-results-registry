Open Peer-Review Guidelines

This document sets out the rules and expectations for peer-reviewers reviewing submissions to the Open Negative Results Registry (ONRR).

1. Review Philosophy (Mindset)

In traditional publications, the reviewer looks for "innovation", "impact" and "clear positive results".

In ONRR, we evaluate methodological rigour exclusively, not the success of the hypothesis.

The central question for an ONRR reviewer is:

"Did this experiment fail because the hypothesis was inherently wrong (which is a valid scientific discovery), or did it fail because of poor execution by the researcher (human error)?"

2. Validation Criteria (Acceptance)

A submission (Pull Request / Issue) must be approved if it meets the following conditions:

[ ] Transparency of Methodology: The experimental steps are described in sufficient detail that another laboratory can reproduce them (even if the reproduction will lead to the same failure).

[ ] Data Validity: If a dataset was used, it is clean, accessible (ideally through an external DOI) and does not present blatant processing errors.

[ ] Hypothesis Substantiation: The initial hypothesis had a coherent scientific logic at the time of its formulation (we do not evaluate "pseudo-science").

[ ] Correct Mathematical/Statistical Analysis: The conclusion of "failure" is supported by metrics (e.g. p-value > 0.05, F1-score below expectations, non-existent chemical reaction proven spectrally).

3. Technical Approval Process

A researcher opens an Issue using the standard form.

An assured Reviewer analyzes the data.

If clarification is needed, the Reviewer leaves a comment (e.g. "Please specify the PyTorch version used").

Once the quality is confirmed, the Reviewer applies the approved-negative-result label and closes the Issue as Completed, triggering its indexing in the public database.

4. Code of Conduct

Criticism should be strictly code and methodology-oriented. We appreciate the courage to publish failures. Condescending comments about the invalidity of an idea will not be tolerated.