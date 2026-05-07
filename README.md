# Operational Decision Standard (ODS)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-Foundation%20Release-success.svg)](./SPECIFICATION.md)
[![Conformance](https://img.shields.io/badge/conformance-Basic%20%7C%20Standard%20%7C%20Full-orange.svg)](./CONFORMANCE.md)
[![Validator](https://img.shields.io/badge/validator-executable-blueviolet.svg)](./validator/)

> **The open standard for institutional decision memory.**

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
| **Reference Implementation** | ORPI Decision Vault™ — first Full-conformance implementation |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [SPECIFICATION.md](./SPECIFICATION.md) | Complete v1.0 technical specification |
| [IMPLEMENTATION.md](./IMPLEMENTATION.md) | Developer guide with code examples |
| [RATIONALE.md](./RATIONALE.md) | Why ODS exists and how it transforms governance |
| [CONFORMANCE.md](./CONFORMANCE.md) | Conformance levels and verification |
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

### Validate a Decision Record

```bash
pip install -r requirements.txt
python validator/validate.py examples/minimal_decision.json
```

Expected output:

```
✓ ODS VALID: compliant with schema v1.0
```

### Minimal Decision Example

```json
{
  "_schema_version": "1.0",
  "identity": {
    "decision_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp_utc": "2026-04-28T14:23:45.123456+00:00",
    "model_version": "v1.0.0",
    "policy_hash": "sha256:..."
  },
  "context": {
    "regime_state": "NORMAL",
    "regime_confidence": 0.87
  },
  "action": {
    "action_type": "APPROVE",
    "expected_value": 0.15
  },
  "cognition": {
    "confidence": 0.72,
    "rationale": "All criteria met within risk tolerance"
  },
  "governance": {
    "audit_trail": [],
    "compliance": {"risk_limit_checks": ["PASSED"]}
  }
}
```

See [examples/](./examples/) for more.

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

The first Full-conformance implementation is **ORPI Decision Vault™** by ORPI Systems.

- 1,786 decisions logged and verified in production
- Append-only storage with SHA-256 chain verification
- Complete meta-learning framework (DPI, CFR, Learning Velocity)
- Real-time governance and compliance reporting

For implementation partnerships, contact ORPI Systems.

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

**v1.x** — schema stability, validator hardening, ecosystem tooling
**v1.1 (Q3 2026)** — multi-party decisions, privacy-preserving extensions, real-time streams
**v2.0 (2027)** — causal inference, cross-organizational benchmarking, blockchain interoperability

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
