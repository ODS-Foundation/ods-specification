# Operational Decision Standard (ODS)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-Stable-success.svg)](./SPECIFICATION.md)
[![Conformance](https://img.shields.io/badge/conformance-Core%20%2B%20Profiles-orange.svg)](./CONFORMANCE.md)
[![Validator](https://img.shields.io/badge/validator-executable-blueviolet.svg)](./validator/)

> **The open standard for institutional decision memory.**

> **Current version: v2.0.0** — introduces the ODS Core + Profiles architecture. Finance-domain fields are now in ODS-Finance/v1 profile; the core specification is domain-agnostic. v1.1.0 records remain valid; see [CHANGELOG.md](./CHANGELOG.md) for the migration path. v1.0 is deprecated and must not be implemented.

ODS defines the schema, governance, and verification model for organizations to capture, audit, and learn from their decisions over time.

It is the missing infrastructure layer between data warehouses (which record *what happened*) and audit logs (which record *system events*) — ODS records *the decisions themselves*.

---

## Why ODS Exists

Organizations make thousands of consequential decisions every year — credit approvals, treatment plans, policy choices, capital allocations, supply-chain pivots.

Most are never captured in a structured, verifiable, auditable way.

The cost is real:

- **Institutional amnesia.** Why was this approved last year? No one remembers.
- **Accountability gaps.** When outcomes diverge, the reasoning is lost.
- **Regulatory exposure.** Auditors and regulators increasingly demand decision trails.
- **Learning failure.** AI and ML systems cannot improve without outcome-linked decision records.

ODS addresses this gap with a single, open, neutral specification.

---

## What ODS Provides

| Layer | Purpose |
|-------|---------|
| **Schema** | A seven-layer decision record (identity, context, action, cognition, outcomes, counterfactuals, governance) |
| **Conformance Levels** | Three tiers — Basic, Standard, Full — for graduated adoption |
| **Validator** | An executable schema validator (`validator/validate.py`) |
| **Governance** | RFC process, versioning policy, and stability guarantees |
| **Reference Implementation** | ORPI Decision Vault — reference implementation of ODS Core v2.0.0 |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [SPECIFICATION.md](./SPECIFICATION.md) | Complete v2.0.0 technical specification |
| [PROFILES.md](./PROFILES.md) | Profile registry, authoring bar, and conformance rules |
| [CONFORMANCE.md](./CONFORMANCE.md) | Two-axis conformance levels and verification |
| [IMPLEMENTATION.md](./IMPLEMENTATION.md) | Developer guide with code examples |
| [RATIONALE.md](./RATIONALE.md) | Why ODS exists and how it transforms governance |
| [GOVERNANCE.md](./GOVERNANCE.md) | Project governance model |
| [VERSIONING.md](./VERSIONING.md) | Versioning and stability policy |
| [COMPATIBILITY.md](./COMPATIBILITY.md) | Backward compatibility commitments |
| [ROADMAP.md](./ROADMAP.md) | Phased ecosystem evolution |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | How to contribute |
| [CHANGELOG.md](./CHANGELOG.md) | Version history |

---

## Schema at a Glance

ODS records every decision in a seven-layer schema:

```
┌─────────────────────────────────────────────────┐
│  1. IDENTITY        — who, when, what version   │
├─────────────────────────────────────────────────┤
│  2. CONTEXT         — state of the world        │
├─────────────────────────────────────────────────┤
│  3. ACTION          — what was decided          │
├─────────────────────────────────────────────────┤
│  4. COGNITION       — rationale and confidence  │
├─────────────────────────────────────────────────┤
│  5. OUTCOMES        — what actually happened    │
├─────────────────────────────────────────────────┤
│  6. COUNTERFACTUALS — what else was considered  │
├─────────────────────────────────────────────────┤
│  7. GOVERNANCE      — audit trail, compliance   │
└─────────────────────────────────────────────────┘
```

Records are append-only and cryptographically verifiable. See [SPECIFICATION.md](./SPECIFICATION.md) for the full data model.

---

## Conformance Levels

ODS defines three tiers so organizations can adopt incrementally:

- **Basic** — minimum viable decision logging with structural integrity
- **Standard** — institutional-grade auditability with verifiable history
- **Full** — meta-learning capability with counterfactuals and outcome tracking

Full details in [CONFORMANCE.md](./CONFORMANCE.md).

---

## Quick Start

### Validate a Record

```bash
pip install jsonschema jcs
python validator/validate.py examples/core_only_decision.json
python validator/validate.py examples/finance_decision.json
```

Expected output:

```
✓ ODS VALID: DECISION record compliant with core schema v2.0.0
✓ ODS VALID: DECISION record compliant with core schema v2.0.0 [ODS-Finance/v1]
```

### Core-Only Record (governance, no profile)

```json
{
  "_schema_version": "2.0.0",
  "record_type": "DECISION",
  "record_id": "7a3f1c2e-0001-4000-a000-000000000001",
  "timestamp_utc": "2026-05-09T10:00:00.000000+00:00",
  "identity": {
    "model_version": "v1.0.0",
    "policy_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "cognition": {
    "confidence": 1.0,
    "rationale": "Policy attestation logged for Q2 2026 governance review."
  },
  "governance": {
    "audit_trail": [{"timestamp_utc": "2026-05-09T10:00:00+00:00", "event": "DECISION_CREATED", "actor": "GOVERNANCE_SYSTEM", "metadata": {}}]
  }
}
```

### Finance Decision (with ODS-Finance/v1 profile)

```json
{
  "_schema_version": "2.0.0",
  "record_type": "DECISION",
  "record_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp_utc": "2026-05-09T14:23:45.123456+00:00",
  "profile": "ODS-Finance/v1",
  "identity": { "model_version": "v2.1.0", "policy_hash": "189bff6265300365c5ff0d775393db04714f1476ef063bc99a215c9e46a16971" },
  "context": { "regime_state": "NORMAL", "volatility_state": "ELEVATED" },
  "action": { "action_type": "BUY", "action_size": 50000.0, "expected_value": 0.08, "risk_posture": 0.62 },
  "cognition": { "confidence": 0.78, "rationale": "Momentum signal above threshold in elevated-volatility regime." },
  "governance": {
    "audit_trail": [{"timestamp_utc": "2026-05-09T14:23:45+00:00", "event": "DECISION_CREATED", "actor": "ALPHA_ENGINE_v2.1", "metadata": {}}],
    "compliance": { "policy_violations": [], "approvals": ["AUTO_APPROVED"], "risk_limit_checks": ["VAR_LIMIT_PASSED"] }
  }
}
```

See [examples/](./examples/) for complete records.

---

## Where ODS Applies

| Sector | Decisions ODS Captures |
|--------|------------------------|
| Financial services | Trading, credit, risk, capital allocation |
| Healthcare | Treatment plans, resource allocation, clinical trials |
| Supply chain | Sourcing, inventory, logistics, supplier selection |
| Government | Policy decisions, budget allocation, infrastructure |
| Energy | Grid management, infrastructure investment |
| Defense | Strategic and operational planning |

Any sector where a decision has consequences — and someone, eventually, will need to know *why*.

---

## Reference Implementation

ODS has an open reference implementation — **[ORPI Decision Vault](https://github.com/ODS-Foundation/ods-reference-implementation)** — a small, faithful implementation of ODS Core v2.0.0. Records written by it validate against the standard's own JSON Schema using the standard's own validator.

- Append-only storage with write-once enforcement and SHA-256 hash-chain integrity
- Independent ledger verification: schema, temporal order, tamper detection, chain continuity
- Counterfactual capture (no decision without its alternative) and outcome linkage via separate OUTCOME records
- Distilled from the original ORPI Decision Vault; the private system's trading and strategy logic is not part of this repository

See the [reference implementation](https://github.com/ODS-Foundation/ods-reference-implementation) to read, run, and verify it yourself.

---

## Why an Open Standard

Infrastructure that compounds in value belongs to no one and everyone.

Open standards have won every major infrastructure category:

- TCP/IP over proprietary networking
- HTTP and HTML over walled gardens
- SQL over proprietary query languages
- Linux over proprietary Unix

Decision memory infrastructure follows the same trajectory. Standardization is what makes interoperability, auditability, and ecosystem development possible.

ODS is licensed Apache 2.0. Use it commercially, modify it, build on it.

---

## Governance

ODS is maintained through an open RFC process. Proposed changes go through structured review before acceptance into the specification.

See:
- [GOVERNANCE.md](./GOVERNANCE.md) for governance model
- [CONTRIBUTING.md](./CONTRIBUTING.md) for how to participate
- [rfcs/](./rfcs/) for active and accepted proposals

The Technical Committee makes final decisions on RFC acceptance, major versions, and conformance certification standards.

---

## Roadmap

**v2.0.0 (current)** — ODS Core + Profiles architecture; ODS-Finance/v1 first authored profile; domain-agnostic core
**v2.1 (planned)** — CORRECTION/ANNOTATION record types, empirically validated DPI weights, ODS-Healthcare/v1 RFC
**v2.x (roadmap)** — causal inference integration, cross-organizational benchmarking, AI explainability alignment

Full plan in [ROADMAP.md](./ROADMAP.md).

---

## Contact

- **Issues:** [GitHub Issues](https://github.com/ODS-Foundation/ods-specification/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ODS-Foundation/ods-specification/discussions)
- **RFCs:** [rfcs/](./rfcs/)

---

## License

Apache License 2.0. See [LICENSE](./LICENSE).

---

<div align="center">

**Decision memory is infrastructure that compounds.**

🏛️ ODS Foundation — 2026

</div>
