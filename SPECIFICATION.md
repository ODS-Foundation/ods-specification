# Operational Decision Standard (ODS) v2.0

**Status:** PUBLISHED
**Version:** 2.0.0
**Date:** May 2026
**License:** Apache 2.0
**Maintainer:** ODS Foundation

---

## Abstract

The Operational Decision Standard (ODS) defines a unified schema and methodology for institutional decision memory systems. ODS establishes requirements for logging, verifying, and governing organizational decisions in a manner that ensures immutability, auditability, and temporal integrity.

ODS v2.0 introduces a two-layer architecture: a minimal, domain-agnostic **core protocol** that is universal across all decision-logging contexts, and independently-versioned **domain profiles** that extend the core with domain-specific fields. The core defines the invariants; profiles define the vocabulary.

This standard addresses a critical gap in enterprise infrastructure: the absence of verifiable, auditable decision trails. ODS provides the missing infrastructure layer.

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
1. **Core Protocol** — a domain-agnostic record schema and governance model
2. **Domain Profiles** — independently-versioned extensions for specific industries
3. **Governance Requirements** — audit trails, compliance, explainability
4. **Temporal Integrity** — immutable logging with cryptographic verification
5. **Meta-Learning Framework** — systematic improvement mechanisms
6. **Conformance Levels** — tiered implementation pathways, independent for core and profile

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

The v2.0 architecture separates protocol from vocabulary. The core protocol defines what is universal: the record model, immutability guarantees, cryptographic verification, and governance infrastructure. Domain profiles define what is domain-specific: the fields that characterize decisions in a given industry. This separation means the core specification is stable across domains, and domain extensions do not require core changes.

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

**Requirement:** Every decision MUST capture complete temporal context — state of the world at decision time.

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

ODS defines three active record types:

| `record_type` | Added | Purpose |
|---------------|-------|---------|
| `DECISION` | v2.0.0 | The primary record capturing the decision, its context, rationale, and governance. Created once, never modified. |
| `OUTCOME` | v2.0.0 | A record capturing a realized outcome linked to a DECISION. Created after the outcome is known. |
| `CHECKPOINT` | v2.1.0 | Cryptographic infrastructure record that attests to the Merkle root of a specific prefix of the store's Merkle log. See §7.7. |

`CHECKPOINT` is an infrastructure primitive, not a domain-semantic record type. It does not affect DPI/CFR metric computation. See §7.7 for the full specification.

The following types are reserved for future minor versions and MUST NOT be used in v2.x implementations:

| `record_type` | Planned Purpose |
|---------------|-----------------|
| `CORRECTION` | Corrects a prior OUTCOME record without modifying it |
| `ANNOTATION` | Adds context to any prior record without affecting metrics |

### 3.3 Common Identity Envelope

Every record, regardless of type, shares this identity structure:

