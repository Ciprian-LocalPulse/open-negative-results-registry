# How to Contribute a Negative Result

Thank you for considering a contribution to the Open Negative Results Registry.
You do **not** need to know Git, GitHub, or any programming to submit data.

## Option 1 — The Simple Form (recommended for clinicians/researchers)

1. Fill out the submission form: **[link to Google Form — add your form URL here]**
2. Answer the questions in plain language:
   - What disease or condition were you studying?
   - What intervention did you test (drug, molecule, device, procedure)?
   - What was your hypothesis?
   - What actually happened? (the negative/null result)
   - How was the study done? (a short summary is fine)
   - Your ORCID ID (optional, but recommended — it adds credibility and lets you get credit)
3. Submit. That's it.

Behind the scenes, an automation converts your answers into our standard data format
and opens a submission for review. A curator checks it for completeness and merges it
into the public database. You will not need to touch GitHub at any point.

## Option 2 — Direct JSON Submission (for technically inclined contributors)

If you're comfortable with GitHub:

1. Copy `data/templates/submission_template.json`
2. Fill in your experiment details, following `docs/DATA_DICTIONARY.md` for field meanings
3. Validate it locally:
   ```
   python scripts/validate_submission.py path/to/your_file.json
   ```
4. Place the file in the correct folder under `data/<domain>/`
5. Open a Pull Request

## What Counts as a Valid Negative Result?

- A tested hypothesis that was **not** confirmed
- A trial or experiment that did **not** reach its primary endpoint
- A treatment/intervention that showed **no significant effect** versus control
- Studies that were terminated early for futility

## What We Do NOT Accept

- Data that could identify individual patients (no patient names, no identifiable case details)
- Unverified anecdotal claims with no methodology
- Duplicate entries of studies already in public trial registries without added value
- Promotional or marketing content of any kind

## Credit and Citation

If you provide an ORCID iD, your contribution is attributed to you. Periodic data
releases are archived on Zenodo with a DOI, so your contribution can be formally
cited in academic work.

## Questions?

Open an Issue on GitHub, or reach out via the contact listed in the main README.
