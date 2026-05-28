# ODS Conformance

ODS v2.0 defines conformance independently for core and profile. Conformance is **structural** — it describes what an implementation captures and how, not which storage backends or programming languages are used.

---

## Conformance Declaration Format

Conformance is declared as a two-axis statement combining a core level and an optional profile level:

> "ODS Core v2 Standard + ODS-Finance v1 Full"

A core-only declaration is valid for governance-only implementations (no operational `action` fields, no domain profile):

> "ODS Core v2 Basic"

### Conformance Level Cap

A profile conformance level may not exceed the core conformance level.

Profile conformance levels (Standard, Full) require integrity guarantees from the underlying core — Merkle chain at Standard, full audit cryptography at Full. A profile claim of Full while core is only Basic would mean profile-level audit guarantees rest on infrastructure that does not provide them. The cap ensures conformance claims are honest about their actual integrity foundation.

| Core Level | Maximum Profile Level |
|------------|-----------------------|
| Basic | Basic |
| Standard | Standard |
| Full | Full |

---

## Core Conformance Levels

### Basic

A Basic-conformant implementation:

- Writes all records using `_schema_version: "2.0.0"` with `record_type` discriminator (`DECISION` or `OUTCOME`)
- DECISION records include identity, cognition, and governance layers
- DECISION records MUST NOT contain an `outcomes` field
- DECISION records containing an `action` section MUST carry a `profile` field (E4 rule)
- Stores records append-only — once written, never modified or deleted
- Enforces `parent_id` referential integrity at write time: a write is rejected if the referenced `parent_id` does not exist in the store
- Maintains an audit trail per record
- Retains records for at least 1 year

Suitable for: internal governance, early adopters, non-regulated decision flows, governance-only record stores.

### Standard

A Standard-conformant implementation includes everything in Basic, plus:

- Captures context on DECISION records (extensible container; contents determined by profile or implementation)
- Writes OUTCOME records (`record_type: OUTCOME`) when outcomes are realized; outcomes are never written by modifying an existing DECISION record
- Enforces the FINAL uniqueness invariant at write time: a second OUTCOME with `outcome_status: FINAL` for the same `parent_id` is rejected
- Implements the canonical read protocol (SPECIFICATION.md Section 3.5) and exposes it via API (`GET /records/{id}/state`)
- Verifies record integrity with SHA-256 per record using RFC 8785 (JCS) canonical serialization
- Retains records for at least 7 years
- Supports third-party audit access to records and the canonical state API
- **(v2.1.0+)** Assigns a monotonically increasing `sequence_number` to each record at write time; rejects client-submitted records that include a `sequence_number` field
- **(v2.1.0+)** Computes Merkle trees per RFC 6962 §2.1 using the construction specified in SPECIFICATION.md §7.7, ordering leaves by `sequence_number ASC`
- **(v2.1.0+)** Emits `CHECKPOINT` records at minimum every 1,000 Merkle-eligible records or every 24 hours of operation with at least one write, whichever comes first
- **(v2.1.0+)** Exposes inclusion proof API: `GET /records/{id}/proof`
- **(v2.1.0+)** Verifies inclusion proofs against `CHECKPOINT` roots on auditor request

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
- **(v2.1.0+)** Implements consistency proof generation (RFC 6962 §2.1.2) between any two sequential CHECKPOINTs; exposes `GET /checkpoints/{new_id}/consistency?from={old_id}`
- **(v2.1.0+)** Verifies consistency proofs on receipt of new CHECKPOINTs
- **(v2.1.0+)** Supports real-time Merkle verification on record ingest (not only at checkpoint intervals)

Suitable for: mission-critical decision systems, organizations building institutional intelligence as a competitive capability.

---

## Profile Conformance

Profile conformance requirements are defined in each profile's schema and documentation. The profile's conformance levels (Basic, Standard, Full) mirror the core structure but apply to profile-specific fields.

### ODS-Finance/v1 Conformance

| Level | Additional Requirements |
|-------|------------------------|
| Basic | `action_type` present; `profile: "ODS-Finance/v1"` on all operational DECISION records |
| Standard | `regime_state` and `regime_confidence` captured on DECISION records; `risk_limit_checks` present in compliance |
| Full | All Standard requirements; `risk_posture`, `capital_at_risk_bps`, `macro_state_vector` captured; DPI computed with `risk_alignment` dimension using ODS-Finance fields |

---

## Verification

ODS conformance is verifiable through three layers:

1. **Core schema validation** — every record validates against `schema/ods_record_v2.json`. The repository ships an executable validator at `validator/validate.py`.

2. **Profile schema validation** — records with a `profile` field are validated against the corresponding profile schema in `schema/profiles/`. The validator performs this as a second pass after core validation.

3. **Behavioral conformance** — the following behaviors are verifiable in practice, not just at the record level:
   - Append-only writes (no record is ever modified)
   - `parent_id` referential integrity enforced at write time
   - FINAL uniqueness enforced at write time
   - Canonical read protocol produces deterministic results
   - Profile field consistency across a decision graph (OUTCOME `profile` matches parent DECISION `profile`)
   - Retention and audit access policies met

