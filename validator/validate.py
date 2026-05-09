"""
ODS v2.0 Record Validator

Performs two-pass validation:
  Pass 1 — core schema (schema/ods_record_v2.json)
  Pass 2 — profile schema (schema/profiles/<namespace>-<version>.json), if profile field is present

Store-level invariants (parent_id existence, FINAL uniqueness, OUTCOME profile consistency)
require the --store flag pointing to a directory of existing records.

Reserved profile namespace detection uses schema/profiles/registry.json.
"""

import json
import sys
import os
import argparse
from pathlib import Path

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("Error: jsonschema is required. Run: pip install jsonschema")
    sys.exit(2)

REPO_ROOT = Path(__file__).parent.parent
CORE_SCHEMA_PATH = REPO_ROOT / "schema" / "ods_record_v2.json"
PROFILES_DIR = REPO_ROOT / "schema" / "profiles"
REGISTRY_PATH = PROFILES_DIR / "registry.json"


def load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def validate_schema(record: dict, schema: dict) -> list[str]:
    errors = []
    validator = Draft7Validator(schema)
    for error in sorted(validator.iter_errors(record), key=str):
        errors.append(error.message)
    return errors


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return load_json(REGISTRY_PATH)
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_profile_schema_path(profile_field: str) -> Path:
    """Given 'ODS-Finance/v1', return the expected path schema/profiles/ods-finance-v1.json."""
    parts = profile_field.split("/")
    if len(parts) != 2:
        return PROFILES_DIR / "INVALID"
    namespace, major_version = parts
    filename = f"{namespace.lower()}-{major_version}.json"
    return PROFILES_DIR / filename


def check_reserved_namespace(profile_field: str, registry: dict) -> str | None:
    """Return an error string if the profile namespace is reserved, else None."""
    namespace = profile_field.split("/")[0]
    profiles = registry.get("profiles", {})
    info = profiles.get(namespace, {})
    if info.get("status") == "reserved":
        return (
            f"Profile namespace '{namespace}' has status 'reserved' in registry. "
            "Conformance claims against reserved profiles are PROHIBITED (OQ3). "
            "See PROFILES.md."
        )
    return None


def validate_profile(record: dict, args) -> tuple[list[str], list[str]]:
    """
    Perform second-pass profile validation.
    Returns (errors, warnings). Warnings are prefixed strings; errors cause non-zero exit.
    """
    errors = []
    warnings = []
    profile_field = record.get("profile")

    if not profile_field:
        record_type = record.get("record_type")
        if record_type == "OUTCOME" and not args.store:
            warnings.append(
                "OUTCOME profile field is absent and --store was not provided. "
                "Profile-specific fields in this OUTCOME cannot be validated without the parent DECISION."
            )
        return errors, warnings

    registry = load_registry()

    reserved_error = check_reserved_namespace(profile_field, registry)
    if reserved_error:
        errors.append(reserved_error)
        return errors, warnings

    schema_path = resolve_profile_schema_path(profile_field)

    if not schema_path.exists():
        if getattr(args, "skip_missing_profile", False):
            warnings.append(
                f"Profile schema for '{profile_field}' not found at {schema_path}. "
                "--skip-missing-profile is set; profile validation skipped."
            )
            return errors, warnings
        else:
            errors.append(
                f"Profile schema for '{profile_field}' not found. "
                f"Searched: {schema_path}. "
                "A missing profile schema is a configuration failure — the profile schema must be "
                "available for validation. Use --skip-missing-profile to bypass (not recommended for production)."
            )
            return errors, warnings

    try:
        profile_schema = load_json(schema_path)
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"Failed to load profile schema at {schema_path}: {e}")
        return errors, warnings

    profile_errors = validate_schema(record, profile_schema)
    errors.extend(profile_errors)

    return errors, warnings


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
        except (json.JSONDecodeError, KeyError, OSError):
            pass
    return store


def validate_store_invariants(record: dict, store: dict[str, dict]) -> list[str]:
    """
    Validate store-level invariants that JSON Schema cannot enforce:
    1. parent_id must reference an existing record_id in the store.
    2. Only one FINAL OUTCOME per parent_id chain.
    """
    errors = []
    record_type = record.get("record_type")
    parent_id = record.get("parent_id")

    if record_type == "OUTCOME":
        if not parent_id:
            errors.append("OUTCOME record is missing parent_id.")
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


