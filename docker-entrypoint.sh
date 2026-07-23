#!/usr/bin/env bash
# Dispatches `docker run darkdata-medicine <command> [args]` to the
# matching script under /app/scripts/, so the image behaves like a
# single CLI rather than requiring the user to know each script's path.
set -euo pipefail

cmd="${1:-}"
shift || true

case "$cmd" in
  validate)
    exec python scripts/validate_submission.py "$@"
    ;;
  analyze)
    exec python scripts/analyze_trends.py "$@"
    ;;
  export)
    exec python scripts/export_to_excel.py "$@"
    ;;
  search-index)
    exec python scripts/generate_search_index.py "$@"
    ;;
  seed-extract)
    exec python scripts/clinicaltrials_seed_extractor.py "$@"
    ;;
  --help|-h|help|"")
    cat <<'EOF'
Dark Data Medicine CLI (containerized)

Usage: docker run --rm [-v <host-data>:/app/data] darkdata-medicine <command> [args]

Commands:
  validate <path>        Validate one JSON file or every .json under a folder
                          against data/templates/submission_schema.json
  analyze [--top N]       Aggregate domain / intervention / institution frequency
                          [--domain X] [--export report.csv]
  export [--output F]    Export the full dataset to a formatted .xlsx workbook
  search-index            Regenerate site/data_index.json from the current dataset
  seed-extract [args]     Pull draft candidate entries from ClinicalTrials.gov
                          (drafts only — still require curator review, see
                          docs/CURATION_GUIDE.md)

Examples:
  docker run --rm darkdata-medicine validate data/
  docker run --rm -v "$PWD/data:/app/data" darkdata-medicine analyze --top 10
  docker run --rm -v "$PWD:/app/out" darkdata-medicine export --output /app/out/DarkData.xlsx
EOF
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Run with --help to see available commands." >&2
    exit 1
    ;;
esac
