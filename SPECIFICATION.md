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
1. **Record Schema** — standardized structure for all record types
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

**Requirement:** Once logged, records MUST NOT be modified or deleted.

**Rationale:** Temporal integrity depends on immutable history. Any system that allows retroactive modification destroys auditability and trust. ODS adopts event sourcing semantics: the store is an append-only log of immutable records. State is reconstructed by reading the graph of related records, not by modifying existing ones. This is the same model used by Kafka (append-only log), EventStore (immutable event streams), and Datomic (database of facts where no fact is ever retracted). New information — such as an outcome or a correction — is expressed by appending a new record that references the original, never by mutating it.

**Implementation:** Append-only data structures, cryptographic hashing, write-once storage.

### 2.2 Verifiability

**Requirement:** Every record MUST be cryptographically verifiable against tampering.

**Rationale:** Audit credibility requires proof that records have not been altered.

**Implementation:** SHA-256 hashing, Merkle trees, blockchain-inspired verification (without requiring distributed consensus).

### 2.3 Attribution

**Requirement:** Every record MUST be attributable to specific actors, models, or processes.

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

**Requirement:** Every decision MUST support outcome logging via linked OUTCOME records.

**Rationale:** Learning requires feedback loops. Decisions without outcome tracking cannot improve over time.

**Implementation:** Autonomous OUTCOME records linked to DECISION records via `parent_id`. See Section 3.3.

---

## 3. Record Model

### 3.1 Event Sourcing Semantics

ODS stores are append-only logs of **records**. A record is the atomic unit of the ODS data model. All records share a common identity envelope and are distinguished by `record_type`. No record is ever modified after it is written.

The current state of a decision is not stored in any single record — it is computed by reading the graph of records related to the original DECISION record. See Section 3.5 for the canonical read protocol.

### 3.2 Record Types

ODS v1.0 defines two record types:

| `record_type` | Purpose |
|---------------|---------|
| `DECISION` | The primary record capturing the decision, its context, rationale, and governance. Created once, never modified. |
| `OUTCOME` | A record capturing a realized outcome linked to a DECISION. Created after the outcome is known. |

The following types are reserved for future minor versions and MUST NOT be used in v1.0 implementations:

| `record_type` | Planned Purpose |
|---------------|-----------------|
| `CORRECTION` | Corrects a prior OUTCOME record without modifying it |
| `ANNOTATION` | Adds context to any prior record without affecting metrics |

### 3.3 Common Identity Envelope

Every record, regardless of type, shares this identity structure:

```json
{
  "_schema_version": "1.0",
  "record_type": "DECISION | OUTCOME",
  "record_id": "UUID v4",
  "timestamp_utc": "ISO 8601 UTC",
  "parent_id": "UUID v4 | absent"
}
```

**`record_id`** (required, all types)
- Type: UUID v4
- Purpose: Globally unique identifier for this record
- Constraints: Must be globally unique across all records in the store

**`record_type`** (required, all types)
- Type: Enum: `DECISION`, `OUTCOME`
- Purpose: Discriminator that determines which fields are valid and required

**`timestamp_utc`** (required, all types)
- Type: ISO 8601 datetime with UTC timezone
- Constraints: Must be UTC, microsecond precision
- Example: `"2026-04-28T14:23:45.123456+00:00"`

**`parent_id`** (absent for DECISION; required for OUTCOME)
- Type: UUID v4
- Purpose: Reference to the record this record depends on
- Constraints: MUST reference a `record_id` that exists in the store at write time. A write MUST be rejected with an error if the referenced `parent_id` does not exist.

### 3.4 Schema by Record Type

#### 3.4.1 DECISION Record

A DECISION record captures the full context of a decision at the moment it is made. It is written once and never modified.

