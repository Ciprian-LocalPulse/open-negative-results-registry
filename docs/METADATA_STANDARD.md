# Metadata Standard

This document defines the recommended metadata fields for each registry entry.

## Required fields

- `title`: The name of the study or entry.
- `field`: The scientific domain.
- `hypothesis`: The original expectation or research question.
- `method`: A short description of the study design or experimental approach.
- `result_type`: The outcome classification, such as negative, null, inconclusive, or terminated.
- `result_summary`: A concise explanation of what happened.
- `date`: The date of the study or report in `YYYY-MM-DD` format.
- `license`: The data license attached to the entry.

## Recommended fields

- `source`: DOI, URL, trial ID, or other traceable reference.
- `keywords`: A list of search terms or thematic tags.
- `status`: Whether the study is completed, unpublished, terminated, or under review.
- `contributor`: Author name, handle, or ORCID if available.
- `notes`: Any important methodological limitations or context.

## Suggested JSON example

```json
{
  "title": "Example Null Result in Oncology",
  "field": "oncology",
  "hypothesis": "The intervention will improve the primary outcome.",
  "method": "Randomized controlled study with a small pilot sample.",
  "result_type": "null",
  "result_summary": "No statistically meaningful difference was observed between the intervention and control groups.",
  "date": "2026-07-22",
  "source": "https://example.org/study",
  "keywords": ["illustrative example", "null result", "oncology"],
  "status": "completed",
  "contributor": "Anonymous",
  "license": "CC0-1.0"
}
```

## Notes on consistency

Use the same terminology across entries whenever possible. If a value can be standardized, it should be standardized. This improves searchability, validation, and long-term reuse.