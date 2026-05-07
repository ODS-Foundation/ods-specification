# Operational Decision Standard (ODS)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-published-success.svg)](./SPECIFICATION.md)
[![Compliance](https://img.shields.io/badge/compliance-L1%20%7C%20L2%20%7C%20L3-orange.svg)](./SPECIFICATION.md#4-compliance-levels)

> **The open standard for institutional decision memory.**

ODS defines a unified schema and methodology for logging, verifying, and governing organizational decisions in a manner that ensures **immutability**, **auditability**, and **temporal integrity**.

---

## 🎯 The Problem

Organizations make thousands of critical decisions annually. In most cases:

- ❌ Decisions are undocumented or poorly documented
- ❌ Context is lost within weeks
- ❌ Outcomes are not systematically tracked
- ❌ Learning from mistakes is ad hoc
- ❌ Accountability is ambiguous
- ❌ Auditability is impossible

**ODS solves this.**

---

## 💡 The Solution

ODS provides a standardized infrastructure layer for decision governance, analogous to how:

- **ISO 27001** standardizes information security
- **SOC 2** standardizes operational controls
- **GDPR** standardizes data protection

**ODS standardizes decision memory.**

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [**SPECIFICATION.md**](./SPECIFICATION.md) | Complete technical specification (v1.0) |
| [**IMPLEMENTATION.md**](./IMPLEMENTATION.md) | Developer implementation guide |
| [**RATIONALE.md**](./RATIONALE.md) | Why ODS exists and how it transforms governance |
| [**CHANGELOG.md**](./CHANGELOG.md) | Version history |
| [**LICENSE**](./LICENSE) | Apache 2.0 |

---

## 🏗️ Core Architecture

ODS defines a **seven-layer decision schema**:

```
┌─────────────────────────────────────────┐
│  1. IDENTITY                            │  ← Who, when, what version
├─────────────────────────────────────────┤
│  2. CONTEXT                             │  ← State of the world at decision time
├─────────────────────────────────────────┤
│  3. ACTION                              │  ← What was decided
├─────────────────────────────────────────┤
│  4. COGNITION                           │  ← Why (rationale, confidence, uncertainty)
├─────────────────────────────────────────┤
│  5. OUTCOMES                            │  ← What happened (logged after the fact)
├─────────────────────────────────────────┤
│  6. COUNTERFACTUALS                     │  ← What else could have been decided
├─────────────────────────────────────────┤
│  7. GOVERNANCE                          │  ← Audit trail, compliance, explainability
└─────────────────────────────────────────┘
```

Each layer is cryptographically verifiable and append-only.

---

## 🎚️ Compliance Levels

ODS defines three implementation tiers:

### Level 1: Basic Compliance
- ✅ Decision logging with identity layer
- ✅ Immutability (append-only)
- ✅ Basic audit trail
- ✅ 1-year retention
- 📌 **Use Case:** Internal governance

### Level 2: Institutional Compliance
- ✅ All Level 1 requirements
- ✅ Complete context layer
- ✅ Outcome tracking
- ✅ Cryptographic verification
- ✅ 7-year retention
- ✅ Third-party audit capability
- 📌 **Use Case:** Regulated industries

### Level 3: Meta-Learning Compliance
- ✅ All Level 2 requirements
- ✅ Counterfactual tracking
- ✅ Meta-learning framework
- ✅ Decision quality metrics
- ✅ Real-time governance
- ✅ Permanent retention
- 📌 **Use Case:** Mission-critical institutional intelligence

---

## 🚀 Quick Start

### For Developers

1. **Read the specification:** [SPECIFICATION.md](./SPECIFICATION.md)
2. **Follow the implementation guide:** [IMPLEMENTATION.md](./IMPLEMENTATION.md)
3. **Choose your compliance level** (L1, L2, or L3)
4. **Implement the seven-layer schema**
5. **Verify with cryptographic checks**

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

---

## 🌐 Use Cases

ODS applies to any sector where decision quality impacts systemic outcomes:

| Sector | Applications |
|--------|-------------|
| 🏦 **Financial Services** | Trading decisions, credit approvals, risk management |
| 🏥 **Healthcare** | Treatment decisions, resource allocation, clinical trials |
| 📦 **Supply Chain** | Sourcing decisions, inventory management, logistics |
| 🏛️ **Government** | Policy decisions, budget allocation, infrastructure |
| ⚡ **Energy** | Grid management, infrastructure investment |
| 🛡️ **Defense** | Strategic decisions, operational planning |

---

## 🏛️ Reference Implementation

The first ODS **Level 3** compliant implementation is **ORPI Decision Vault™** by ORPI Systems.

- ✅ 1,786 decisions logged and verified
- ✅ Append-only storage with SHA-256 verification
- ✅ Full meta-learning framework
- ✅ Real-time governance

For partnership inquiries: contact ORPI Systems.

---

## 🤝 Contributing

We welcome contributions from organizations, researchers, and individual developers.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- How to propose schema improvements
- RFC (Request for Comments) process
- Community guidelines
- Code of conduct

---

## 📅 Roadmap

### v1.1 (Q3 2026)
- Multi-party decision schema (committee/board decisions)
- Privacy-preserving decision logging (zero-knowledge proofs)
- Real-time decision stream protocols

### v2.0 (2027)
- Causal inference integration
- Cross-organizational decision benchmarking
- Blockchain interoperability

See [CHANGELOG.md](./CHANGELOG.md) for full roadmap.

---

## 📜 License

ODS v1.0 is licensed under **Apache License 2.0**.

You are free to:
- ✅ Use ODS in commercial products
- ✅ Modify and distribute
- ✅ Create derivative standards

See [LICENSE](./LICENSE) for full terms.

---

## 🌟 Why "Decision Memory" Is the Next Infrastructure Category

> *"In a world of synthetic intelligence, verified decision memory is the ultimate moat."*

Read the full thesis in [RATIONALE.md](./RATIONALE.md).

Key insights:
- **AI commoditizes intelligence; institutional memory becomes the differentiator**
- **Decision data compounds in value over time**
- **Time-based moats are unreproducible**
- **Standards create category leaders (Stripe, AWS, Bloomberg)**

---

## 📞 Contact

- **GitHub Issues:** [Report bugs or request features](https://github.com/ODS-Foundation/ods-specification/issues)
- **Discussions:** [Community discussions](https://github.com/ODS-Foundation/ods-specification/discussions)
- **Email:** ods@orpi.systems
- **Web:** https://ods-standard.org *(coming soon)*

---

## ⭐ Star History

If ODS resonates with your work, please star this repository to help others discover it.

---

<div align="center">

**Building the infrastructure for the future of decision governance.**

🏛️ ODS Foundation • 2026

</div>
