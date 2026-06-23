#!/usr/bin/env python3
"""
ODS Conformance Runner (Layer 1 + Layer 3)

Drives the reference validator (validator/validate.py) over a manifest of
fixtures and produces a deterministic, clause-traceable conformance report.

Exit-code contract of the validator under test:
  0 -> record accepted   (maps to observed "accept")
  1 -> record rejected   (maps to observed "reject")
  other (e.g. 2) -> operational error (maps to observed "operror" -> test ERROR)

A fixture PASSES when observed == expect. A reject fixture that yields exit 2
is an ERROR, not a pass: a clean record-level rejection is required.

The JSON report is emitted in deterministic, canonicalizable form (sorted keys,
compact separators, UTF-8) so its SHA-256 is a reproducible fingerprint of the
result. The report contains no timestamps, hostnames, or absolute paths.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CONF_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CONF_DIR.parent
VALIDATOR = REPO_ROOT / "validator" / "validate.py"
MANIFEST = CONF_DIR / "manifest.json"

# Flags applied per fixture "mode". Layer 2 modes (stored) are reserved for a
# later sub-delivery; the mapping is intentionally explicit and conservative.
MODE_FLAGS = {
    "core": [],
    "profile": [],            # profile validation is automatic when a profile field is present
    "store": ["--store"],     # requires a store directory argument; populated in a later sub-delivery
}


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def observed_from_exit(code: int) -> str:
    return {0: "accept", 1: "reject"}.get(code, f"operror({code})")


def run_fixture(fx: dict) -> dict:
    fixture_path = CONF_DIR / fx["file"]
    flags = MODE_FLAGS.get(fx.get("mode", "core"), [])
    if not fixture_path.exists():
        observed, status = "missing", "ERROR"
    else:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(fixture_path), *flags],
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
        lv = levels.setdefault(r["level"], {"passed": 0, "total": 0})
        lv["total"] += 1
        if r["status"] == "PASS":
            lv["passed"] += 1
    for lv in levels.values():
        lv["verdict"] = "PASS" if lv["passed"] == lv["total"] else "FAIL"

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errored = sum(1 for r in results if r["status"] == "ERROR")

    return {
        "suite": manifest["suite"],
        "suite_version": manifest["suite_version"],
        "spec_version": manifest["spec_version"],
        "validator": "validator/validate.py",
        "summary": {"total": len(results), "passed": passed, "failed": failed, "errored": errored},
        "levels": {k: levels[k] for k in sorted(levels)},
        "results": results,
        "not_covered": manifest.get("not_covered_v1", []),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the ODS conformance suite against the reference validator.")
    ap.add_argument("--level", help="Only run fixtures for this level (e.g. 'Core Basic').")
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
    print(f"  fixtures: {s['total']}  passed: {s['passed']}  failed: {s['failed']}  errored: {s['errored']}")
    for lv in sorted(report["levels"]):
        d = report["levels"][lv]
        print(f"  {lv}: {d['verdict']} ({d['passed']}/{d['total']})")
    for r in report["results"]:
        if r["status"] != "PASS":
            print(f"  [{r['status']}] {r['file']} — expect {r['expect']}, observed {r['observed']}")
    print(f"  report SHA-256: {digest}")
    if report["not_covered"]:
        print("  not covered in this version:")
        for n in report["not_covered"]:
            print(f"    - {n}")

    return 0 if (s["failed"] == 0 and s["errored"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
