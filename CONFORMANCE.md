# ODS Conformance

ODS defines three conformance levels so organizations can adopt the standard at the depth that fits their needs and resources.

Conformance is **structural** — it describes what an implementation captures and how, not which implementation tools or storage backends are used.

---

## Levels

### Basic

A Basic-conformant implementation:

- Records every decision in the ODS schema (identity, action, cognition, governance layers required)
- Stores records append-only — once written, never modified or deleted
- Maintains a structural audit trail per decision
- Retains records for at least 1 year

Suitable for: internal governance, early adopters, non-regulated decision flows.

### Standard

A Standard-conformant implementation includes everything in Basic, plus:

- Captures the context layer (state of the world at decision time)
- Logs outcomes when they are realized
- Verifies record integrity with cryptographic hashing (SHA-256 minimum)
- Retains records for at least 7 years
- Supports third-party audit access

Suitable for: regulated industries, enterprise governance, organizations preparing for external audit.

### Full

A Full-conformant implementation includes everything in Standard, plus:

- Captures counterfactuals — alternative actions considered and their expected outcomes
- Computes decision quality metrics (DPI, CFR, Learning Velocity per the specification)
- Supports real-time governance and compliance signaling
- Retains records permanently

Suitable for: mission-critical decision systems, organizations building institutional intelligence as a competitive capability.

---

## Verification

ODS conformance is verifiable through three layers:

1. **Schema validation** — every record validates against the JSON Schema in `schema/ods_decision_v1.json`. The repository ships an executable validator at `validator/validate.py`.

2. **Structural conformance** — the implementation's data model includes the required layers for its declared conformance level.

3. **Behavioral conformance** — append-only writes, retention, and audit-trail integrity are verifiable in practice (not just at the record level).

The Technical Committee will publish more detailed verification tooling and procedures as the ecosystem matures. See [ROADMAP.md](./ROADMAP.md).

---

## Self-Declaration

For now, organizations may self-declare conformance at Basic, Standard, or Full level by:

1. Implementing the requirements above
2. Documenting their implementation in a public conformance statement
3. Referencing ODS v1.0 and the conformance level claimed

A formal certification program will follow as the standard matures.

---

## Why Three Levels

Most standards fail because they demand too much, too soon. Three levels allow:

- **Adoption velocity** — organizations can start at Basic in weeks, not months
- **Migration path** — clear progression as needs grow
- **Right-sizing** — no organization is forced into requirements it doesn't need

The reference implementation — ORPI Decision Vault™ — operates at Full conformance and demonstrates what is possible at the highest level.

---

## See Also

- [SPECIFICATION.md](./SPECIFICATION.md) — full schema and requirements
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) — how to build an ODS-conformant system
- [validator/](./validator/) — executable schema validator
