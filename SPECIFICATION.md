# Operational Decision Standard (ODS) v1.0

**Status:** PUBLISHED  
**Version:** 1.0  
**Date:** April 2026  
**License:** Apache 2.0  
**Maintainer:** ODS Foundation

---

## Abstract

The Operational Decision Standard (ODS) defines a unified schema and methodology for institutional decision memory systems. ODS establishes requirements for logging, verifying, and governing organizational decisions in a manner that ensures immutability, auditability, and temporal integrity.

This standard addresses a critical gap in enterprise infrastructure: the absence of verifiable, auditable decision trails. While organizations invest heavily in data warehouses, business intelligence, and analytics, they lack standardized infrastructure for decision governance—the process of capturing, validating, and learning from decisions over time.

ODS provides this missing infrastructure layer.

**Scope:** This standard applies to all organizational decisions where:
- Financial impact exceeds material thresholds
- Regulatory compliance requires audit trails
- Institutional learning depends on historical context
- Accountability mechanisms require attribution

**Applicability:** Financial services, healthcare, government, supply chain, energy, infrastructure, and any sector where decision quality impacts systemic outcomes.

---

## 1. Introduction

### 1.1 Purpose

Organizations make thousands of critical decisions annually. In most cases:
- Decisions are undocumented or poorly documented
- Context is lost within weeks
- Outcomes are not systematically tracked
- Learning from mistakes is ad hoc
- Accountability is ambiguous
- Auditability is impossible

ODS solves this by defining:
1. **Decision Schema** — standardized structure for decision records
2. **Governance Requirements** — audit trails, compliance, explainability
3. **Temporal Integrity** — immutable logging with cryptographic verification
4. **Meta-Learning Framework** — systematic improvement mechanisms
5. **Compliance Levels** — tiered implementation pathways

### 1.2 Problem Statement

Modern organizations face a decision governance crisis:

**Institutional Amnesia:** Companies forget why critical decisions were made, leading to repeated mistakes and loss of institutional knowledge.

**Accountability Gaps:** When outcomes diverge from expectations, reconstructing decision context is often impossible, preventing meaningful accountability.

**Regulatory Risk:** Sectors like finance, healthcare, and energy face increasing regulatory scrutiny. Without verifiable decision trails, compliance is difficult to demonstrate.

**Learning Failure:** Organizations cannot systematically improve decision quality without rigorous tracking of decision-outcome relationships.

**Trust Erosion:** Stakeholders (boards, regulators, investors, public) demand transparency. Decision opacity creates risk.

### 1.3 Solution Approach

ODS provides a standardized infrastructure layer for decision governance, analogous to how:
- ISO 27001 standardizes information security
- SOC 2 standardizes operational controls
- GDPR standardizes data protection

ODS standardizes **decision memory**.

---

## 2. Core Principles

ODS implementations MUST adhere to six constitutional principles:

### 2.1 Immutability

**Requirement:** Once logged, decision records MUST NOT be modified or deleted.

**Rationale:** Temporal integrity depends on immutable history. Any system that allows retroactive modification destroys auditability and trust.

**Implementation:** Append-only data structures, cryptographic hashing, write-once storage.

### 2.2 Verifiability

**Requirement:** Every decision MUST be cryptographically verifiable against tampering.

**Rationale:** Audit credibility requires proof that records have not been altered.

**Implementation:** SHA-256 hashing, Merkle trees, blockchain-inspired verification (without requiring distributed consensus).

### 2.3 Attribution

**Requirement:** Every decision MUST be attributable to specific actors, models, or processes.

**Rationale:** Accountability requires knowing who/what made a decision and why.

**Implementation:** Actor logging, model versioning, process attribution.

### 2.4 Temporal Integrity

**Requirement:** Every decision MUST capture complete temporal context—state of the world at decision time.

**Rationale:** Reconstructing decisions requires knowing what information was available when the decision was made.

**Implementation:** Snapshot mechanisms, state versioning, temporal databases.

### 2.5 Explainability

**Requirement:** Every decision MUST include rationale, assumptions, and expected outcomes.

**Rationale:** Trust and learning require understanding *why* decisions were made, not just *what* was decided.

**Implementation:** Structured rationale fields, assumption logging, expected value documentation.

### 2.6 Outcome Tracking

**Requirement:** Every decision MUST support outcome logging and post-decision analysis.

**Rationale:** Learning requires feedback loops. Decisions without outcome tracking cannot improve over time.

**Implementation:** Outcome schemas, counterfactual frameworks, performance metrics.