```json
{
  "_schema_version": "1.0",
  "record_type": "DECISION",
  "record_id": "UUID v4",
  "timestamp_utc": "ISO 8601 UTC",

  "identity": {
    "model_version": "semver string",
    "policy_hash": "SHA-256 hex"
  },

  "context": {
    "regime_state": "enum",
    "regime_confidence": "float [0,1]",
    "volatility_state": "enum",
    "macro_state_vector": []
  },

  "action": {
    "action_type": "string",
    "action_size": "float",
    "risk_posture": "float [0,1]",
    "expected_value": "float"
  },

  "cognition": {
    "confidence": "float [0,1]",
    "uncertainty_score": "float [0,1]",
    "decision_latency_ms": "integer",
    "rationale": "string"
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

A DECISION record MUST NOT contain an `outcomes` field. Outcomes are expressed exclusively through linked OUTCOME records.

#### 3.4.2 OUTCOME Record

An OUTCOME record captures a realized outcome for a DECISION. It is a first-class record in the store, linked via `parent_id` to the DECISION it describes.

```json
{
  "_schema_version": "1.0",
  "record_type": "OUTCOME",
  "record_id": "UUID v4",
  "timestamp_utc": "ISO 8601 UTC",
  "parent_id": "UUID v4",

  "outcome_status": "PARTIAL | FINAL",

  "outcomes": {
    "actual_result": "float",
    "realized_at": "ISO 8601 UTC",
    "delta_from_expected": "float",
    "outcome_quality": "float [0,1]"
  },

  "governance": {
    "audit_trail": [],
    "compliance": {}
  }
}
```

**`outcome_status`** (required)
- `PARTIAL` — an intermediate measurement. Multiple PARTIAL records may exist for the same DECISION.
- `FINAL` — closes the outcome cycle for the DECISION. Only one FINAL is permitted per DECISION chain. A write MUST be rejected if a FINAL already exists for the target `parent_id`.

**Invariant — one FINAL per chain:** A store MUST reject any attempt to write a second OUTCOME record with `outcome_status: FINAL` for the same `parent_id`. This invariant is evaluated at write time.

### 3.5 Canonical Read Protocol

Because a decision's complete state spans multiple records, implementations MUST use the following algorithm to compute the canonical reading of any DECISION:

```
function canonical_state(decision_record_id):

  1. Load the DECISION record with record_id = decision_record_id.
     If not found, return NOT_FOUND.

  2. Load all records where parent_id = decision_record_id.
     These are the direct children of the DECISION.

  3. For each child record:
     - If record_type = OUTCOME: this is a candidate outcome for this DECISION.
     - Classify by outcome_status (PARTIAL or FINAL).

  4. Return:
     - decision: the DECISION record (immutable, always canonical)
     - outcomes_partial: list of PARTIAL OUTCOME records, ordered by timestamp_utc
     - outcome_final: the single FINAL OUTCOME record, or null if none exists
