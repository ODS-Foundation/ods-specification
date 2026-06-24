# ODS Conformance Suite

The conformance suite turns a conformance *claim* into a *reproducible result*. An
implementation runs the suite and obtains a report stating which core/profile levels it
satisfies, traceable to the specific normative clauses exercised. Governed by
DESIGN-MEMO-003.

## Honest scope (read this first)

The suite tests **statically-decidable clauses only** — clauses that can be decided by
validating records (and small record stores) against the reference validator. Many
Standard and Full requirements are **behavioral** (runtime APIs, retention, CHECKPOINT
cadence, metric computation, Merkle proof generation/verification, real-time signaling) and
**cannot** be decided statically. The report therefore:

- labels every level verdict with the scope qualifier, e.g. `Core Standard
  (statically-decidable clauses): PASS`, and
- enumerates every behavioral clause in a machine-readable `not_covered` list.

A passing static report is necessary but **not sufficient** for a full Standard/Full
conformance claim. The behavioral remainder is certified by the Layer 2 (write-time)
suite, which is the next normative item after the static suite (see DESIGN-MEMO-003
Addendum 2026-06-24).

## Sub-deliveries

- **SD-1** — runner + Layer 1 Core Basic fixture slice.
- **SD-2** — Layer 1 Core Standard static clauses: store-level invariants (parent_id
  existence, FINAL uniqueness) and stored-mode `sequence_number` (required/accepted).
- **SD-3** — Layer 3 profile fixtures (ODS-Finance/v1) incl. OUTCOME profile consistency (C4).

## What it tests

- **Layer 1 — record & store conformance (static fixtures).** Each fixture is a real ODS
  record (or candidate validated against a small store) that the reference validator
  (`validator/validate.py`) MUST accept or MUST reject.
- **Layer 3 — profile conformance.** Ships in SD-3.

## Fixture modes

- `core` — `validate.py <candidate>`
- `stored` — `validate.py --stored <candidate>` (stored records MUST carry `sequence_number`)
- `store` — `validate.py --store <store_dir> <candidate>`; the candidate lives **outside**
  the store directory, which holds the pre-existing records.

## How to run

```
python conformance/runner/run_conformance.py
```

Options:
- `--level "Core Standard"` — run only fixtures for one level.
- `--report PATH` — write the canonical JSON report to PATH.

## Exit-code contract

The validator returns: `0` accept, `1` clean reject, other (e.g. `2`) operational error. A
fixture passes when the observed outcome equals its declared `expect`. A reject fixture that
yields an operational error is an ERROR, not a pass. The runner exits `0` only if every
in-scope fixture passes.

## The manifest

`manifest.json` maps each fixture to `{ file, level, mode, expect, clause, rationale }`
(plus `store` for store-mode fixtures). It also carries the structured `not_covered` list:
each entry is `{ level, clause, category, reason }`, where `category` is
`behavioral (Layer 2)`, `behavioral (policy)`, or `Layer 3 (later static sub-delivery)`.

## The report and its fingerprint

The JSON report is deterministic (sorted keys, compact separators, UTF-8) and contains no
timestamps, hostnames, or absolute paths. Its SHA-256 is a reproducible fingerprint and
equals `sha256sum` of the `--report` file. A full ODS-style verifiable-artifact form of the
report (attestation/checkpoint model, not a DECISION) is deferred per DESIGN-MEMO-003 §7.

## Declaring conformance

State the suite version, the report SHA-256, and the scope qualifier with any claim, e.g.
"ODS Core v2 Standard (statically-decidable clauses) — conformance suite v0.2.0, report
SHA-256 `<digest>`". Do not drop the qualifier: it is what keeps the claim honest until the
Layer 2 behavioral suite lands.
