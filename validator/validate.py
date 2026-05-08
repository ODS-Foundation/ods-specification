"""
ODS v1.0 Record Validator

Validates ODS records against the unified schema (ods_record_v1.json).
Schema-level validation is performed by jsonschema.
Store-level invariants (parent_id existence, FINAL uniqueness) require
the --store flag pointing to a directory of previously written records.
"""

import json
import sys
import os
import argparse
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("Error: jsonschema is required. Run: pip install jsonschema")
    sys.exit(2)

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "ods_record_v1.json"


def load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def validate_schema(record: dict, schema: dict) -> list[str]:
    errors = []
    validator = Draft7Validator(schema)
    for error in sorted(validator.iter_errors(record), key=str):
        errors.append(error.message)
    return errors


def load_store(store_path: Path) -> dict[str, dict]:
    """Load all records from a store directory, keyed by record_id."""
    store = {}
    if not store_path.is_dir():
        print(f"Error: store path is not a directory: {store_path}", file=sys.stderr)
        sys.exit(2)
    for f in store_path.glob("*.json"):
        try:
            r = load_json(f)
            rid = r.get("record_id")
            if rid:
                store[rid] = r
        except (json.JSONDecodeError, KeyError):
            pass
    return store


def validate_store_invariants(record: dict, store: dict[str, dict]) -> list[str]:
    """
    Validate store-level invariants that the JSON Schema cannot enforce:
    1. parent_id must reference an existing record_id in the store.
    2. Only one FINAL OUTCOME per parent_id chain.
    """
    errors = []
    record_type = record.get("record_type")
    parent_id = record.get("parent_id")

    if record_type == "OUTCOME":
        if not parent_id:
            errors.append("OUTCOME record is missing parent_id")
            return errors

        if parent_id not in store:
            errors.append(
                f"parent_id '{parent_id}' does not reference any known record_id in the store. "
                "Write must be rejected."
            )

        if record.get("outcome_status") == "FINAL":
            existing_finals = [
                r for r in store.values()
                if r.get("record_type") == "OUTCOME"
                and r.get("parent_id") == parent_id
                and r.get("outcome_status") == "FINAL"
            ]
            if existing_finals:
                errors.append(
                    f"A FINAL OUTCOME already exists for parent_id '{parent_id}' "
                    f"(record_id: {existing_finals[0]['record_id']}). "
                    "Only one FINAL is permitted per decision chain. Write must be rejected."
                )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate an ODS v1.0 record against the schema and optional store invariants."
    )
    parser.add_argument("file", help="Path to the JSON record to validate")
    parser.add_argument(
        "--store",
        metavar="DIR",
        help="Path to a directory of existing records for store-level invariant checking "
             "(parent_id existence, FINAL uniqueness). Required for complete OUTCOME validation.",
    )
    args = parser.parse_args()

    schema = load_json(SCHEMA_PATH)
    record = load_json(Path(args.file))

    schema_errors = validate_schema(record, schema)
    if schema_errors:
        print("✗ ODS INVALID — schema errors:")
        for e in schema_errors:
            print(f"  · {e}")
        sys.exit(1)

    store_errors = []
    if args.store:
        store = load_store(Path(args.store))
        store_errors = validate_store_invariants(record, store)
    elif record.get("record_type") == "OUTCOME":
        print(
            "⚠  Schema valid. Store-level invariants not checked "
            "(use --store DIR to validate parent_id existence and FINAL uniqueness)."
        )
        sys.exit(0)

    if store_errors:
        print("✗ ODS INVALID — store invariant violations:")
        for e in store_errors:
            print(f"  · {e}")
        sys.exit(1)

    record_type = record.get("record_type", "RECORD")
    print(f"✓ ODS VALID: {record_type} record compliant with schema v1.0")
    sys.exit(0)


if __name__ == "__main__":
    main()