```

**Determinism requirement:** Two conformant implementations reading the same store MUST produce identical canonical state for the same `decision_record_id`. This protocol is the normative definition of "current state" for audit and verification purposes.

**Note on future CORRECTION records (v1.x):** When CORRECTION is introduced in a future minor version, the read protocol will extend to follow correction chains recursively. The terminal record in a correction chain — the one that is not itself corrected by any other record — is the canonical reading for that chain. CORRECTION on a FINAL OUTCOME becomes the new canonical FINAL; the invariant "one FINAL per chain" is evaluated against the terminal record, not against all records historically bearing `outcome_status: FINAL`. The read protocol for v1.0 is complete as specified above; implementations do not need to handle CORRECTION chains.

---

## 4. Field Specifications

### 4.1 DECISION Fields

#### 4.1.1 Identity Sub-object

**`model_version`** (required)
- Type: Semantic version string
- Purpose: Track which decision model or process was used
- Constraints: Must follow semver (e.g., `v2.1.3`)
- Example: `"v2.1.0"`

**`policy_hash`** (required)
- Type: SHA-256 hash
- Purpose: Cryptographic fingerprint of the decision policy document in effect at decision time
- Constraints: 64-character lowercase hexadecimal
- Canonical input: The UTF-8 encoded canonical JSON representation of the policy object as defined in **RFC 8785** (JSON Canonicalization Scheme, JCS). Implementations MUST use a JCS-conformant canonicalization library. The hash is `SHA-256(JCS(policy_object))`.
- Concrete example: policy object `{"version":"3","name":"credit_policy"}` canonicalizes under JCS to `{"name":"credit_policy","version":"3"}` (UTF-8, keys sorted, no whitespace) and produces SHA-256 `189bff6265300365c5ff0d775393db04714f1476ef063bc99a215c9e46a16971`
- Note: key ordering in the source object is irrelevant; JCS sorting is deterministic across all conformant implementations regardless of programming language

#### 4.1.2 Context Layer

**`regime_state`** (required for Standard and Full conformance)
- Type: Enum
- Purpose: Detected environmental regime at decision time
- Values: `NORMAL`, `TRANSITION`, `CRISIS`, `RECOVERY`

**`regime_confidence`** (required for Standard and Full conformance)
- Type: Float [0.0, 1.0]
- Purpose: Confidence in regime classification

**`volatility_state`** (optional)
- Type: Enum
- Values: `LOW`, `NORMAL`, `ELEVATED`, `EXTREME`

**`macro_state_vector`** (optional)
- Type: Array of floats
- Purpose: Domain-specific normalized state indicators at decision time

#### 4.1.3 Action Layer

**`action_type`** (required)
- Type: String
- Purpose: Domain-specific category of action taken
- Note: ODS does not constrain the vocabulary. Implementations define their own action type enumerations appropriate to their domain.

**`action_size`** (optional)
- Type: Float
- Purpose: Magnitude of action in domain-specific units

**`risk_posture`** (optional)
- Type: Float [0.0, 1.0]
- Purpose: Risk appetite at decision time; 0.0 = minimum risk, 1.0 = maximum risk

**`expected_value`** (optional)
- Type: Float
- Purpose: Expected outcome of the decision in domain-specific units

#### 4.1.4 Cognition Layer

**`confidence`** (required)
- Type: Float [0.0, 1.0]
- Purpose: Decision maker's confidence in the chosen action

**`uncertainty_score`** (optional)
- Type: Float [0.0, 1.0]
- Purpose: Quantified epistemic uncertainty; conventionally `1 - confidence`

**`decision_latency_ms`** (optional)
- Type: Integer
- Purpose: Time elapsed between receiving inputs and committing the decision, in milliseconds

**`rationale`** (required)
- Type: String [10, 2000] characters
- Purpose: Human- or machine-readable explanation of why this action was chosen

#### 4.1.5 Counterfactuals Layer

Each counterfactual entry represents an alternative action considered and not taken.

**`alternative_action`** (required per entry)
- Type: String
- Purpose: Description of the alternative action

**`expected_outcome`** (required per entry)
- Type: Float
- Purpose: Estimated outcome had the alternative been taken

**`regret`** (optional, computed)
- Type: Float
- Formula: `alternative_expected_outcome - actual_result` (requires a linked FINAL OUTCOME record)

#### 4.1.6 Governance Layer

**`audit_trail`** (required)
- Type: Array of events
- Schema per entry: `{ timestamp_utc, event, actor, metadata }`
- Valid events for DECISION records: `DECISION_CREATED`, `VERIFIED`, `AUDITED`

**`explainability`** (optional)
- Type: Object
- Purpose: Additional interpretability context (feature importances, SHAP values, decision factors)

**`compliance`** (optional for Basic; required for Standard and Full)
- Type: Object
- Fields: `risk_limit_checks` (array of strings), `policy_violations` (array of strings), `approvals` (array of strings)

### 4.2 OUTCOME Fields

**`outcome_status`** (required)
- Type: Enum: `PARTIAL`, `FINAL`
- See Section 3.4.2 for semantics.

**`actual_result`** (required)
- Type: Float
- Purpose: Realized outcome in domain-specific units

**`realized_at`** (required)
- Type: ISO 8601 datetime UTC
- Purpose: When the outcome was measured or became known

**`delta_from_expected`** (required)
- Type: Float
- Formula: `actual_result - expected_value` where `expected_value` is taken from the parent DECISION record's `action.expected_value`
- Purpose: Quantifies deviation between prediction and realization

**`outcome_quality`** (optional)
- Type: Float [0.0, 1.0]
- Purpose: Domain-specific composite quality score for the outcome

**`audit_trail`** (required)
- Valid events for OUTCOME records: `OUTCOME_LOGGED`, `VERIFIED`, `AUDITED`

---

## 5. Conformance Levels

ODS defines three implementation tiers. See [CONFORMANCE.md](./CONFORMANCE.md) for full requirements.

### 5.1 Basic

**Requirements:**
- All records use the unified schema with `record_type` discriminator
- DECISION records logged with identity, action, and cognition layers
- Append-only storage; no record modified after write
- `parent_id` referential integrity enforced at write time
- Audit trail per record
- Minimum 1-year retention

### 5.2 Standard

**Requirements:**
- All Basic requirements
- Context layer captured on DECISION records
- OUTCOME records logged when outcomes are realized
- Canonical read protocol (Section 3.5) implemented and exposed via API
- Cryptographic verification (SHA-256 per record)
- Minimum 7-year retention
- Third-party audit access supported

### 5.3 Full

**Requirements:**
- All Standard requirements
- Counterfactuals captured on DECISION records
- Decision quality metrics computed (DPI, CFR, Learning Velocity) — formal definitions in Section 6
- Real-time governance and compliance signaling
- Permanent retention

---

## 6. Decision Quality Metrics (Level 3)

These metrics are required for Full conformance. They are computed from the graph of DECISION and OUTCOME records. Two conformant implementations MUST produce identical metric values for the same record graph.

> **Provisional weights notice:** The component weights in §6.1 are provisional and lack empirical justification. They MUST be used as specified for v1.0 conformance comparability, but are subject to revision via RFC before v1.2. Implementations claiming Full conformance are claiming compliance with the spec as written, not with empirically validated metrics.

### 6.1 Decision Performance Index (DPI)

DPI measures the quality of a single decision along five dimensions:

```
DPI = (calibration × 0.30)
    + (attribution  × 0.25)
    + (accuracy     × 0.25)
    + (risk_alignment × 0.15)
    + (latency_score  × 0.05)
