#!/usr/bin/env python3
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "generated" / "0.9.1.2" / "starintel-doc-v0.9.1.2.schema.json"
VALID = ROOT / "tests" / "fixtures" / "actor-config-valid.json"
INVALID = ROOT / "tests" / "fixtures" / "actor-config-invalid-profile.json"


def main() -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    valid_errors = list(validator.iter_errors(json.loads(VALID.read_text())))
    if valid_errors:
        raise SystemExit("valid actor-config rejected: " + "; ".join(error.message for error in valid_errors))
    if not list(validator.iter_errors(json.loads(INVALID.read_text()))):
        raise SystemExit("invalid actor-config profile version was accepted")


if __name__ == "__main__":
    main()
