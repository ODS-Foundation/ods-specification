# ODS Conformance

ODS defines three conformance levels so organizations can adopt the standard at the depth that fits their needs and resources.

Conformance is **structural** — it describes what an implementation captures and how, not which storage backends or programming languages are used.

---

## Levels

### Basic

A Basic-conformant implementation:

- Writes all records using the unified ODS schema with `record_type` discriminator (`DECISION` or `OUTCOME`)
- DECISION records include the identity, action, and cognition layers
- DECISION records MUST NOT contain an `outcomes` field
- Stores records append-only — once written, never modified or deleted
- Enforces `parent_id` referential integrity at write time: a write is rejected if the referenced `parent_id` does not exist in the store
- Maintains an audit trail per record
- Retains records for at least 1 year

Suitable for: internal governance, early adopters, non-regulated decision flows.

### Standard

A Standard-conformant implementation includes everything in Basic, plus:

- Captures the context layer on DECISION records (state of the world at decision time)
- Writes OUTCOME records (`record_type: OUTCOME`) when outcomes are realized; outcomes are never written by modifying an existing DECISION record
- Enforces the FINAL uniqueness invariant at write time: a second OUTCOME with `outcome_status: FINAL` for the same `parent_id` is rejected
- Implements the canonical read protocol (SPECIFICATION.md Section 3.5) and exposes it via API (`GET /records/{id}/state`)
- Verifies record integrity with SHA-256 per record using canonical JSON serialization (keys sorted, no whitespace)
- Retains records for at least 7 years
- Supports third-party audit access to records and the canonical state API

Suitable for: regulated industries, enterprise governance, organizations preparing for external audit.

### Full

A Full-conformant implementation includes everything in Standard, plus:

- Captures counterfactuals on DECISION records — alternative actions considered and their expected outcomes
- Computes the three decision quality metrics defined in SPECIFICATION.md Section 6, using the prescribed formulas:
  - **DPI** (Decision Performance Index)
  - **CFR** (Counterfactual Regret)
  - **Learning Velocity** (OLS regression slope of DPI over time)
- Supports real-time governance and compliance signaling
- Retains records permanently

Suitable for: mission-critical decision systems, organizations building institutional intelligence as a competitive capability.

---

## Verification

ODS conformance is verifiable through three layers:

1. **Schema validation** — every record validates against the JSON Schema in `schema/ods_record_v1.json`. The repository ships an executable validator at `validator/validate.py`.

2. **Structural conformance** — the implementation's record model includes the required layers for its declared conformance level, and excludes prohibited fields (e.g., no `outcomes` field on DECISION records).

3. **Behavioral conformance** — the following behaviors are verifiable in practice, not just at the record level:
   - Append-only writes (no record is ever modified)
   - `parent_id` referential integrity enforced at write time
   - FINAL uniqueness enforced at write time
   - Canonical read protocol produces deterministic results
   - Retention and audit access policies met

The Technical Committee will publish a formal behavioral conformance test suite as the ecosystem matures. See [ROADMAP.md](./ROADMAP.md).

---

## Self-Declaration

Organizations may self-declare conformance at Basic, Standard, or Full level by:

1. Implementing the requirements above
2. Documenting their implementation in a public conformance statement
3. Referencing ODS v1.0.0 and the conformance level claimed

A formal third-party certification program will follow as the standard matures.

---

## Why Three Levels

Most standards fail because they demand too much, too soon. Three levels allow:

- **Adoption velocity** — organizations can reach Basic conformance in weeks, not months
- **Migration path** — clear progression as needs and regulatory requirements grow
- **Right-sizing** — no organization is forced into requirements it does not yet need

---

## See Also

- [SPECIFICATION.md](./SPECIFICATION.md) — full schema, record model, and requirements
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) — how to build an ODS-conformant system
- [schema/ods_record_v1.json](./schema/ods_record_v1.json) — executable JSON Schema
- [validator/validate.py](./validator/validate.py) — schema and store-level validator
