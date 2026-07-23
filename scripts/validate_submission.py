#!/usr/bin/env python3
"""
validate_submission.py

Validates a negative-result submission JSON file against the project's
JSON Schema (data/templates/submission_schema.json).

Usage:
    python validate_submission.py path/to/submission.json
    python validate_submission.py path/to/folder/  # validates every .json in folder

Requires:
    pip install jsonschema
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("Missing dependency. Install with: pip install jsonschema --break-system-packages")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "data" / "templates" / "submission_schema.json"


def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_file(path: Path, schema: dict) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[FAIL] {path.name}: invalid JSON ({e})")
        return False

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if errors:
        print(f"[FAIL] {path.name}:")
        for err in errors:
            location = "/".join(str(p) for p in err.path) or "(root)"
            print(f"    - {location}: {err.message}")
        return False

    print(f"[OK]   {path.name}")
    return True


def gather_targets(input_path: Path):
    if input_path.is_dir():
        return sorted(
            p for p in input_path.rglob("*.json")
            if "templates" not in p.parts
        )
    return [input_path]


def main():
    parser = argparse.ArgumentParser(description="Validate negative-result submission JSON files.")
    parser.add_argument("target", help="Path to a submission JSON file or a folder of JSON files")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Path not found: {target_path}")
        sys.exit(1)

    schema = load_schema()
    files = gather_targets(target_path)

    if not files:
        print("No JSON files found to validate.")
        sys.exit(1)

    results = [validate_file(f, schema) for f in files]

    total = len(results)
    passed = sum(results)
    print(f"\n{passed}/{total} files passed validation.")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