---

## 3. Schema Definition

### 3.1 Core Schema Structure

ODS defines a seven-layer decision schema:

```json
{
  "_schema_version": "1.0",
  
  "identity": {
    "decision_id": "UUID",
    "timestamp_utc": "ISO 8601",
    "model_version": "string",
    "policy_hash": "SHA-256"
  },
  
  "context": {
    "regime_state": "enum",
    "regime_confidence": "float [0,1]",
    "volatility_state": "enum",
    "macro_state_vector": []
  },
  
  "action": {
    "action_type": "enum",
    "action_size": "float",
    "risk_posture": "float [0,1]",
    "capital_at_risk_bps": "integer",
    "expected_value": "float"
  },
  
  "cognition": {
    "expected_value": "float",
    "confidence": "float [0,1]",
    "uncertainty_score": "float [0,1]",
    "decision_latency_ms": "integer",
    "rationale": "string"
  },
  
  "outcomes": {
    "actual_result": "float",
    "realized_at": "ISO 8601",
    "delta_from_expected": "float",
    "outcome_quality": "float [0,1]"
  },
  
  "counterfactuals": [
    {
      "alternative_action": "string",
      "expected_outcome": "float",
      "regret": "float"
    }
  ],
  
  "governance": {
    "audit_trail": [],
    "explainability": {},
    "compliance": {}
  }
}
```

### 3.2 Field Specifications

#### 3.2.1 Identity Layer

**decision_id** (required)
- Type: UUID v4
- Purpose: Unique identifier for decision
- Constraints: Must be globally unique
- Example: `"550e8400-e29b-41d4-a716-446655440000"`

**timestamp_utc** (required)
- Type: ISO 8601 datetime with timezone
- Purpose: Moment decision was made
- Constraints: Must be UTC, microsecond precision
- Example: `"2026-04-28T14:23:45.123456+00:00"`

**model_version** (required)
- Type: Semantic version string
- Purpose: Track which decision model/process was used
- Constraints: Must follow semver (e.g., v2.1.3)
- Example: `"v2.1.0"`

**policy_hash** (required)
- Type: SHA-256 hash
- Purpose: Cryptographic fingerprint of decision policy
- Constraints: 64-character hexadecimal
- Example: `"a1b2c3..."`

#### 3.2.2 Context Layer

**regime_state** (required)
- Type: Enum
- Purpose: Detected environmental regime at decision time
- Values: `[NORMAL, TRANSITION, CRISIS, RECOVERY]`
- Example: `"NORMAL"`

**regime_confidence** (required)
- Type: Float
- Purpose: Confidence in regime detection
- Constraints: [0.0, 1.0]
- Example: `0.87`

**macro_state_vector** (optional)
- Type: Array of floats
- Purpose: Normalized macro-economic indicators
- Example: `[0.12, -0.34, 0.56]`

#### 3.2.3 Action Layer

**action_type** (required)
- Type: Enum
- Purpose: Category of action taken
- Values: `[BUY, SELL, HOLD, REDUCE, INCREASE, ABSTAIN]`
- Example: `"HOLD"`

**action_size** (required)
- Type: Float
- Purpose: Magnitude of action
- Constraints: Domain-specific (e.g., % of portfolio)
- Example: `0.25` (25% of portfolio)

**risk_posture** (required)
- Type: Float
- Purpose: Risk appetite at decision time
- Constraints: [0.0, 1.0] where 0=minimum risk, 1=maximum risk
- Example: `0.60`

**expected_value** (required)
- Type: Float
- Purpose: Expected outcome of decision
- Example: `0.15` (15% expected return)

#### 3.2.4 Cognition Layer

**confidence** (required)
- Type: Float
- Purpose: Decision maker's confidence in decision
- Constraints: [0.0, 1.0]
- Example: `0.72`

**uncertainty_score** (required)
- Type: Float
- Purpose: Quantified epistemic uncertainty
- Constraints: [0.0, 1.0], often `1 - confidence`
- Example: `0.28`

**decision_latency_ms** (required)
- Type: Integer
- Purpose: Time taken to make decision
- Constraints: Milliseconds
- Example: `1523`

**rationale** (required)
- Type: String
- Purpose: Human/machine-readable explanation
- Constraints: 50-500 characters
- Example: `"Market volatility elevated. Regime transition detected. Reducing exposure to preserve capital."`

#### 3.2.5 Outcomes Layer

**actual_result** (required after outcome)
- Type: Float
- Purpose: Realized outcome
- Example: `0.12` (12% actual return)