The Technical Committee will publish a formal behavioral conformance test suite as the ecosystem matures. See [ROADMAP.md](./ROADMAP.md).

---

## Operational Stance on Missing Records

An adopting system claiming ODS conformance treats the absence of an ODS record, for any decision the adopter has committed to documenting via ODS, as a fault condition equivalent to silent execution failure.

A conformant operational stance MUST surface missing in-scope records as system alerts, not as routine data quality observations. The distinction is semantic and operational:

- **Treating absence as data quality**: missing records accumulate in monitoring dashboards, are reviewed in batch retrospectives, and may persist for weeks before triage. This stance is incompatible with ODS conformance claims.
- **Treating absence as fault**: missing records trigger alerts at the same severity as silent execution failures. The adopting system architecturally guarantees that a state mutation within its declared ODS scope, without a corresponding record, is an audit failure, not a backlog item.

This stance does not require any schema change. It is a conformance interpretation that distinguishes implementers treating ODS as audit-grade infrastructure from those treating it as logging convention.

Rationale: regulatory frameworks evaluating decision systems (e.g., EU AI Act) expect the audit trail to be complete within its declared scope. An audit trail that tolerates indefinite gaps within its own scope fails the underlying assurance the standard exists to provide.

## Validator Behavior

### Core Validation

The validator performs core schema validation against `schema/ods_record_v2.json` for all records. Core validation checks the identity envelope, record type, and all core-defined fields.

### Profile Validation

When a record contains a `profile` field, the validator performs a second pass against the appropriate profile schema.

**Validation flow:**

1. Validate core schema. If core validation fails, stop and report errors.
2. If `profile` field is present, perform profile validation (see below).
3. If `--store` is provided, perform store-level invariant checks.

### Missing Profile Schema

When the validator encounters a record with a profile field referencing a profile schema that is not available in its local schema directory:

- The validator MUST validate all core fields against the core schema.
- The validator MUST emit an error (not a warning) for the missing profile schema, identifying the profile namespace and the local search path.
- The validator MUST NOT silently skip profile validation. A missing profile schema is a configuration failure, not a record-level error.
- Implementations MAY provide a `--skip-missing-profile` flag for tooling use cases (e.g., bulk inspection without full profile coverage), but this flag MUST NOT be the default behavior.

### Reserved Profile Namespace

When the validator encounters a `profile` field referencing a namespace with status `reserved` in the registry (`schema/profiles/registry.json`):

- The validator MUST emit an error identifying the reserved namespace.
- The validator MUST NOT proceed to profile schema validation (no schema exists for reserved namespaces).

### OUTCOME Record Profile Validation

OUTCOME records have a derived profile association via their parent DECISION.

**Without `--store`:**
- Core fields are validated normally.
- If the OUTCOME carries a `profile` field, the validator performs profile validation on the OUTCOME.
- If the OUTCOME lacks a `profile` field, the validator emits a warning: profile-specific fields in OUTCOME cannot be validated without `--store`.

**With `--store`:**
- The validator resolves the parent DECISION via `parent_id`.
- If the OUTCOME carries an explicit `profile` field, the validator checks it matches the parent DECISION's `profile` field. A mismatch is an error.
- If the OUTCOME lacks a `profile` field, the validator applies the parent's profile schema to the OUTCOME.

---

## Reserved Profile Conformance Claims

Conformance claims against a profile with status `reserved` in [PROFILES.md](./PROFILES.md) are PROHIBITED. Reserved namespaces are placeholders; no profile schema exists, and no implementation may claim conformance with them.

---

## Self-Declaration

Organizations may self-declare conformance at any level by:

1. Implementing the requirements above
2. Documenting their implementation in a public conformance statement
3. Referencing ODS v2.0.0, the core conformance level claimed, and (if applicable) the profile and profile conformance level claimed

Example declaration: *"This implementation is ODS Core v2 Standard + ODS-Finance v1 Standard conformant."*

A formal third-party certification program will follow as the standard matures.

---

## Merkle Conformance Grace Period (v2.1.0)

Implementations currently claiming Standard conformance without Merkle support (i.e., prior to v2.1.0) are given a **90-day grace period** from the v2.1.0 release date to add `sequence_number` assignment, `CHECKPOINT` emission, and inclusion proof support before their Standard conformance claim becomes non-conformant.

As of v2.1.0, there are no known external implementers. The grace period is precautionary and formalizes the transition norm for the record.

---

## Why Three Levels

Most standards fail because they demand too much, too soon. Three levels allow:

- **Adoption velocity** — organizations can reach Basic conformance in weeks, not months
- **Migration path** — clear progression as needs and regulatory requirements grow
- **Right-sizing** — no organization is forced into requirements it does not yet need

---

## See Also

- [SPECIFICATION.md](./SPECIFICATION.md) — full schema, record model, and requirements
- [PROFILES.md](./PROFILES.md) — profile registry, authoring bar, and conformance rules
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) — how to build an ODS-conformant system
- [schema/ods_record_v2.json](./schema/ods_record_v2.json) — executable core JSON Schema
- [schema/profiles/](./schema/profiles/) — profile JSON Schema files
- [validator/validate.py](./validator/validate.py) — schema and store-level validator
