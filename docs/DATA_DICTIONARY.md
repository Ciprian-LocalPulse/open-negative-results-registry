# Data Dictionary

This document explains every field used in a submission entry
(`data/templates/submission_template.json`).

| Field | Type | Required | Description |
|---|---|---|---|
| `experiment_id` | string | Yes | A unique identifier for this experiment. If you don't have one, one will be auto-generated on submission. If the study has a public trial ID (e.g. an NCT number from ClinicalTrials.gov), use that. |
| `domain` | string | Yes | The broad medical field. One of: Oncology, Neurology, Pharmacology, Cardiology, Psychiatry, Immunology, Infectious Disease, Endocrinology, Other. |
| `target_disease` | string | Yes | The disease, condition, or cell line being studied (e.g. "Breast Cancer (MCF-7 cells)"). |
| `tested_intervention.type` | string | Yes | The kind of intervention: Molecule, Drug, Biologic, Device, Behavioral, Procedure, Other. |
| `tested_intervention.name` | string | Yes | Name or code of the compound/drug/device tested. |
| `tested_intervention.dosage` | string | No | Dosage or exposure level used, if applicable. |
| `hypothesis` | string | Yes | The hypothesis being tested, in one sentence. |
| `outcome` | string | Yes | What actually happened — the negative or null result. Be specific and factual. |
| `methodology_summary` | string | Yes | A short description of the study design (e.g. "Randomized controlled trial, phase II", "In vitro, MTT assay"). |
| `researcher_orcid` | string | No | Your ORCID iD (format: 0000-0000-0000-0000). Adds credibility and ensures you get credit. Get one free at [orcid.org](https://orcid.org). |
| `institution_type` | string | Yes | One of: University Research Lab, Hospital / Clinical Center, Pharmaceutical Company, Independent Researcher, Government Institute, Other. |
| `date_concluded` | string (date) | Yes | Date the study concluded, format YYYY-MM-DD. |
| `source_type` | string | Yes | `original_submission` (you ran this study yourself), `public_database_extraction` (pulled from a public registry), or `literature_mining` (extracted from a published paper). |
| `source_url` | string | No | Link to the original trial registry entry or publication, if applicable. |
| `license` | string | Yes | The license you release this data entry under. We recommend `CC0-1.0` (public domain) or `CC-BY-4.0` (attribution required). |
| `contact_email_optional` | string | No | Only if you're willing to be contacted about this entry. Never required. |
| `keywords` | array of strings | No | Free-text tags to help others find your entry. |

## Privacy Note

Never include patient names, dates of birth, medical record numbers, or any other
personally identifiable patient information in any field. Submissions are reviewed
before merging, but the responsibility to de-identify data starts with the submitter.
