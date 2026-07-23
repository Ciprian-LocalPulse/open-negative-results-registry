# Specifications

This folder holds granular, topic-specific specification documents — as
distinct from the full-length architecture documents in [`architecture/`](../architecture/),
which cover these same topics as chapters within a single larger document.

## Currently populated

- **`domain/`** — [`DATA_MODEL_DIAGRAM.md`](domain/DATA_MODEL_DIAGRAM.md),
  a standalone diagram/reference for the registry's data model.

## Reserved for future extraction

The following subfolders are intentionally not yet created. As the project
matures, granular specifications on these individual topics may be extracted
from the relevant chapters of `architecture/Dark_Data_Medicine_System_Architecture.md`
and the 16-chapter series, so each can be versioned, linked, and updated
independently of the full-length documents they came from:

- `ontology/` — see `architecture/Chapter_6_Ontology_Specification.md` in the meantime
- `knowledge-graph/` — covered within the ontology/knowledge-graph chapter
- `database/` — see the Database Schema chapter of `Dark_Data_Medicine_System_Architecture.md`
- `api/` — see `architecture/Chapter_7_API_Specification.md`
- `metadata/` — see [`docs/METADATA_STANDARD.md`](../docs/METADATA_STANDARD.md)
- `schemas/` — the authoritative, machine-readable schema lives at
  [`data/templates/submission_schema.json`](../data/templates/submission_schema.json)
  and intentionally stays there rather than being duplicated here, since
  `scripts/validate_submission.py` and the test suite read it from that exact path.
- `validation/` — see [`docs/CURATION_GUIDE.md`](../docs/CURATION_GUIDE.md)
- `governance/` — see [`docs/GOVERNANCE.md`](../docs/GOVERNANCE.md)

These are deliberately left as pointers rather than empty folders with no
explanation, so a reader knows where the material currently lives while a
maintainer decides whether splitting it out further is worth the added
maintenance surface.
