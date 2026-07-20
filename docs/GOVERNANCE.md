# Governance

## Current Structure

This project is currently maintained by a single founding maintainer,
**Ciprian Stefan Plesca**. It is an independent open-source initiative and is
**not** affiliated with any university, hospital, or research institution
unless explicitly stated otherwise in a given release.

## Decision-Making

- **Data schema changes:** proposed via Issue/PR, require a written rationale
  and a migration plan for existing entries (see `CONTRIBUTING.md` §Versioning).
- **New domain categories:** added when there's a demonstrated need (e.g. 5+
  pending submissions that don't fit existing categories).
- **Code/tooling changes:** standard PR review, must pass tests and CI.

## Path to Broader Governance

As the registry grows, the intent is to move toward a small steering group
with representation across medical domains (oncology, neurology,
pharmacology, etc.), rather than a single maintainer holding unilateral
control over data-acceptance policy. Researchers who consistently contribute
high-quality curation work are the first candidates for co-maintainer status.
If you're interested in taking on a curator role for a specific domain, open
an Issue titled `Governance: volunteer curator — <domain>`.

## Conflicts of Interest

Curators reviewing a submission related to their own institution's or
sponsor's research should disclose this in the PR thread. It doesn't
disqualify the review, but transparency matters for a project whose entire
value proposition is trustworthy, unbiased reporting of negative results.

## Funding & Independence

This project accepts optional personal support for the maintainer (see
`FUNDING.md`). No funder, sponsor, or donor has any influence over which data
entries are accepted, rejected, or featured. This separation is a hard rule,
not a policy that can be waived case-by-case.
