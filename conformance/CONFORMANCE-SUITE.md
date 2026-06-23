# ODS Conformance Suite

The conformance suite turns a conformance *claim* into a *reproducible result*. An
implementation runs the suite and obtains a report stating which core/profile levels it
satisfies, traceable to the specific normative clauses exercised. Governed by
DESIGN-MEMO-003.

This is the first sub-delivery (SD-1): the runner and a Layer 1, Core Basic fixture slice.
Later sub-deliveries add the rest of Layer 1 (Standard/Full, store-level, Merkle) and
Layer 3 (ODS-Finance profile fixtures).

## What it tests

- **Layer 1 — record & store conformance (static fixtures).** Each fixture is a real ODS
  record that the reference validator (`validator/validate.py`) MUST accept or MUST reject.
- **Layer 3 — profile conformance.** Profile fixtures, later sub-delivery.

Write-time behavioral invariants (Layer 2 — store-assigned `sequence_number`, write-time
FINAL rejection, append-only enforcement) are **not** covered by the static suite. The
report lists them explicitly under `not_covered` so a result never overstates what it proves.

## How to run

```
python conformance/runner/run_conformance.py
```

Options:
- `--level "Core Basic"` — run only fixtures for one level.
- `--report PATH` — write the canonical JSON report to PATH.

The runner drives the validator over `manifest.json` and reports per-level and per-clause
results, plus a SHA-256 fingerprint of the canonical report.

## Exit-code contract

The validator under test returns: `0` accept, `1` clean record-level reject, other (e.g.
`2`) operational error. A fixture **passes** when the observed outcome equals its declared
`expect`. A reject fixture that yields an operational error is an **ERROR**, not a pass — a
clean rejection is required. The runner exits `0` only if every in-scope fixture passes.

## The manifest

`manifest.json` maps each fixture to `{ file, level, mode, expect, clause, rationale }`.
Fixtures are kept free of test metadata so they remain usable as real examples; the manifest
carries the test semantics and makes clause coverage auditable.

## The report and its fingerprint

The JSON report is emitted in deterministic, canonicalizable form (sorted keys, compact
separators, UTF-8) and contains no timestamps, hostnames, or absolute paths. Its SHA-256 is
therefore a reproducible fingerprint: two runs against the same code and fixtures produce
byte-identical reports and the same digest. The digest printed by the runner equals
`sha256sum` of the `--report` file.

A full ODS-style verifiable-artifact form of the report (attestation/checkpoint model, not a
DECISION) is deferred to a later version per DESIGN-MEMO-003 §7.

## Declaring conformance

A passing report for a level demonstrates conformance to that level's **testable** clauses
as exercised by the in-scope fixtures. State the suite version and the report SHA-256 with
any conformance claim, and note that write-time (Layer 2) clauses are out of scope for the
static suite. Example: "ODS Core v2 Basic — conformance suite v0.1.0, report
SHA-256 `<digest>` (static/Layer 1)."