```

Where each dimension is a float [0.0, 1.0]:

- **calibration:** alignment between `confidence` and realized accuracy over a rolling window
- **attribution:** whether the decision actor and policy were correctly identified
- **accuracy:** `1 - |delta_from_expected| / |expected_value|`, clamped to [0, 1]
- **risk_alignment:** alignment between `risk_posture` and the volatility context
- **latency_score:** normalized inverse of `decision_latency_ms` against a domain baseline

### 6.2 Counterfactual Regret (CFR)

CFR is computed after a FINAL OUTCOME record exists:

```
CFR per counterfactual = alternative_expected_outcome - actual_result
```

Aggregate CFR for a decision = mean CFR across all counterfactual entries where `regret > 0`.

### 6.3 Learning Velocity (LV)

LV measures the rate of change in decision quality over time:

```
LV = ΔDPI / ΔTime
```

Computed as the linear regression slope of DPI values ordered by `timestamp_utc` over a configurable rolling window (default: 30 days). Positive LV indicates improving decision quality. Implementations MUST use ordinary least squares regression for comparability.

---

## 7. Implementation Requirements

### 7.1 Storage Requirements

**Immutability:** ODS-compliant systems MUST use append-only storage.

**Acceptable implementations:**
- Append-only files with cryptographic chaining
- Write-once databases (WORM storage)
- Immutable object storage (e.g., AWS S3 Object Lock)

**Prohibited:**
- Any storage mechanism that permits modification of a written record
- Soft-delete patterns that mark records as deleted without physical retention

### 7.2 Referential Integrity

Implementations MUST enforce `parent_id` referential integrity at write time. A record with a `parent_id` that does not reference an existing `record_id` in the store MUST be rejected. The rejection response MUST identify the missing `parent_id`.

### 7.3 FINAL Invariant Enforcement

Implementations MUST enforce the one-FINAL-per-chain invariant at write time. An OUTCOME record with `outcome_status: FINAL` MUST be rejected if any existing OUTCOME record with the same `parent_id` already has `outcome_status: FINAL`.

### 7.4 Cryptographic Requirements

**Hashing:** SHA-256 minimum for per-record fingerprinting.

**Canonical serialization for hashing:** UTF-8 encoded JSON, keys sorted lexicographically, no whitespace. Implementations MUST use this canonical form to ensure hash portability across implementations.

**Verification:** Merkle tree construction is specified in a separate document (pending RFC). For v1.0, per-record SHA-256 hashing is required at Standard conformance; Merkle tree batch verification is required at Full conformance but the exact construction is deferred to v1.1.

### 7.5 Temporal Requirements

**Clock synchronization:** NTP or equivalent, ±100ms accuracy.

**Timezone:** All `timestamp_utc` fields MUST be UTC.

**Precision:** Microsecond minimum.

### 7.6 API Requirements

ODS-compliant systems SHOULD expose:

```
POST /records                       — Write a new record (DECISION or OUTCOME)
GET  /records/{record_id}           — Retrieve a single record
GET  /records/{record_id}/state     — Canonical state per Section 3.5
GET  /records?parent_id={id}        — All records with a given parent_id
GET  /records/{record_id}/verify    — Cryptographic verification
```

---

## 8. Relationship to Existing Standards

### 8.1 ISO 27001

ODS complements ISO 27001 by providing decision-specific audit trails, immutability guarantees, and temporal integrity. ISO 27001 governs information security controls; ODS governs decision memory.

### 8.2 SOC 2

ODS enhances SOC 2 compliance by providing verifiable decision logs and enabling continuous monitoring. SOC 2 defines operational controls; ODS defines decision memory.

### 8.3 GDPR

ODS is compatible with GDPR:
- Right to explanation → explainability layer in DECISION records
- Right to erasure → handle via anonymization of actor identifiers, not deletion of records
- Data minimization → log only decision-relevant data

### 8.4 Basel III / Dodd-Frank

ODS supports financial regulatory compliance via risk decision audit trails, model governance tracking, and stress test documentation.

---

## 9. Reference Implementation

### 9.1 ORPI Decision Vault

The first Full-conformance implementation is **ORPI Decision Vault** by ORPI Systems.

**Source:** Reference implementation available at github.com/orpi-systems/decision-vault

### 9.2 Implementation Guide

See [IMPLEMENTATION.md](./IMPLEMENTATION.md) for step-by-step instructions.

---

## 10. Versioning and Governance

### 10.1 Version Control

ODS follows semantic versioning (MAJOR.MINOR.PATCH):
- **Major** (X.0.0) — breaking schema changes
- **Minor** (1.X.0) — backward-compatible additions
- **Patch** (1.0.X) — clarifications, no semantic change

Current version: **1.0.0**

### 10.2 Governance Process

ODS is maintained by the **ODS Foundation** through an open RFC process.

**Proposal process:**
1. Submit RFC via GitHub issue using the RFC template
2. Community review (minimum 30 days)
3. Technical Committee decision, recorded publicly
4. Implementation in next appropriate release

See [GOVERNANCE.md](./GOVERNANCE.md) for full governance model.

---

## 11. Use Cases

### 11.1 Financial Services

**Application:** Trading decisions, credit approvals, risk management

**ODS benefit:** Regulatory compliance (MiFID II, Dodd-Frank), model governance, backtesting verification, accountability for trading losses.

### 11.2 Healthcare

**Application:** Treatment decisions, resource allocation, clinical trials

**ODS benefit:** Patient safety, clinical decision support, research reproducibility, malpractice defense.

### 11.3 Supply Chain

**Application:** Sourcing decisions, inventory management, logistics

**ODS benefit:** Disruption analysis, supplier accountability, demand forecasting improvement.

### 11.4 Government

**Application:** Policy decisions, budget allocation, infrastructure

**ODS benefit:** Public accountability, evidence-based policymaking, institutional memory preservation.

---

## 12. Future Directions

### 12.1 Planned (v1.1)

- CORRECTION record type — corrects a prior OUTCOME without modifying it
- ANNOTATION record type — adds context without affecting metrics
- Multi-party decision schema (committee and board decisions)
- Privacy-preserving decision logging
- Formal Merkle tree construction specification

### 12.2 Research Areas

- Causal inference integration
- Cross-organizational decision benchmarking
- AI explainability standards alignment

---

## License

This specification is licensed under **Apache License 2.0**. See [LICENSE](./LICENSE) for full terms.

---

## Contact

**ODS Foundation**
GitHub: https://github.com/ODS-Foundation/ods-specification
Issues: https://github.com/ODS-Foundation/ods-specification/issues

---

**Version:** 1.0.0
**Published:** April 2026
**Next Review:** October 2026
