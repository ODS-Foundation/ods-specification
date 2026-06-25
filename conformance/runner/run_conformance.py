#!/usr/bin/env python3
"""
ODS Conformance Runner (Layer 1 + Layer 3)

Drives the reference validator (validator/validate.py) over a manifest of
fixtures and produces a deterministic, clause-traceable conformance report.

The suite tests STATICALLY-DECIDABLE clauses only. Level verdicts are always
reported with that qualifier, e.g. "Core Standard (statically-decidable
clauses): PASS". Behavioral/write-time clauses are enumerated in the report's
machine-readable `not_covered` list so a result never overstates what it proves.

Validator exit-code contract:
  0 -> accept | 1 -> clean reject | other (e.g. 2) -> operational error (ERROR)

Fixture modes:
  core    -> validate.py <candidate>
  stored  -> validate.py --stored <candidate>        (sequence_number required)
  store   -> validate.py --store <store_dir> <candidate>   (candidate OUTSIDE the dir)

The JSON report is deterministic (sorted keys, compact separators, UTF-8) and
contains no timestamps, hostnames, or absolute paths; its SHA-256 is therefore a
reproducible fingerprint and equals sha256sum of the --report file.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCOPE = "statically-decidable clauses"
CONF_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CONF_DIR.parent
VALIDATOR = REPO_ROOT / "validator" / "validate.py"
MANIFEST = CONF_DIR / "manifest.json"


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def observed_from_exit(code: int) -> str:
    return {0: "accept", 1: "reject"}.get(code, f"operror({code})")


def argv_for(fx: dict) -> list[str] | None:
    candidate = str(CONF_DIR / fx["file"])
    mode = fx.get("mode", "core")
    if mode == "core":
        return [candidate]
    if mode == "stored":
        return ["--stored", candidate]
    if mode == "store":
        store = fx.get("store")
        if not store:
            return None
        return ["--store", str(CONF_DIR / store), candidate]
    return None


def run_fixture(fx: dict) -> dict:
    fixture_path = CONF_DIR / fx["file"]
    args = argv_for(fx)
    if not fixture_path.exists() or args is None:
        observed, status = "missing", "ERROR"
    else:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), *args],
            capture_output=True, text=True,
        )
        observed = observed_from_exit(proc.returncode)
        if observed == fx["expect"]:
            status = "PASS"
        elif observed in ("accept", "reject"):
            status = "FAIL"
        else:
            status = "ERROR"
    return {
        "file": fx["file"],
        "level": fx["level"],
        "mode": fx.get("mode", "core"),
        "clause": fx["clause"],
        "expect": fx["expect"],
        "observed": observed,
        "status": status,
    }


def build_report(manifest: dict, level_filter: str | None) -> dict:
    fixtures = manifest["fixtures"]
    if level_filter:
        fixtures = [f for f in fixtures if f["level"] == level_filter]

    results = sorted((run_fixture(f) for f in fixtures), key=lambda r: r["file"])

    levels: dict[str, dict] = {}
    for r in results:
        lv = levels.setdefault(r["level"], {"passed": 0, "total": 0, "scope": SCOPE})
        lv["total"] += 1
        if r["status"] == "PASS":
            lv["passed"] += 1
    for lv in levels.values():
        lv["verdict"] = "PASS" if lv["passed"] == lv["total"] else "FAIL"

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errored = sum(1 for r in results if r["status"] == "ERROR")

    not_covered = sorted(
        manifest.get("not_covered", []),
        key=lambda n: (n.get("level", ""), n.get("clause", "")),
    )

    return {
        "suite": manifest["suite"],
        "suite_version": manifest["suite_version"],
        "spec_version": manifest["spec_version"],
        "scope": SCOPE,
        "validator": "validator/validate.py",
        "summary": {"total": len(results), "passed": passed, "failed": failed, "errored": errored},
        "levels": {k: levels[k] for k in sorted(levels)},
        "results": results,
        "not_covered": not_covered,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the ODS conformance suite against the reference validator.")
    ap.add_argument("--level", help="Only run fixtures for this level (e.g. 'Core Standard').")
    ap.add_argument("--report", metavar="PATH", help="Write the canonical JSON report to PATH.")
    args = ap.parse_args()

    if not VALIDATOR.exists():
        print(f"Error: validator not found at {VALIDATOR}", file=sys.stderr)
        return 2
    manifest = json.loads(MANIFEST.read_text())

    report = build_report(manifest, args.level)
    canon = canonical(report)
    digest = hashlib.sha256(canon.encode("utf-8")).hexdigest()

    if args.report:
        # Exact canonical bytes (no trailing newline) so sha256sum(report) == digest below.
        Path(args.report).write_text(canon)

    s = report["summary"]
    print(f"ODS Conformance — {report['suite']} v{report['suite_version']} (spec v{report['spec_version']})")
    print(f"  scope: {SCOPE}")
    print(f"  fixtures: {s['total']}  passed: {s['passed']}  failed: {s['failed']}  errored: {s['errored']}")
    for lv in sorted(report["levels"]):
        d = report["levels"][lv]
        print(f"  {lv} ({SCOPE}): {d['verdict']} ({d['passed']}/{d['total']})")
    for r in report["results"]:
        if r["status"] != "PASS":
            print(f"  [{r['status']}] {r['file']} — expect {r['expect']}, observed {r['observed']}")
    print(f"  report SHA-256: {digest}")
    if report["not_covered"]:
        print(f"  not covered (behavioral / later sub-delivery) — {len(report['not_covered'])} clauses; see report 'not_covered'.")

    return 0 if (s["failed"] == 0 and s["errored"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
