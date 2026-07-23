# Data Model Diagram

A visual reference for the schema defined in `data/templates/submission_schema.json` and documented field-by-field in `DATA_DICTIONARY.md`. Intended for a first-time reader who wants the shape of the data before reading the full field reference.

![Dark Data Medicine schema entity diagram](../assets/schema_erd.png)

## Reading this diagram

- The blue table (`NegativeResultEntry`) is the top-level object every file under `data/<domain>/` contains. Bold fields are required; non-bold fields are optional.
- `tested_intervention` is the one nested object in the schema — a structured `{type, name, dosage}` triple rather than a free-text field, so an intervention can be filtered by type (`Drug`, `Molecule`, `Biologic`, `Device`, `Behavioral`, `Procedure`, `Other`) independent of its name.
- The three red tables (`domain`, `institution_type`, `license`) are controlled vocabularies — every entry's value in these fields must be one of the listed options, enforced by automated schema validation (`scripts/validate_submission.py`, `.github/workflows/validate-submissions.yml`) before a curator ever reviews the submission.

## Relationship to Part IV of the white paper

`DarkData-Medicine_WhitePaper.md` Part IV proposes a substantially larger version-2.0 schema (persistent identifiers, statistical detail, provenance, ontology links — see its Table 4) as an explicitly optional, additive extension to the schema diagrammed here, not a replacement. This diagram reflects the schema as it exists in this release, not the proposal.
