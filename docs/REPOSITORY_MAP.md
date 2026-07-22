# Repository Map

## Purpose

This document provides a structured overview of the repository architecture for **Dark Data Medicine — The Open Negative Results Registry**.

Its purpose is to help contributors, reviewers, researchers, and maintainers understand where information is located, how the repository is organized, and which documents should be consulted for specific tasks. A clear repository map reduces friction, improves navigability, and strengthens the documentation ecosystem of the project [web:18][web:22].

## Conceptual Organization

This repository is organized around five main functions:

1. **Data preservation** — storing negative, null, and unpublished scientific results.
2. **Documentation** — explaining the project, its standards, and its procedures.
3. **Validation and tooling** — ensuring that submissions are structurally consistent and technically usable.
4. **Governance and ethics** — defining responsibility, oversight, and acceptable use.
5. **Public accessibility** — making the registry searchable, citable, and understandable to non-specialist users.

This structure follows a documentation logic in which each file serves a distinct function and each document answers a specific class of user need [web:22][web:27].

## Top-Level Structure

```text
DarkData-Medicine/
├── data/
├── docs/
├── examples/
├── scripts/
├── site/
├── tests/
├── .github/
├── assets/
├── README.md
├── LICENSE
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── CITATION.cff
├── .zenodo.json
├── requirements.txt
├── requirements-dev.txt
└── FUNDING.md
```

## Directory Overview

### `data/`

This directory contains the scientific content of the registry: negative results, null findings, and associated structured records. It is the conceptual core of the project and should remain machine-readable, traceable, and consistently formatted.

Expected contents may include:

- Domain-specific subfolders such as oncology, neurology, pharmacology, and psychiatry.
- Submission templates.
- JSON schema definitions.
- Structured dataset entries.

### `docs/`

This directory contains all human-readable documentation intended to explain the project’s purpose, standards, and procedures. It should be considered the interpretive layer of the repository.

Recommended documents include:

- `HOW_TO_CONTRIBUTE.md`
- `DATA_DICTIONARY.md`
- `CURATION_GUIDE.md`
- `GOVERNANCE.md`
- `FAQ.md`
- `ETHICS.md`
- `SUBMISSION_TEMPLATE.md`
- `METADATA_STANDARD.md`
- `REPOSITORY_MAP.md`

Each document should address a distinct function, following the principle that documentation should be focused, navigable, and purpose-specific [web:22][web:27].

### `examples/`

This directory contains illustrative entries that demonstrate how valid submissions should be written and formatted. It is especially useful for new contributors who need concrete models before preparing real data.

Recommended contents may include:

- `sample_entry.md`
- Example JSON records.
- Example metadata files.
- Example submission packages.

### `scripts/`

This directory contains the project’s utility scripts and automation tools. These scripts support validation, analysis, conversion, indexing, and export.

Typical functions include:

- Schema validation.
- Dataset analysis.
- Search index generation.
- File export.
- Seed extraction from public registries.

### `site/`

This directory contains the static browsing interface for the registry. It should remain lightweight, dependency-free, and synchronized with the validated dataset.

Typical contents may include:

- `index.html`
- Generated search index files.
- Client-side assets required for browsing.

### `tests/`

This directory contains the automated tests that protect the integrity of the project. It exists to ensure that schema rules, validation logic, and analytical tools continue to function reliably as the repository evolves.

Typical test coverage may include:

- Schema validation.
- Input parsing.
- Output consistency.
- Tooling behavior.

### `.github/`

This directory contains the operational infrastructure for contribution management and automation.

It may include:

- GitHub Actions workflows.
- Issue templates.
- Pull request templates.
- Repository automation files.

### `assets/`

This directory contains visual and branding resources used by the project, including banners, icons, and illustrative images for documentation.

### Root-level governance and identity files

The repository root contains documents that define identity, legitimacy, and community rules. These files are essential to the public and institutional character of the project.

#### `README.md`
The primary entry point to the repository. It explains the project’s purpose, scope, structure, use, and contribution pathways.

#### `LICENSE`
Defines the legal terms under which the code and/or data are distributed.

#### `CODE_OF_CONDUCT.md`
Defines standards of behavior for contributors and participants.

#### `CONTRIBUTING.md`
Explains technical contribution workflows, setup requirements, and submission procedures.

#### `CHANGELOG.md`
Documents notable changes across versions and releases.

#### `CITATION.cff`
Provides machine-readable citation metadata for academic and scholarly reuse.

#### `.zenodo.json`
Defines metadata used for DOI archiving through Zenodo.

#### `requirements.txt` and `requirements-dev.txt`
Define runtime and development dependencies.

#### `FUNDING.md`
Provides optional mechanisms for supporting the project’s maintenance and growth.

## Documentation Logic

The documentation in this repository should be interpreted according to the following hierarchy:

- **README.md** provides the public overview.
- **docs/** provides specialized explanatory and procedural documents.
- **examples/** demonstrates correct usage.
- **data/** stores the core registry content.
- **scripts/** and **tests/** maintain integrity, reliability, and reproducibility.
- **.github/** automates review and publishing workflows.

This hierarchy helps preserve conceptual clarity. Users should be able to understand the project at a glance, then descend into increasingly specialized documents depending on their needs [web:22][web:18].

## Recommended Reading Path

For a new visitor, the recommended sequence is:

1. Read `README.md` for the project overview.
2. Read `docs/FAQ.md` for conceptual clarification.
3. Read `docs/ETHICS.md` to understand inclusion principles.
4. Read `docs/SUBMISSION_TEMPLATE.md` before preparing a contribution.
5. Read `docs/METADATA_STANDARD.md` to format structured data correctly.
6. Read `docs/HOW_TO_CONTRIBUTE.md` for the actual submission process.
7. Consult `examples/sample_entry.md` to see a model entry in practice.

This reading path reflects a documentation model in which orientation comes first, followed by explanation, then procedure, then technical detail [web:22][web:29].

## Maintenance Principles

This map should be updated whenever the repository structure changes materially. New folders or documents should be added to this file immediately so that the map remains accurate.

The following principles should guide maintenance:

- Keep descriptions concise but sufficiently informative.
- Preserve consistency in naming and formatting.
- Avoid duplicating content that belongs in another document.
- Ensure that newly added files are represented in the map.
- Review the map after major structural changes or version releases.

A repository map is only useful if it remains current. Stale documentation reduces trust and creates avoidable confusion [web:18][web:22].

## Final Note

This repository is not merely a collection of files. It is an information architecture designed to preserve scientific absence as a form of evidence.

The repository map exists to ensure that this architecture remains legible, navigable, and maintainable for contributors, curators, and researchers alike.