def validate_outcome_profile_consistency(record: dict, store: dict[str, dict]) -> tuple[list[str], list[str]]:
    """
    C4: For OUTCOME records, validate profile consistency against the parent DECISION.
    Returns (errors, warnings).
    """
    errors = []
    warnings = []

    if record.get("record_type") != "OUTCOME":
        return errors, warnings

    parent_id = record.get("parent_id")
    if not parent_id or parent_id not in store:
        return errors, warnings

    parent = store[parent_id]
    parent_profile = parent.get("profile")
    outcome_profile = record.get("profile")

    if outcome_profile is not None and parent_profile is not None:
        if outcome_profile != parent_profile:
            errors.append(
                f"OUTCOME profile '{outcome_profile}' does not match parent DECISION profile "
                f"'{parent_profile}'. All records in a decision graph must share the same profile. "
                "Write must be rejected."
            )
    elif outcome_profile is None and parent_profile is not None:
        warnings.append(
            f"OUTCOME has no profile field; profile '{parent_profile}' inherited from parent DECISION "
            f"'{parent_id}'. Profile-specific fields on this OUTCOME validated against '{parent_profile}'."
        )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Validate an ODS v2.0 record against the core schema and optional profile schema. "
            "Pass 1: core (ods_record_v2.json). Pass 2: profile schema if profile field is present. "
            "Use --store for store-level invariant checks."
        )
    )
    parser.add_argument("file", help="Path to the JSON record to validate")
    parser.add_argument(
        "--store",
        metavar="DIR",
        help=(
            "Path to a directory of existing records for store-level invariant checking "
            "(parent_id existence, FINAL uniqueness, OUTCOME profile consistency). "
            "Required for complete OUTCOME validation."
        ),
    )
    parser.add_argument(
        "--skip-missing-profile",
        action="store_true",
        default=False,
        help=(
            "Skip profile schema validation when the profile schema file is not found locally. "
            "Emits a warning instead of an error. NOT recommended for production use."
        ),
    )
    args = parser.parse_args()

    record_path = Path(args.file)
    if not record_path.exists():
        print(f"Error: file not found: {record_path}", file=sys.stderr)
        sys.exit(2)

    try:
        record = load_json(record_path)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {record_path}: {e}", file=sys.stderr)
        sys.exit(2)

    if not CORE_SCHEMA_PATH.exists():
        print(f"Error: core schema not found at {CORE_SCHEMA_PATH}", file=sys.stderr)
        sys.exit(2)

    core_schema = load_json(CORE_SCHEMA_PATH)

    # Pass 1 — core schema
    core_errors = validate_schema(record, core_schema)
    if core_errors:
        print("✗ ODS INVALID — core schema errors:")
        for e in core_errors:
            print(f"  · {e}")
        sys.exit(1)

    # Pass 2 — profile schema
    profile_errors, profile_warnings = validate_profile(record, args)

    all_errors = list(profile_errors)
    all_warnings = list(profile_warnings)

    # Store-level invariants
    if args.store:
        store = load_store(Path(args.store))
        store_errors = validate_store_invariants(record, store)
        all_errors.extend(store_errors)

        consistency_errors, consistency_warnings = validate_outcome_profile_consistency(record, store)
        all_errors.extend(consistency_errors)
        all_warnings.extend(consistency_warnings)
    elif record.get("record_type") == "OUTCOME" and not profile_errors:
        all_warnings.append(
            "Store-level invariants not checked "
            "(use --store DIR to validate parent_id existence, FINAL uniqueness, and profile consistency)."
        )

    if all_errors:
        print("✗ ODS INVALID — validation errors:")
        for e in all_errors:
            print(f"  · {e}")
        sys.exit(1)

    for w in all_warnings:
        print(f"⚠  {w}")

    record_type = record.get("record_type", "RECORD")
    profile_field = record.get("profile")
    profile_suffix = f" [{profile_field}]" if profile_field else ""
    print(f"✓ ODS VALID: {record_type} record compliant with core schema v2.0.0{profile_suffix}")
    sys.exit(0)


if __name__ == "__main__":
    main()