```json
{
  "_schema_version": "2.0.0",
  "record_type": "DECISION | OUTCOME",
  "record_id": "UUID v4",
  "timestamp_utc": "ISO 8601 UTC",
  "parent_id": "UUID v4 | absent",
  "profile": "namespace/vN | absent"
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
- Example: `"2026-05-09T14:23:45.123456+00:00"`

**`parent_id`** (absent for DECISION; required for OUTCOME)
- Type: UUID v4
- Purpose: Reference to the record this record depends on
- Constraints: MUST reference a `record_id` that exists in the store at write time. A write MUST be rejected with an error if the referenced `parent_id` does not exist.

**`profile`** (conditionally required — see Section 4.1.2 and §E4 rule)
- Type: String — format `"namespace/vN"` (e.g., `"ODS-Finance/v1"`)
- Purpose: Identifies the domain profile governing domain-specific fields in this record
- For DECISION records: REQUIRED when the record contains an `action` section; MAY be absent on governance-only records (no `action`)
- For OUTCOME records: OPTIONAL; if present, MUST match the profile of the parent DECISION

**`sequence_number`** (store-assigned; present in v2.1.0+ stored representations from Standard-and-above stores)
- Type: Positive integer, beginning at 1 per Merkle log
- Assigned exclusively by the store at write time; absent from client-submitted payloads
- Clients MUST NOT include `sequence_number` in submitted records; the store MUST reject records that include it
- Monotonically increasing and gapless within a Merkle log; used as the canonical leaf-ordering key (§7.7)
- Absent on records written before the store was upgraded to v2.1.0 (those records are Merkle-ineligible)

**`context`** (DECISION records — RECOMMENDED)
- Type: Object
- The core imposes no required structure on `context`. It is an extensible container. Profiles MAY define required context fields. See Section 4.1.3.

### 3.4 Schema by Record Type

#### 3.4.1 DECISION Record

A DECISION record captures the full context of a decision at the moment it is made. It is written once and never modified.

```json
{
  "_schema_version": "2.0.0",
  "record_type": "DECISION",
  "record_id": "UUID v4",
  "timestamp_utc": "ISO 8601 UTC",
  "profile": "ODS-Finance/v1",

  "identity": {
    "model_version": "semver string",
    "policy_hash": "SHA-256 hex"
  },

  "context": {},

  "action": {
    "action_type": "string",
    "action_size": "float",
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
    "compliance": {
      "policy_violations": [],
      "approvals": []
    }
  }
}
```

**E4 rule:** If a DECISION record contains an `action` section, the `profile` field is REQUIRED. A DECISION record MAY omit `profile` only when it contains no `action` section (governance-only records: audit events, policy attestations, meta-records).

A DECISION record MUST NOT contain an `outcomes` field. Outcomes are expressed exclusively through linked OUTCOME records.

#### 3.4.2 OUTCOME Record

An OUTCOME record captures a realized outcome for a DECISION. It is a first-class record in the store, linked via `parent_id` to the DECISION it describes.

```json
{
  "_schema_version": "2.0.0",
  "record_type": "OUTCOME",
  "record_id": "UUID v4",
  "timestamp_utc": "ISO 8601 UTC",
  "parent_id": "UUID v4",
  "profile": "ODS-Finance/v1",

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

**`profile`** on OUTCOME records (optional)
- If present, MUST match the `profile` field of the parent DECISION record.
- If absent, the profile association is resolved via the parent DECISION through `parent_id`.
- Validators with `--store` enforce consistency. Validators without `--store` validate only core fields and emit a warning about unvalidated profile-specific fields.

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

**Note on future CORRECTION records (v2.x):** When CORRECTION is introduced in a future minor version, the read protocol will extend to follow correction chains recursively. The terminal record in a correction chain — the one that is not itself corrected by any other record — is the canonical reading for that chain. CORRECTION on a FINAL OUTCOME becomes the new canonical FINAL; the invariant "one FINAL per chain" is evaluated against the terminal record. The read protocol for v2.0 is complete as specified above.

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

#### 4.1.2 Profile Field

**`profile`** (conditionally required on DECISION; optional on OUTCOME)
- Type: String
- Format: `"<namespace>/v<major>"` — e.g., `"ODS-Finance/v1"`, `"ODS-Healthcare/v2"`
- The namespace must correspond to an entry in [PROFILES.md](./PROFILES.md) with status `authored` or higher
- The major version is the profile's major version number at write time. The precise minor/patch version is resolved via PROFILES.md registry by cross-referencing the record's `timestamp_utc`

**E4 rule:**

| Record type | Condition | `profile` field |
|-------------|-----------|-----------------|
| DECISION | Contains `action` section | REQUIRED |
| DECISION | No `action` section (governance-only) | MAY be absent |
| OUTCOME | Any | OPTIONAL; if present, MUST match parent DECISION's `profile` |

**OQ3 rule:** A `profile` field referencing a namespace with status `reserved` in PROFILES.md is a conformance violation. Validators MUST emit an error, not a warning.

#### 4.1.3 Context Layer

`context` is a RECOMMENDED (`SHOULD`) extensible container. The core specification imposes no required properties on `context` and no constraint on its contents. Implementations MAY omit `context` entirely without violating core conformance.

Profiles MAY define required context fields within the profile schema extension. A profile MAY also define top-level context fields with documented RFC justification.

**Core schema behavior:** The core schema accepts any object as `context`. Profiles enforce structure on `context` in the second validation pass.

#### 4.1.4 Action Layer

The action layer captures what was decided. The following fields are defined at the core level:

| Field | Core v2.0 | Type | Notes |
|-------|-----------|------|-------|
| `action_type` | core | String | Required when action is present. Domain-specific category. ODS does not constrain the vocabulary. |
| `action_size` | core | Float | Magnitude of action in domain-specific units. Units are domain-defined. |
| `expected_value` | core | Float | Expected outcome of the decision in domain-specific units. |
| `risk_posture` | ODS-Finance/v1 | Float [0,1] | Risk appetite at decision time. The [0,1] formalization is a finance idiom. |
| `capital_at_risk_bps` | ODS-Finance/v1 | Float | Capital at risk expressed in basis points. Purely financial. |

The principle: *structure is universal; vocabulary is profile-specific.* `action_type` and `action_size` remain core fields because every domain has an action category and magnitude, even though the vocabulary and units differ. `risk_posture` and `capital_at_risk_bps` are ODS-Finance/v1 fields because their conceptual framing is finance-specific.

Profiles MAY enumerate valid `action_type` values or specify `action_size` units without moving these fields out of the core schema.

**`action_type`** (required when `action` section is present)
- Type: String
- Purpose: Domain-specific category of action taken
- Note: ODS does not constrain the vocabulary. Implementations and profiles define their own action type enumerations.

**`action_size`** (optional)
- Type: Float
- Purpose: Magnitude of action in domain-specific units

**`expected_value`** (optional)
- Type: Float
- Purpose: Expected outcome of the decision in domain-specific units

#### 4.1.5 Cognition Layer

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

#### 4.1.6 Counterfactuals Layer

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

#### 4.1.7 Governance Layer

**`audit_trail`** (required)
- Type: Array of events
- Schema per entry: `{ timestamp_utc, event, actor, metadata }`
- Valid events for DECISION records: `DECISION_CREATED`, `VERIFIED`, `AUDITED`

**`explainability`** (optional)
- Type: Object
- Purpose: Additional interpretability context (feature importances, SHAP values, decision factors)

**`compliance`** (optional for Basic; required for Standard and Full)
- Type: Object
- Core fields:
  - `policy_violations` (array of strings) — documents policy breaches. Universal: every domain has a concept of policy adherence.
  - `approvals` (array of strings) — documents authorization grants. Universal: every domain has authorization gates.
- Profile-defined fields (not in core):
  - `risk_limit_checks` — defined in ODS-Finance/v1. Finance-domain pre-decision gate checks.

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

**`profile`** (optional)
- See Section 3.3 and 3.4.2 for the full specification of OUTCOME profile behavior.

---

## 5. Conformance Levels

ODS v2.0 defines conformance independently for core and profile. See [CONFORMANCE.md](./CONFORMANCE.md) for full requirements.

Conformance is declared as a two-axis statement:

> "ODS Core v2 Standard + ODS-Finance v1 Full"

A core-only conformance declaration is valid for governance-only implementations:

> "ODS Core v2 Basic"

### 5.1 Core — Basic

**Requirements:**
- All records use the unified schema with `record_type` discriminator and `_schema_version: "2.0.0"`
- DECISION records include identity, cognition, and governance layers
- DECISION records MUST NOT contain an `outcomes` field
- Append-only storage; no record modified after write
- `parent_id` referential integrity enforced at write time
- Audit trail per record
- Minimum 1-year retention

### 5.2 Core — Standard

**Requirements:**
- All Basic requirements
- Canonical read protocol (Section 3.5) implemented and exposed via API
- OUTCOME records logged when outcomes are realized; outcomes are never written by modifying an existing DECISION record
- FINAL uniqueness invariant enforced at write time
- Cryptographic verification (SHA-256 per record)
- Minimum 7-year retention
- Third-party audit access supported

### 5.3 Core — Full

**Requirements:**
- All Standard requirements
- Counterfactuals captured on DECISION records
- Decision quality metrics computed (DPI, CFR, Learning Velocity) — formal definitions in Section 6
- Real-time governance and compliance signaling
- Permanent retention

---

## 6. Decision Quality Metrics (Full Conformance)

These metrics are required for Full conformance (core or profile). They are computed from the graph of DECISION and OUTCOME records. Two conformant implementations MUST produce identical metric values for the same record graph.

> **Provisional weights notice:** The component weights in §6.1 are provisional and lack empirical justification. They MUST be used as specified for v2.0 conformance comparability, but are subject to revision via RFC before v2.1. Implementations claiming Full conformance are claiming compliance with the spec as written, not with empirically validated metrics.

### 6.1 Decision Performance Index (DPI)

DPI measures the quality of a single decision along five dimensions:

```
DPI = (calibration    × 0.30)
    + (attribution    × 0.25)
    + (accuracy       × 0.25)
    + (risk_alignment × 0.15)
    + (latency_score  × 0.05)
```

Where each dimension is a float [0.0, 1.0]:

- **calibration:** alignment between `confidence` and realized accuracy over a rolling window
- **attribution:** whether the decision actor and policy were correctly identified
- **accuracy:** `1 - |delta_from_expected| / |expected_value|`, clamped to [0, 1]
- **risk_alignment:** alignment between `risk_posture` and the volatility context
- **latency_score:** normalized inverse of `decision_latency_ms` against a domain baseline

> **Note on `risk_alignment`:** This dimension requires `risk_posture` (action layer) and `volatility_state` (context layer), both of which are defined in ODS-Finance/v1. Implementations using core only — without ODS-Finance/v1 — SHOULD compute DPI without the `risk_alignment` dimension, redistributing its weight (0.15) proportionally among the remaining dimensions, such that total weight remains 1.0.

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

**Canonical serialization for hashing:** RFC 8785 (JSON Canonicalization Scheme, JCS). Implementations MUST use a JCS-conformant library. JCS is portable across all programming languages; Python-flavor `json.dumps(sort_keys=True)` is NOT conformant.

**Verification:** Per-record SHA-256 hashing is required at all conformance levels (Basic and above). Merkle tree batch verification is required at Standard conformance and above; the normative construction is specified in §7.7 (introduced in v2.1.0).

### 7.5 Temporal Requirements

**Clock synchronization:** NTP or equivalent, ±100ms accuracy.

**Timezone:** All `timestamp_utc` fields MUST be UTC.

**Precision:** Microsecond minimum.

### 7.6 API Requirements

ODS-compliant systems SHOULD expose:

```
POST /records                                                    — Write a new record (DECISION, OUTCOME, or CHECKPOINT)
GET  /records/{record_id}                                        — Retrieve a single record
GET  /records/{record_id}/state                                  — Canonical state per Section 3.5
GET  /records?parent_id={id}                                     — All records with a given parent_id
GET  /records/{record_id}/verify                                 — Per-record SHA-256 verification
GET  /records/{record_id}/proof?checkpoint={checkpoint_id}       — Merkle inclusion proof (v2.1.0+, Standard)
GET  /checkpoints/{checkpoint_id}/consistency?from={old_id}      — Consistency proof between checkpoints (v2.1.0+, Full)
```

### 7.7 Merkle Tree Construction (v2.1.0)

**Normative references:** RFC 6962 §2.1 (Merkle Hash Trees), §2.1.1 (Merkle Audit Proofs), §2.1.2 (Merkle Consistency Proofs), §3.5 (Signed Tree Head). RFC 8785 (JCS) for leaf pre-image serialization.

ODS adopts the RFC 6962 (Certificate Transparency) Merkle Hash Tree construction as the normative basis for batch verification. ODS does not invent cryptographic constructions; it adopts battle-tested IETF-specified ones — the same philosophy that drove adoption of RFC 8785 for canonical serialization.

#### 7.7.1 Leaf Hash Construction

Each Merkle-eligible record (any record with a store-assigned `sequence_number`) maps to exactly one leaf:

```
leaf_hash = SHA-256(0x00 || UTF-8(JCS(stored_record)))
```

- `0x00` — single-byte domain separation prefix per RFC 6962 §2.1 (prevents second-preimage attacks: a leaf hash cannot be mistaken for an internal node hash)
- `JCS(stored_record)` — RFC 8785 canonical JSON serialization of the complete stored record as returned by `GET /records/{id}`, including the store-assigned `sequence_number` field
- The leaf hash commits to every field of the record, including `sequence_number`, binding each record to its position in the log

#### 7.7.2 Internal Node Construction

For any two child hashes `left` and `right` (each 32 bytes):

```
node_hash = SHA-256(0x01 || left || right)
```

- `0x01` — single-byte domain separation prefix per RFC 6962 §2.1
- Pre-image length: 65 bytes (1 + 32 + 32)

This is identical to the Certificate Transparency log hash function.

#### 7.7.3 Canonical Ordering

**Canonical ordering is by `sequence_number` ascending.**

`sequence_number` is store-assigned and monotonically increasing, making the Merkle log append-only by construction. This is the required property for RFC 6962 §2.1.2 consistency proofs to be mathematically valid. Client-supplied `timestamp_utc` MUST NOT be used as the ordering key: it is not monotonic at the log level (clock skew and bulk imports allow backdated records), which would break the prefix-extension property that consistency proofs depend on.

#### 7.7.4 Edge Cases

Per RFC 6962 §2.1 recursive definition:

**Empty tree:**
```
MTH({}) = SHA-256(b"")
```

**Single record:**
```
MTH({d[0]}) = SHA-256(0x00 || UTF-8(JCS(stored_record_0)))
```
Root equals the single leaf hash; no internal node.

**Odd or general `n` — RFC 6962 power-of-two split rule:**

For `n` records `D[0..n-1]`:
1. `k = 2^⌊log₂(n-1)⌋` — the largest power of 2 strictly less than `n`
2. Left subtree: `D[0..k-1]` (k records); right subtree: `D[k..n-1]` (n−k records)
3. `MTH(D[0..n-1]) = SHA-256(0x01 || MTH(D[0..k-1]) || MTH(D[k..n-1]))`

| n | k | Left | Right |
|---|---|------|-------|
| 3 | 2 | 2    | 1     |
| 5 | 4 | 4    | 1     |
| 6 | 4 | 4    | 2     |
| 7 | 4 | 4    | 3     |
| 9 | 8 | 8    | 1     |

RFC 6962 does NOT pad with zero hashes. Any implementation that pads will produce a different root.

#### 7.7.5 CHECKPOINT Record

A `CHECKPOINT` record attests to the Merkle root of a specific prefix of the store's Merkle log. It is stored as an ordinary ODS record (immutable, append-only) and receives its own `sequence_number`. It is NOT included in the tree it describes; it IS included as a leaf in subsequent trees.

**Schema:**

```json
{
  "_schema_version": "2.1.0",
  "record_type": "CHECKPOINT",
  "record_id": "<uuid-v4>",
  "sequence_number": 43,
  "timestamp_utc": "<iso-8601-microseconds>",
  "identity": {
    "model_version": "<string>",
    "policy_hash": "<sha256-hex>"
  },
  "checkpoint": {
    "tree_size": 42,
    "tree_root": "<sha256-hex-64-chars>",
    "covers_through_sequence_number": 42,
    "ordering": "sequence_number ASC"
  }
}
```

- `checkpoint.tree_size` — number of records included as leaves
- `checkpoint.tree_root` — 64-char lowercase hex SHA-256 Merkle root
- `checkpoint.covers_through_sequence_number` — `sequence_number` of the last included record; equals `tree_size` when the log is gapless from sequence_number 1
- `checkpoint.ordering` — literal string `"sequence_number ASC"` for v2.1.0

**Security limitation:** Unsigned CHECKPOINTs provide tamper-evidence (any modification to included records changes the root and causes verification to fail) but do NOT provide tamper-proof attribution (without a signature, it cannot be proven who generated a given CHECKPOINT). Signed CHECKPOINTs are deferred to a future RFC as a Full-level requirement.

**Emission cadence:** Standard-conformant implementations MUST emit at least one CHECKPOINT after every 1,000 Merkle-eligible records appended, or after every 24 hours of operation with at least one write, whichever comes first.

#### 7.7.6 Merkle Log Genesis and v2.0 Record Exclusion

When a v2.0 store is upgraded to v2.1.0, pre-existing records (those written before the upgrade) have no `sequence_number` and are excluded from the Merkle log. The Merkle sequence begins at `sequence_number: 1` with the first record written after the upgrade. Pre-existing records remain fully readable and SHA-256-verified (v2.0 Standard requirement) but do not appear as Merkle leaves.

Retroactive assignment of `sequence_number` to v2.0 records is PROHIBITED — it would require modifying their stored representation, violating ODS immutability.

#### 7.7.7 Inclusion Proof Format

An inclusion proof demonstrates that a record is a leaf in a specific CHECKPOINT's tree without reconstructing the full tree (RFC 6962 §2.1.1 audit path):

**Request:** `GET /records/{record_id}/proof?checkpoint={checkpoint_record_id}`

If `checkpoint` is omitted, the most recent CHECKPOINT covering the record is used.

**Response:**
```json
{
  "record_id": "<uuid>",
  "checkpoint_record_id": "<uuid>",
  "leaf_index": 41,
  "tree_size": 42,
  "audit_path": ["<sha256-hex>", "..."]
}
```

- `leaf_index` — zero-based position; equals `stored_record.sequence_number - 1`

**Verification procedure:**
1. Fetch stored record; compute `leaf_hash = SHA-256(0x00 || UTF-8(JCS(stored_record)))`
2. Fetch CHECKPOINT; extract `tree_root`
3. Confirm `leaf_index = stored_record.sequence_number - 1`
4. Walk `audit_path` per RFC 6962 §2.1.1, combining with `SHA-256(0x01 || left || right)`
5. Accept if and only if computed root equals `tree_root`

#### 7.7.8 Consistency Proofs (Full Conformance)

RFC 6962 §2.1.2 consistency proofs prove that a later tree is a prefix extension of an earlier tree (no records were deleted or reordered). Valid under `sequence_number` ordering because the log is append-only by construction.

**Request:** `GET /checkpoints/{new_checkpoint_id}/consistency?from={old_checkpoint_id}`

Required for Full conformance. Recommended for Standard. See CONFORMANCE.md.

---

## 8. Profile Specification

### 8.1 Architecture

A profile is a named, versioned extension of ODS Core. Profiles define domain-specific fields that extend the core record schema. The two-layer architecture separates the stable protocol substrate (core) from the domain-specific vocabulary (profile).

Profiles:
- MUST NOT redefine or override core fields
- MUST declare their dependency on an ODS Core major version
- Are independently versioned with their own SemVer, beginning at v1
- Are registered in [PROFILES.md](./PROFILES.md) with a canonical namespace and status

A profile schema is a supplementary JSON Schema document (`schema/profiles/<namespace>-<version>.json`) validated in a second pass after core validation passes.

### 8.2 One Profile Per Record

A record is associated with at most one profile. Cross-domain decisions
(e.g., a financial trade with hiring implications) are represented at the
application layer through linked records — not through multi-profile records.
Each linked record carries its own profile field, and the relationship between
them is expressed via parent_id chains or application-level metadata, not
within the profile field itself.

### 8.3 Profile Field Format

The `profile` field stores the namespace and major version:

```
"profile": "ODS-Finance/v1"
```

Auditors resolve the precise minor/patch version by cross-referencing the record's `timestamp_utc` against the PROFILES.md registry.

### 8.4 Conformance Claims

Conformance is declared independently for core and profile:

> "ODS Core v2 Standard + ODS-Finance v1 Full"

A profile conformance level may not exceed the core conformance level. Profile conformance levels (Standard, Full) require integrity guarantees from the underlying core — Merkle chain at Standard, full audit cryptography at Full. A profile claim of Full while core is only Basic would mean profile-level audit guarantees rest on infrastructure that does not provide them. The cap ensures conformance claims are honest about their actual integrity foundation.

Conformance claims against reserved profiles (status `reserved` in PROFILES.md) are PROHIBITED. See [PROFILES.md](./PROFILES.md).

### 8.5 Profile Backward Compatibility

Within a profile major version, backward compatibility is governed by the rules in [PROFILES.md §Backward Compatibility](./PROFILES.md). The short form: optional additions are permitted; any breaking change requires a major version increment with a migration RFC.

### 8.6 ODS-Finance/v1

ODS-Finance/v1 is the first authored profile. Its content is migrated from ODS Core v1.1.0 fields that are finance-domain-specific. Its schema is at `schema/profiles/ods-finance-v1.json`.

ODS-Finance/v1 defines:

**Context fields:**
- `regime_state`: Enum (`NORMAL`, `TRANSITION`, `CRISIS`, `RECOVERY`) — detected market regime
- `regime_confidence`: Float [0,1] — confidence in regime classification
- `volatility_state`: Enum (`LOW`, `NORMAL`, `ELEVATED`, `EXTREME`) — volatility environment
- `macro_state_vector`: Array of floats — normalized macro indicators at decision time

**Action fields:**
- `action_type`: Enum (`BUY`, `SELL`, `HOLD`, `REDUCE`, `INCREASE`, `ABSTAIN`) — finance action vocabulary
- `risk_posture`: Float [0,1] — risk appetite; 0.0 = minimum risk, 1.0 = maximum risk
- `capital_at_risk_bps`: Float — capital at risk in basis points

**Compliance fields:**
- `risk_limit_checks`: Array of strings — pre-decision gate check results

---

## 9. Relationship to Existing Standards

### 9.1 ISO 27001

ODS complements ISO 27001 by providing decision-specific audit trails, immutability guarantees, and temporal integrity. ISO 27001 governs information security controls; ODS governs decision memory.

### 9.2 SOC 2

ODS enhances SOC 2 compliance by providing verifiable decision logs and enabling continuous monitoring. SOC 2 defines operational controls; ODS defines decision memory.

### 9.3 GDPR

ODS is compatible with GDPR:
- Right to explanation → explainability layer in DECISION records
- Right to erasure → handle via anonymization of actor identifiers, not deletion of records
- Data minimization → log only decision-relevant data

### 9.4 Basel III / Dodd-Frank

ODS supports financial regulatory compliance via risk decision audit trails, model governance tracking, and stress test documentation. ODS-Finance/v1 is specifically designed for finance-regulated environments.

---

## 10. Reference Implementation

### 10.1 ORPI Decision Vault

The first Full-conformance implementation is **ORPI Decision Vault** by ORPI Systems.

**Conformance:** ODS Core v2 Full + ODS-Finance v1 Full

**Source:** Reference implementation available at github.com/orpi-systems/decision-vault

### 10.2 Implementation Guide

See [IMPLEMENTATION.md](./IMPLEMENTATION.md) for step-by-step instructions.

---

## 11. Versioning and Governance

### 11.1 Version Control

ODS follows semantic versioning (MAJOR.MINOR.PATCH):
- **Major** (X.0.0) — breaking schema changes to core or profile
- **Minor** (2.X.0) — backward-compatible additions (new optional core fields, new profiles, new reserved record types)
- **Patch** (2.0.X) — clarifications, no semantic change

Current version: **2.0.0**

### 11.2 Governance Process

ODS is maintained by the **ODS Foundation** through an open RFC process.

**Proposal process:**
1. Submit RFC via GitHub issue using the RFC template
2. Community review (minimum 30 days)
3. Technical Committee decision, recorded publicly
4. Implementation in next appropriate release

See [GOVERNANCE.md](./GOVERNANCE.md) for full governance model.

---

## 12. Use Cases

### 12.1 Financial Services

**Application:** Trading decisions, credit approvals, risk management

**Profile:** ODS-Finance/v1

**ODS benefit:** Regulatory compliance (MiFID II, Dodd-Frank), model governance, backtesting verification, accountability for trading losses. The ODS-Finance/v1 profile provides regime detection, volatility context, and risk limit tracking required for finance-grade auditability.

### 12.2 Healthcare

**Application:** Treatment decisions, resource allocation, clinical trials

**Profile:** ODS-Healthcare (reserved — RFC in progress)

**ODS benefit:** Patient safety, clinical decision support, research reproducibility, malpractice defense.

### 12.3 Supply Chain

**Application:** Sourcing decisions, inventory management, logistics

**Profile:** ODS-Supply-Chain (reserved — RFC in progress)

**ODS benefit:** Disruption analysis, supplier accountability, demand forecasting improvement.

### 12.4 Government

**Application:** Policy decisions, budget allocation, infrastructure

**Profile:** ODS-Government (reserved — RFC in progress)

**ODS benefit:** Public accountability, evidence-based policymaking, institutional memory preservation.

---

## 13. Future Directions

### 13.1 Planned (v2.x)

- CORRECTION record type — corrects a prior OUTCOME without modifying it
- ANNOTATION record type — adds context without affecting metrics
- Multi-party decision schema (committee and board decisions)
- Empirically validated DPI component weights (replaces provisional weights in §6.1)
- Signed CHECKPOINT records (key management, signing procedure, Full-level conformance requirement)

### 13.2 Profile Development

- ODS-Healthcare/v1 — pending RFC
- ODS-Government/v1 — pending RFC
- ODS-Supply-Chain/v1 — pending RFC
- Conformance test suite per profile

### 13.3 Research Areas

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

**Version:** 2.1.0
**Published:** May 2026
**Next Review:** November 2026
