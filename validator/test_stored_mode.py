"""
Submitted-vs-Stored Mode Validation — Behavioral Tests

Verifies that validator/validate.py correctly distinguishes between:
  - Submitted records: sequence_number absent (pre-store-assignment); validated
    without --stored. Valid for all record types.
  - Stored records: sequence_number present (post-store-assignment); validated
    with --stored. Invalid if sequence_number is absent.

See SPECIFICATION.md §3.3 and the validate.py --stored flag.

Test cases:
  1. Submitted DECISION (no seq), default mode       → VALID
  2. Submitted DECISION (no seq), --stored           → INVALID
  3a. Stored DECISION (seq=7), --stored              → VALID
  3b. Stored OUTCOME (seq=8), --stored               → VALID
  4a. Submitted CHECKPOINT (no seq), default mode    → VALID
  4b. Submitted CHECKPOINT (no seq), --stored        → INVALID
  4c. Stored CHECKPOINT (seq=7, covers=6), --stored  → VALID
  5.  _schema_version 2.0.0 + CHECKPOINT             → INVALID (schema)
  6.  CHECKPOINT seq=6 == covers=6                   → INVALID (own_seq > covers)

Run: python3 validator/test_stored_mode.py
All tests must pass.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

sys.path.insert(0, str(Path(__file__).parent))
from validate import (
    load_json,
    validate_checkpoint,
    validate_schema,
    validate_sequence_number,
    validate_stored_representation,
)

CORE_SCHEMA_PATH = REPO_ROOT / "schema" / "ods_record_v2.json"

_POLICY_HASH = "a" * 64
_TREE_ROOT = "b" * 64
_RECORD_ID = "00000000-0000-4000-8000-000000000001"
_PARENT_ID = "00000000-0000-4000-8000-000000000002"
_TS = "2026-05-19T10:00:00.000000Z"


def _decision(seq=None, schema_version="2.1.0"):
    r = {
        "_schema_version": schema_version,
        "record_type": "DECISION",
        "record_id": _RECORD_ID,
        "timestamp_utc": _TS,
        "identity": {"model_version": "v2.1.0", "policy_hash": _POLICY_HASH},
        "cognition": {"confidence": 0.9, "rationale": "Test decision record for stored-mode tests."},
        "governance": {
            "audit_trail": [{"timestamp_utc": _TS, "event": "DECISION_CREATED", "actor": "test"}]
        },
    }
    if seq is not None:
        r["sequence_number"] = seq
    return r


def _outcome(seq=None):
    r = {
        "_schema_version": "2.1.0",
        "record_type": "OUTCOME",
        "record_id": _RECORD_ID,
        "timestamp_utc": _TS,
        "parent_id": _PARENT_ID,
        "outcome_status": "FINAL",
        "outcomes": {
            "actual_result": 0.95,
            "realized_at": _TS,
            "delta_from_expected": 0.05,
        },
        "governance": {
            "audit_trail": [{"timestamp_utc": _TS, "event": "OUTCOME_LOGGED", "actor": "test"}]
        },
    }
    if seq is not None:
        r["sequence_number"] = seq
    return r


def _checkpoint(seq=None, covers=6, schema_version="2.1.0"):
    r = {
        "_schema_version": schema_version,
        "record_type": "CHECKPOINT",
        "record_id": _RECORD_ID,
        "timestamp_utc": _TS,
        "identity": {"model_version": "v2.1.0", "policy_hash": _POLICY_HASH},
        "checkpoint": {
            "tree_size": covers,
            "tree_root": _TREE_ROOT,
            "covers_through_sequence_number": covers,
            "ordering": "sequence_number ASC",
        },
    }
    if seq is not None:
        r["sequence_number"] = seq
    return r


def _collect_errors(record, stored=False):
    """Mirror the validation pipeline in main() without I/O."""
    errs = validate_schema(record, core_schema)
    if errs:
        return errs  # schema failure short-circuits; deeper checks are meaningless
    errs = list(validate_sequence_number(record))
    cp_errs, _ = validate_checkpoint(record)
    errs.extend(cp_errs)
    if stored:
        errs.extend(validate_stored_representation(record))
    return errs


def run_tests() -> bool:
    passed = 0
    failed = 0

    def check(name: str, record, stored: bool, expect_invalid: bool):
        nonlocal passed, failed
        errs = _collect_errors(record, stored=stored)
        got_invalid = len(errs) > 0
        if got_invalid == expect_invalid:
            status = "INVALID" if got_invalid else "VALID"
            print(f"  PASS  {name}  [{status}]")
            passed += 1
        else:
            want = "INVALID" if expect_invalid else "VALID"
            got = "INVALID" if got_invalid else "VALID"
            print(f"  FAIL  {name}")
            print(f"        expected: {want}  got: {got}")
            for e in errs:
                print(f"        · {e}")
            failed += 1

    print("Submitted-vs-Stored Mode — Behavioral Tests")
    print("=" * 60)

    check("1.  submitted DECISION (no seq), default mode",
          _decision(), stored=False, expect_invalid=False)

    check("2.  submitted DECISION (no seq), --stored",
          _decision(), stored=True, expect_invalid=True)

    check("3a. stored DECISION (seq=7, v2.1.0), --stored",
          _decision(seq=7), stored=True, expect_invalid=False)

    check("3b. stored OUTCOME (seq=8), --stored",
          _outcome(seq=8), stored=True, expect_invalid=False)

    check("4a. submitted CHECKPOINT (no seq), default mode",
          _checkpoint(), stored=False, expect_invalid=False)

    check("4b. submitted CHECKPOINT (no seq), --stored",
          _checkpoint(), stored=True, expect_invalid=True)

    check("4c. stored CHECKPOINT (seq=7, covers=6), --stored",
          _checkpoint(seq=7, covers=6), stored=True, expect_invalid=False)

    check("5.  _schema_version 2.0.0 + CHECKPOINT (impossible combination)",
          _checkpoint(seq=7, schema_version="2.0.0"), stored=True, expect_invalid=True)

    check("6.  CHECKPOINT seq=6 == covers=6 (own_seq must be strictly greater)",
          _checkpoint(seq=6, covers=6), stored=True, expect_invalid=True)

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        print("FAIL")
        return False
    print("PASS")
    return True


if __name__ == "__main__":
    core_schema = load_json(CORE_SCHEMA_PATH)
    ok = run_tests()
    sys.exit(0 if ok else 1)