**realized_at** (required after outcome)
- Type: ISO 8601 datetime
- Purpose: When outcome was measured
- Example: `"2026-05-15T09:00:00+00:00"`

**delta_from_expected** (computed)
- Type: Float
- Purpose: Difference between expected and actual
- Formula: `actual_result - expected_value`
- Example: `-0.03` (underperformed by 3%)

#### 3.2.6 Counterfactuals Layer

**alternative_action** (required)
- Type: String
- Purpose: Action not taken
- Example: `"SELL"`

**expected_outcome** (required)
- Type: Float
- Purpose: Estimated outcome of alternative
- Example: `0.18`

**regret** (computed)
- Type: Float
- Purpose: Difference between alternative and chosen action
- Formula: `alternative_expected_outcome - actual_result`
- Example: `0.06` (6% regret)

#### 3.2.7 Governance Layer

**audit_trail** (required)
- Type: Array of events
- Purpose: Immutable log of all modifications
- Schema: `[{timestamp, event, actor, metadata}]`

**explainability** (optional)
- Type: Object
- Purpose: Additional context for regulatory/audit needs
- Example: Feature importances, SHAP values, decision trees

**compliance** (required)
- Type: Object
- Purpose: Regulatory compliance tracking
- Fields: `risk_limit_checks`, `policy_violations`, `approvals`

---

## 4. Compliance Levels

ODS defines three implementation tiers:

### 4.1 Level 1: Basic Compliance

**Requirements:**
- ✅ Decision logging with identity layer
- ✅ Immutability (append-only)
- ✅ Basic audit trail
- ✅ Minimum 1-year retention

**Use Cases:** Internal governance, basic accountability

**Certification:** Self-attestation

---

### 4.2 Level 2: Institutional Compliance

**Requirements:**
- ✅ All Level 1 requirements
- ✅ Complete context layer
- ✅ Outcome tracking
- ✅ Cryptographic verification
- ✅ Minimum 7-year retention
- ✅ Third-party audit capability

**Use Cases:** Regulated industries, enterprise governance

**Certification:** Third-party audit required

---

### 4.3 Level 3: Meta-Learning Compliance

**Requirements:**
- ✅ All Level 2 requirements
- ✅ Counterfactual tracking
- ✅ Meta-learning framework
- ✅ Decision quality metrics
- ✅ Learning velocity measurement
- ✅ Real-time governance
- ✅ Permanent retention

**Use Cases:** Mission-critical systems, institutional intelligence

**Certification:** Continuous third-party monitoring

---

## 5. Implementation Requirements

### 5.1 Storage Requirements

**Immutability:** ODS-compliant systems MUST use append-only storage.

**Acceptable implementations:**
- Append-only files with cryptographic chaining
- Write-once databases (e.g., WORM storage)
- Immutable object storage (e.g., AWS S3 Object Lock)
- Blockchain-based storage (optional, not required)

**Prohibited:**
- Mutable databases without immutability guarantees
- Storage systems that allow silent modification

### 5.2 Cryptographic Requirements

**Hashing:** SHA-256 minimum for decision fingerprinting

**Verification:** Merkle tree or equivalent for batch verification

**Signing:** Optional but recommended for high-security environments

### 5.3 Temporal Requirements

**Clock Synchronization:** NTP or equivalent, ±100ms accuracy

**Timezone:** All timestamps MUST be UTC

**Precision:** Microsecond minimum

### 5.4 API Requirements

ODS-compliant systems SHOULD expose:
- `POST /decisions` — Log new decision
- `GET /decisions/{id}` — Retrieve decision
- `GET /decisions` — Query decisions
- `PUT /decisions/{id}/outcome` — Log outcome
- `GET /decisions/{id}/verify` — Cryptographic verification

---

## 6. Relationship to Existing Standards

### 6.1 ISO 27001 (Information Security)

ODS complements ISO 27001 by providing:
- Decision-specific audit trails
- Immutability guarantees
- Temporal integrity

ISO 27001 focuses on information security controls. ODS focuses on decision governance.

### 6.2 SOC 2 (Service Organization Controls)

ODS enhances SOC 2 compliance by:
- Providing verifiable decision logs
- Enabling continuous monitoring
- Supporting audit requirements

SOC 2 defines operational controls. ODS defines decision memory.

### 6.3 GDPR (Data Protection)

ODS is compatible with GDPR:
- Right to explanation → explainability layer
- Right to erasure → handle via anonymization, not deletion
- Data minimization → log only decision-relevant data

