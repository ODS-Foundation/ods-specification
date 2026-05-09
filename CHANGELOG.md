# Changelog

All notable changes to the Operational Decision Standard (ODS) are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-05-08

**v1.1.0 is the first defensible release of ODS.**

v1.0 contained a fundamental immutability contradiction: the specification required that records never be modified, while the reference implementation's `log_outcome()` function modified DECISION records in place to add outcome data. This made v1.0 unauditable by design. v1.1.0 resolves this and two additional audit findings identified during War Council review.

### Fixed

**Audit Finding #1 — Immutability contradiction (critical)**

The core immutability principle (§2.1) was violated by the implementation model. v1.1.0 resolves this by adopting event sourcing semantics: the store is an append-only log of immutable records. Outcomes are now expressed as autonomous OUTCOME records linked to their DECISION via `parent_id`, never by modifying the original DECISION record. This is the same model used by Kafka (append-only log), EventStore (immutable event streams), and Datomic (database of facts where no fact is ever retracted).

**Audit Finding #3 — Decision quality metrics undefined in spec**

DPI, CFR, and Learning Velocity were referenced as Level 3 (Full conformance) requirements but were not formally defined in SPECIFICATION.md — only as pseudocode in IMPLEMENTATION.md. These metrics are now formally defined in SPECIFICATION.md §6 with precise formulas. A provisional weight notice is included: the DPI component weights lack empirical justification and are subject to revision via RFC before v1.2.

**Audit Finding #4 — `policy_hash` not interoperably specified**

The canonical serialization for `policy_hash` was specified as a Python-flavor `json.dumps(sort_keys=True)` convention, which is not portable across programming languages due to edge cases in number formatting and Unicode handling. v1.1.0 specifies RFC 8785 (JSON Canonicalization Scheme, JCS) as the required canonicalization method. The `jcs` library (PyPI) is the reference implementation for Python.

**Audit Finding #6 — SemVer inconsistency**

VERSIONING.md specified three-component SemVer (`1.0.0`, `1.1.0`) while `_schema_version` in records used two-component strings (`"1.0"`). These are now consistent: `_schema_version` uses `"1.1.0"`.

### Changed

- **Unified record model:** All records now share a common identity envelope with `record_type` (discriminator), `record_id`, `timestamp_utc`, and `parent_id`. The field `decision_id` is removed; `record_id` is used across all record types.
- **Schema file renamed:** `schema/ods_decision_v1.json` → `schema/ods_record_v1.json`. The new schema uses JSON Schema `if/then/else` to enforce per-type field requirements.
- **OUTCOME records formalized:** `outcome_status: PARTIAL | FINAL` with write-time enforcement of the one-FINAL-per-chain invariant. `CORRECTION` and `ANNOTATION` types are reserved for v1.x.
- **Canonical read protocol:** SPECIFICATION.md §3.5 defines the normative algorithm for computing the current state of a decision from the record graph. Two conformant implementations reading the same store MUST produce identical results.
- **CORRECTION chain semantics pre-documented:** The terminal record in a correction chain is canonical. CORRECTION on a FINAL OUTCOME is the new canonical FINAL. Invariants are evaluated against the terminal record, not historical records.
- **Conformance levels updated:** Basic, Standard, and Full conformance requirements rewritten in terms of the new record model.
- **`policy_hash` canonical form:** SHA-256(JCS(policy\_object)) per RFC 8785. Concrete example provided in §4.1.1.
- **Validator extended:** `validator/validate.py` now accepts `--store DIR` to check store-level invariants (parent\_id existence, FINAL uniqueness) beyond schema validation.

### Added

- `examples/outcome_partial.json` — example OUTCOME record with `outcome_status: PARTIAL`
- `examples/outcome_final.json` — example OUTCOME record with `outcome_status: FINAL`

### Deprecated

**v1.0 is deprecated as of this release.**

v1.0 MUST NOT be used for new implementations. The immutability contradiction in v1.0 makes any v1.0-compliant system unauditable: a system following the v1.0 spec produces records whose hashes change after outcome logging, breaking the cryptographic audit trail. There is no migration path from v1.0 to v1.1.0 that preserves existing record hashes; implementers should treat v1.0 records as non-conformant and re-log from source systems where possible.

---

## [1.0.0] - 2026-05-06

> **Deprecated.** See [1.1.0] for the reason. v1.0 should not be implemented.

### Added

- Initial release of ODS specification
- Core seven-layer decision schema (identity, context, action, cognition, outcomes, counterfactuals, governance)
- Three conformance levels (Basic, Standard, Full)
- Complete technical specification (SPECIFICATION.md)
- Implementation guide for developers (IMPLEMENTATION.md)
- Six core principles: Immutability, Verifiability, Attribution, Temporal Integrity, Explainability, Outcome Tracking
- Cryptographic verification requirements (SHA-256, Merkle trees)
- Reference implementation: ORPI Decision Vault
- JSON schema with field specifications
- Apache 2.0 license
- ODS Foundation governance model and RFC process

---

## Planned

### v1.2 (RFC pending)
- Empirically validated DPI component weights (replaces provisional weights in §6.1)
- Formal Merkle tree construction specification
- CORRECTION and ANNOTATION record types
- Multi-party decision schema (committee and board decisions)
- Conformance test suite for behavioral invariants

### v2.0 (long-term)
- Causal inference integration
- Cross-organizational decision benchmarking
- AI explainability standards alignment

---

## Contributing

All changes follow the RFC process. See [CONTRIBUTING.md](./CONTRIBUTING.md) and [rfcs/](./rfcs/).

**ODS Foundation** — https://github.com/ODS-Foundation/ods-specification