### 6.4 Basel III / Dodd-Frank (Financial Regulation)

ODS supports regulatory compliance:
- Risk decision audit trails
- Model governance
- Stress test documentation

---

## 7. Reference Implementation

### 7.1 ORPI Decision Vault™

The first ODS Level 3 compliant implementation is **ORPI Decision Vault™**.

**Features:**
- ✅ Seven-layer decision schema
- ✅ Append-only storage with SHA-256 verification
- ✅ Complete counterfactual tracking
- ✅ Meta-learning framework (DPI, CFR, Observer Drift)
- ✅ Real-time governance
- ✅ Learning velocity measurement

**Source:** Open-source reference implementation available at github.com/orpi-systems/decision-vault

### 7.2 Implementation Guide

See [IMPLEMENTATION.md](./IMPLEMENTATION.md) for step-by-step instructions.

---

## 8. Versioning and Governance

### 8.1 Version Control

ODS follows semantic versioning:
- **Major version** (X.0.0) — Breaking schema changes
- **Minor version** (1.X.0) — Backward-compatible additions
- **Patch version** (1.0.X) — Clarifications, bug fixes

Current version: **1.0**

### 8.2 Governance Process

ODS is maintained by the **ODS Foundation**, a community-driven standards body.

**Proposal Process:**
1. Submit RFC (Request for Comments)
2. Community review (30 days)
3. Technical committee vote
4. Publication

**Contact:** ods@orpi.systems

---

## 9. Adoption and Certification

### 9.1 Self-Certification (Level 1)

Organizations may self-certify Level 1 compliance by:
1. Implementing minimum requirements
2. Documenting compliance
3. Publishing attestation

### 9.2 Third-Party Audit (Level 2)

Level 2 requires audit by certified ODS auditors:
- Schema compliance verification
- Cryptographic verification testing
- Retention policy audit
- Outcome tracking validation

### 9.3 Continuous Monitoring (Level 3)

Level 3 requires ongoing third-party monitoring:
- Real-time compliance dashboard
- Quarterly audits
- Annual recertification

---

## 10. Use Cases

### 10.1 Financial Services

**Application:** Trading decisions, credit approvals, risk management

**Benefits:**
- Regulatory compliance (MiFID II, Dodd-Frank)
- Model governance
- Backtesting verification
- Accountability for trading losses

### 10.2 Healthcare

**Application:** Treatment decisions, resource allocation, clinical trials

**Benefits:**
- Patient safety
- Clinical decision support
- Research reproducibility
- Malpractice defense

### 10.3 Supply Chain

**Application:** Sourcing decisions, inventory management, logistics

**Benefits:**
- Disruption analysis
- Supplier accountability
- Demand forecasting improvement
- Crisis response optimization

### 10.4 Government

**Application:** Policy decisions, budget allocation, infrastructure

**Benefits:**
- Public accountability
- Evidence-based policymaking
- Institutional memory preservation
- Corruption prevention

---

## 11. Future Directions

### 11.1 Planned Enhancements (v1.1)

- Multi-party decision schema (committee/board decisions)
- Privacy-preserving decision logging (zero-knowledge proofs)
- Interoperability with blockchain systems
- Real-time decision stream protocols

### 11.2 Research Areas

- Causal inference integration
- Adversarial decision detection
- Cross-organizational decision benchmarking
- AI explainability standards integration

---

## 12. Conclusion

ODS provides the missing infrastructure layer for institutional decision governance. By standardizing decision memory, ODS enables:

- **Trust** through verifiability
- **Learning** through outcome tracking
- **Accountability** through attribution
- **Compliance** through auditability

Organizations implementing ODS gain:
1. Reduced regulatory risk
2. Improved decision quality over time
3. Institutional knowledge preservation
4. Competitive advantage through superior decision intelligence

**The future of enterprise intelligence is verifiable, auditable, and continuously improving.**

**ODS makes that future possible.**

---

## License

This specification is licensed under **Apache License 2.0**.

See [LICENSE](./LICENSE) for full terms.

---

## Contact

**ODS Foundation**  
GitHub: https://github.com/ODS-Foundation  
Issues: https://github.com/ODS-Foundation/ods-specification/issues  
Discussions: https://github.com/ODS-Foundation/ods-specification/discussions

---

**Version:** 1.0  
**Published:** April 2026  
**Next Review:** October 2026

---

*"In a world of synthetic intelligence, verified decision memory is the ultimate moat."*

— ODS Foundation
