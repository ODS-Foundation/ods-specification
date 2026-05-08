# ODS v1.0 Implementation Guide

**Version:** 1.0
**Audience:** Developers, System Architects
**Prerequisites:** Familiarity with [SPECIFICATION.md](./SPECIFICATION.md)
**Estimated Implementation Time:** 4-12 weeks (depending on conformance level)

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Record Model](#2-record-model)
3. [Architecture Patterns](#3-architecture-patterns)
4. [Basic Conformance](#4-basic-conformance)
5. [Standard Conformance](#5-standard-conformance)
6. [Full Conformance](#6-full-conformance)
7. [Storage Implementation](#7-storage-implementation)
8. [API Design](#8-api-design)
9. [Security Considerations](#9-security-considerations)
10. [Testing and Validation](#10-testing-and-validation)
11. [Deployment Patterns](#11-deployment-patterns)

---

## 1. Getting Started

### 1.1 Determine Your Conformance Level

| Level | When to choose |
|-------|----------------|
| **Basic** | Internal governance, no regulatory requirements, basic accountability |
| **Standard** | Regulated industry (finance, healthcare, energy), external audit, multi-year retention |
| **Full** | Mission-critical systems, continuous improvement, institutional intelligence |

### 1.2 Assessment Checklist

```
□ Executive sponsorship secured
□ Conformance level determined
□ Budget allocated
□ Technical team assigned
□ Existing decision workflows mapped
□ Data retention policies reviewed
□ Storage infrastructure evaluated
□ Security requirements documented
```

---

## 2. Record Model

### 2.1 Core Principle: Append-Only Event Log

ODS stores are append-only logs. No record is ever modified after it is written. This is the same model used by Kafka, EventStore, and Datomic. New information — an outcome, a correction — is expressed by appending a new record that references the original via `parent_id`.

Every record shares the same identity envelope:

```python
{
    "_schema_version": "1.0",
    "record_type": "DECISION",  # or "OUTCOME"
    "record_id": str(uuid4()),
    "timestamp_utc": datetime.utcnow().isoformat() + "+00:00",
    # parent_id: absent for DECISION, required for OUTCOME
}
```

### 2.2 DECISION Records

A DECISION record is written once and never modified. It captures the full context of the decision at the moment it was made.

```python
import json
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import jcs  # RFC 8785 JSON Canonicalization Scheme — pip install jcs


class ODSStore:
    """Minimal ODS-compliant append-only record store."""

    def __init__(self, store_path: str):
        self.path = Path(store_path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.path / "index.jsonl"

    def _record_path(self, record_id: str) -> Path:
        return self.path / f"{record_id}.json"

    def _record_exists(self, record_id: str) -> bool:
        return self._record_path(record_id).exists()

    def _write_record(self, record: dict) -> str:
        record_id = record["record_id"]
        record_path = self._record_path(record_id)

        record_hash = hashlib.sha256(jcs.canonicalize(record)).hexdigest()

        with open(record_path, "w") as f:
            f.write(json.dumps(record, indent=2))

        with open(self.index_file, "a") as f:
            f.write(json.dumps({
                "record_id": record_id,
                "record_type": record["record_type"],
                "timestamp_utc": record["timestamp_utc"],
                "parent_id": record.get("parent_id"),
                "hash": record_hash,
            }) + "\n")

        return record_id

    def write_decision(self, action: dict, cognition: dict, model_version: str,
                       policy: dict, context: dict = None,
                       counterfactuals: list = None, actor: str = "SYSTEM",
                       compliance: dict = None) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()

        policy_hash = hashlib.sha256(jcs.canonicalize(policy)).hexdigest()

        record = {
            "_schema_version": "1.0",
            "record_type": "DECISION",
            "record_id": str(uuid.uuid4()),
            "timestamp_utc": timestamp,
            "identity": {
                "model_version": model_version,
                "policy_hash": policy_hash,
            },
            "action": action,
            "cognition": cognition,
            "governance": {
                "audit_trail": [{
                    "timestamp_utc": timestamp,
                    "event": "DECISION_CREATED",
                    "actor": actor,
                    "metadata": {},
                }],
            },
        }

        if context:
            record["context"] = context
        if counterfactuals:
            record["counterfactuals"] = counterfactuals
        if compliance:
            record["governance"]["compliance"] = compliance

        return self._write_record(record)

    def write_outcome(self, parent_id: str, actual_result: float,
                      realized_at: str, outcome_status: str,
                      actor: str = "OUTCOME_TRACKER",
                      outcome_quality: float = None) -> str:
        """
        Write an OUTCOME record. parent_id must exist in the store.
        outcome_status must be PARTIAL or FINAL.
        Only one FINAL is permitted per parent_id.
        """
        if not self._record_exists(parent_id):
            raise ValueError(
                f"parent_id '{parent_id}' does not exist in the store. "
                "Write rejected."
            )

        if outcome_status == "FINAL":
            existing_finals = self._find_finals(parent_id)
            if existing_finals:
                raise ValueError(
                    f"A FINAL OUTCOME already exists for parent_id '{parent_id}' "
                    f"(record_id: {existing_finals[0]}). "
                    "Only one FINAL is permitted per decision chain. Write rejected."
                )

        if outcome_status not in ("PARTIAL", "FINAL"):
            raise ValueError(f"outcome_status must be PARTIAL or FINAL, got: {outcome_status}")

        parent = self.get_record(parent_id)
        expected_value = parent.get("action", {}).get("expected_value")
        delta = (actual_result - expected_value) if expected_value is not None else None

        timestamp = datetime.now(timezone.utc).isoformat()

        outcomes = {
            "actual_result": actual_result,
            "realized_at": realized_at,
            "delta_from_expected": delta,
        }
        if outcome_quality is not None:
            outcomes["outcome_quality"] = outcome_quality

        record = {
            "_schema_version": "1.0",
            "record_type": "OUTCOME",
            "record_id": str(uuid.uuid4()),
            "timestamp_utc": timestamp,
            "parent_id": parent_id,
            "outcome_status": outcome_status,
            "outcomes": outcomes,
            "governance": {
                "audit_trail": [{
                    "timestamp_utc": timestamp,
                    "event": "OUTCOME_LOGGED",
                    "actor": actor,
                    "metadata": {"outcome_status": outcome_status},
                }],
            },
        }

        return self._write_record(record)

    def get_record(self, record_id: str) -> dict:
        path = self._record_path(record_id)
        if not path.exists():
            raise KeyError(f"Record not found: {record_id}")
        with open(path) as f:
            return json.load(f)

    def canonical_state(self, decision_record_id: str) -> dict:
        """
        Compute the canonical state of a decision per SPECIFICATION.md Section 3.5.

        Returns:
            {
                "decision": <DECISION record>,
                "outcomes_partial": [<OUTCOME records>, ...],  # ordered by timestamp
                "outcome_final": <OUTCOME record> | None,
            }
        """
        decision = self.get_record(decision_record_id)
        if decision.get("record_type") != "DECISION":
            raise ValueError(f"record_id '{decision_record_id}' is not a DECISION record")

        children = self._find_children(decision_record_id)
        outcome_records = [r for r in children if r.get("record_type") == "OUTCOME"]
        outcome_records.sort(key=lambda r: r["timestamp_utc"])

        partials = [r for r in outcome_records if r.get("outcome_status") == "PARTIAL"]
        finals = [r for r in outcome_records if r.get("outcome_status") == "FINAL"]

        return {
            "decision": decision,
            "outcomes_partial": partials,
            "outcome_final": finals[0] if finals else None,
        }

    def _find_children(self, parent_id: str) -> list[dict]:
        children = []
        if not self.index_file.exists():
            return children
        with open(self.index_file) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("parent_id") == parent_id:
                    try:
                        children.append(self.get_record(entry["record_id"]))
                    except KeyError:
                        pass
        return children

    def _find_finals(self, parent_id: str) -> list[str]:
        finals = []
        if not self.index_file.exists():
            return finals
        with open(self.index_file) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("parent_id") == parent_id:
                    record = self.get_record(entry["record_id"])
                    if record.get("outcome_status") == "FINAL":
                        finals.append(entry["record_id"])
        return finals

    def verify_integrity(self) -> tuple[bool, str]:
        """Verify SHA-256 hash of every record against the index."""
        if not self.index_file.exists():
            return True, "Store is empty"
        with open(self.index_file) as f:
            for line in f:
                entry = json.loads(line.strip())
                record = self.get_record(entry["record_id"])
                current_hash = hashlib.sha256(jcs.canonicalize(record)).hexdigest()
                if current_hash != entry["hash"]:
                    return False, f"Integrity failure: {entry['record_id']}"
        return True, "All records verified"
```

### 2.3 Usage Example

```python
store = ODSStore("./decision_vault")

# Write a DECISION record
decision_id = store.write_decision(
    model_version="v2.1.0",
    policy={"name": "credit_policy", "version": "3"},
    actor="CREDIT_ENGINE",
    action={"action_type": "APPROVE", "expected_value": 0.15},
    cognition={"confidence": 0.85, "rationale": "All criteria met within risk tolerance"},
    compliance={"risk_limit_checks": ["PASSED"], "policy_violations": [], "approvals": []},
)
print(f"Decision logged: {decision_id}")

# Later: write a PARTIAL outcome (interim measurement)
outcome_id = store.write_outcome(
    parent_id=decision_id,
    actual_result=0.07,
    realized_at="2026-05-14T09:00:00+00:00",
    outcome_status="PARTIAL",
    outcome_quality=0.6,
)

# Later: write the FINAL outcome
final_id = store.write_outcome(
    parent_id=decision_id,
    actual_result=0.14,
    realized_at="2026-06-01T09:00:00+00:00",
    outcome_status="FINAL",
    outcome_quality=0.88,
)

# Canonical state per Section 3.5
state = store.canonical_state(decision_id)
print("Decision:", state["decision"]["record_id"])
print("Partials:", len(state["outcomes_partial"]))
print("Final:", state["outcome_final"]["outcomes"]["actual_result"])

# Integrity check
ok, msg = store.verify_integrity()
print(f"Integrity: {msg}")
```

---

## 3. Architecture Patterns

### 3.1 Centralized Store

Single append-only store for all records. Suitable for Basic and Standard conformance, organizations under 10,000 decisions/day.

```
┌─────────────────────────────────────────┐
│         ODS Store                        │
│  ┌─────────────────────────────────┐    │
│  │   Append-Only Records            │    │
│  │   - DECISION records            │    │
│  │   - OUTCOME records             │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Index + Verification          │    │
│  │   - SHA-256 per record          │    │
│  │   - parent_id index             │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 3.2 Distributed Store

Multiple stores synchronized. Suitable for Full conformance, global deployments, >50,000 decisions/day. Higher operational complexity; consistency guarantees must be specified per deployment.

---

## 4. Basic Conformance

**Requirements:** DECISION records with identity, action, cognition; append-only; audit trail; 1-year retention.

### 4.1 Storage Setup

**Local filesystem (development):**
```bash
mkdir -p /var/lib/decision_vault
chmod 700 /var/lib/decision_vault
```

**AWS S3 with Object Lock (production):**
```python
import boto3

s3 = boto3.client('s3')
s3.put_bucket_versioning(
    Bucket='org-decision-vault',
    VersioningConfiguration={'Status': 'Enabled'}
)
s3.put_object_lock_configuration(
    Bucket='org-decision-vault',
    ObjectLockConfiguration={
        'ObjectLockEnabled': 'Enabled',
        'Rule': {
            'DefaultRetention': {'Mode': 'GOVERNANCE', 'Years': 7}
        }
    }
)
```

### 4.2 Basic Checklist

```
□ Append-only storage configured
□ DECISION records include identity, action, cognition layers
□ write_decision() enforces no outcomes field
□ Audit trail records DECISION_CREATED event
□ 1-year retention policy documented
□ verify_integrity() tested
□ Schema validation passing for all written records
```

**Time to Basic conformance:** 1-2 weeks

---

## 5. Standard Conformance

**Additional requirements:** context layer, OUTCOME records, SHA-256 per record, canonical_state() API, 7-year retention, third-party audit access.

### 5.1 Standard Checklist

```
□ All Basic requirements met
□ Context layer captured on DECISION records
□ write_outcome() with parent_id validation working
□ FINAL uniqueness invariant enforced at write time
□ canonical_state() implemented and exposed via API
□ SHA-256 per-record hashing in index
□ 7-year retention configured
□ GET /records/{id}/state endpoint available for auditors
□ Third-party audit access documented
```

**Time to Standard conformance:** 4-6 weeks

---

## 6. Full Conformance

**Additional requirements:** counterfactuals on DECISION records, DPI/CFR/Learning Velocity computed, real-time governance, permanent retention.

### 6.1 Decision Quality Metrics

These implement the formulas in SPECIFICATION.md Section 6. Two conformant implementations MUST produce identical results for the same record graph.

```python
import numpy as np
from datetime import datetime, timezone


class MetricsEngine:

    def dpi(self, decision: dict, final_outcome: dict) -> float:
        """Decision Performance Index per SPECIFICATION.md Section 6.1."""
        action = decision.get("action", {})
        cognition = decision.get("cognition", {})
        outcomes = final_outcome.get("outcomes", {})

        expected = action.get("expected_value", 0)
        actual = outcomes.get("actual_result", 0)
        confidence = cognition.get("confidence", 0)
        latency_ms = cognition.get("decision_latency_ms")

        accuracy = max(0.0, 1.0 - abs(actual - expected) / max(abs(expected), 1e-9))
        calibration = 1.0 - abs(confidence - accuracy)
        attribution = 1.0 if decision.get("identity", {}).get("policy_hash") else 0.0
        risk_alignment = self._risk_alignment(decision)
        latency_score = self._latency_score(latency_ms)

        return (
            calibration   * 0.30 +
            attribution   * 0.25 +
            accuracy      * 0.25 +
            risk_alignment * 0.15 +
            latency_score  * 0.05
        )

    def cfr(self, decision: dict, final_outcome: dict) -> float:
        """Aggregate Counterfactual Regret per SPECIFICATION.md Section 6.2."""
        actual = final_outcome.get("outcomes", {}).get("actual_result", 0)
        counterfactuals = decision.get("counterfactuals", [])
        regrets = [
            cf["expected_outcome"] - actual
            for cf in counterfactuals
            if cf.get("expected_outcome") is not None and cf["expected_outcome"] - actual > 0
        ]
        return float(np.mean(regrets)) if regrets else 0.0

    def learning_velocity(self, store: "ODSStore", window_days: int = 30) -> float | None:
        """
        Learning Velocity per SPECIFICATION.md Section 6.3.
        OLS regression slope of DPI over time. Positive = improving quality.
        Returns None if fewer than 10 completed decisions in the window.
        """
        records = self._completed_decisions_in_window(store, window_days)
        if len(records) < 10:
            return None

        timestamps = []
        dpis = []
        t0 = datetime.fromisoformat(records[0]["decision"]["timestamp_utc"])
        for r in records:
            t = datetime.fromisoformat(r["decision"]["timestamp_utc"])
            days = (t - t0).total_seconds() / 86400
            timestamps.append(days)
            dpis.append(self.dpi(r["decision"], r["outcome_final"]))

        coeffs = np.polyfit(timestamps, dpis, 1)
        return float(coeffs[0])

    def _risk_alignment(self, decision: dict) -> float:
        context = decision.get("context", {})
        action = decision.get("action", {})
        volatility = context.get("volatility_state", "NORMAL")
        risk_posture = action.get("risk_posture", 0.5)
        target = {"LOW": 0.7, "NORMAL": 0.5, "ELEVATED": 0.3, "EXTREME": 0.1}.get(volatility, 0.5)
        return max(0.0, 1.0 - abs(risk_posture - target))

    def _latency_score(self, latency_ms: int | None, baseline_ms: int = 5000) -> float:
        if latency_ms is None:
            return 0.5
        return max(0.0, 1.0 - latency_ms / baseline_ms)

    def _completed_decisions_in_window(self, store: "ODSStore", days: int) -> list[dict]:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        completed = []
        if not store.index_file.exists():
            return completed
        with open(store.index_file) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("record_type") != "DECISION":
                    continue
                ts = datetime.fromisoformat(entry["timestamp_utc"]).timestamp()
                if ts < cutoff:
                    continue
                try:
                    state = store.canonical_state(entry["record_id"])
                    if state["outcome_final"]:
                        completed.append(state)
                except (KeyError, ValueError):
                    pass
        return sorted(completed, key=lambda r: r["decision"]["timestamp_utc"])
```

### 6.2 Full Checklist

```
□ All Standard requirements met
□ Counterfactuals logged on DECISION records
□ MetricsEngine.dpi() producing results
□ MetricsEngine.cfr() producing results
□ MetricsEngine.learning_velocity() with ≥10 completed decisions
□ Real-time governance alerts on policy violations
□ Permanent retention configured
□ Continuous third-party monitoring arranged
```

**Time to Full conformance:** 8-12 weeks

---

## 7. Storage Implementation

### 7.1 PostgreSQL with Append-Only Enforcement

```sql
CREATE TABLE ods_records (
    record_id     UUID PRIMARY KEY,
    record_type   TEXT NOT NULL CHECK (record_type IN ('DECISION', 'OUTCOME')),
    timestamp_utc TIMESTAMPTZ NOT NULL,
    parent_id     UUID REFERENCES ods_records(record_id),
    record_data   JSONB NOT NULL,
    record_hash   CHAR(64) NOT NULL,
    appended_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_parent_id ON ods_records(parent_id);

CREATE OR REPLACE FUNCTION reject_modifications()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'ODS records are immutable. record_id=% cannot be modified.', OLD.record_id;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_updates
    BEFORE UPDATE OR DELETE ON ods_records
    FOR EACH ROW EXECUTE FUNCTION reject_modifications();
```

---

## 8. API Design

```yaml
openapi: 3.0.0
info:
  title: ODS Record Store API
  version: 1.0.0

paths:
  /v1/records:
    post:
      summary: Write a new record (DECISION or OUTCOME)
      description: >
        Validates schema and store-level invariants before writing.
        Rejects if parent_id not found or FINAL already exists for parent.
      responses:
        '201':
          description: Record written
        '409':
          description: Store invariant violation (parent_id not found or duplicate FINAL)
        '422':
          description: Schema validation failure

  /v1/records/{record_id}:
    get:
      summary: Retrieve a single record by record_id

  /v1/records/{record_id}/state:
    get:
      summary: Canonical state of a DECISION per SPECIFICATION.md Section 3.5
      description: Returns the DECISION record and all linked OUTCOME records.

  /v1/records:
    get:
      summary: Query records
      parameters:
        - name: parent_id
          in: query
          description: Filter records by parent_id
        - name: record_type
          in: query
          description: Filter by record_type (DECISION or OUTCOME)

  /v1/records/{record_id}/verify:
    get:
      summary: Verify SHA-256 integrity of a record
```

---

## 9. Security Considerations

- Use TLS 1.3+ for all API communication
- Authenticate all writes with strong identity (OAuth 2.0 / mTLS)
- Store SHA-256 keys and signing keys in an HSM or equivalent
- Log all read and write access to the store
- Encrypt data at rest; ODS records are immutable but not inherently confidential
- Rate-limit write endpoints to prevent log flooding

---

## 10. Testing and Validation

### 10.1 Schema Validation

```bash
python validator/validate.py examples/minimal_decision.json
python validator/validate.py examples/complete_decision.json
python validator/validate.py examples/outcome_final.json --store examples/
```

### 10.2 Invariant Tests

```python
import unittest
from pathlib import Path
import tempfile


class TestODSStore(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.store = ODSStore(self.tmp)

    def _make_decision(self):
        return self.store.write_decision(
            model_version="v1.0.0",
            policy={"name": "test_policy"},
            action={"action_type": "APPROVE", "expected_value": 0.10},
            cognition={"confidence": 0.80, "rationale": "Test rationale for decision"},
        )

    def test_decision_has_no_outcomes_field(self):
        did = self._make_decision()
        record = self.store.get_record(did)
        self.assertNotIn("outcomes", record)

    def test_outcome_rejected_without_valid_parent(self):
        with self.assertRaises(ValueError, msg="parent_id not found"):
            self.store.write_outcome(
                parent_id="00000000-0000-0000-0000-000000000000",
                actual_result=0.12,
                realized_at="2026-06-01T00:00:00+00:00",
                outcome_status="FINAL",
            )

    def test_second_final_rejected(self):
        did = self._make_decision()
        self.store.write_outcome(did, 0.10, "2026-06-01T00:00:00+00:00", "FINAL")
        with self.assertRaises(ValueError, msg="FINAL already exists"):
            self.store.write_outcome(did, 0.12, "2026-06-02T00:00:00+00:00", "FINAL")

    def test_multiple_partials_allowed(self):
        did = self._make_decision()
        self.store.write_outcome(did, 0.05, "2026-05-15T00:00:00+00:00", "PARTIAL")
        self.store.write_outcome(did, 0.08, "2026-05-22T00:00:00+00:00", "PARTIAL")
        state = self.store.canonical_state(did)
        self.assertEqual(len(state["outcomes_partial"]), 2)
        self.assertIsNone(state["outcome_final"])

    def test_canonical_state(self):
        did = self._make_decision()
        self.store.write_outcome(did, 0.05, "2026-05-15T00:00:00+00:00", "PARTIAL")
        self.store.write_outcome(did, 0.12, "2026-06-01T00:00:00+00:00", "FINAL")
        state = self.store.canonical_state(did)
        self.assertEqual(len(state["outcomes_partial"]), 1)
        self.assertIsNotNone(state["outcome_final"])
        self.assertEqual(state["outcome_final"]["outcomes"]["actual_result"], 0.12)

    def test_integrity_verification(self):
        self._make_decision()
        ok, msg = self.store.verify_integrity()
        self.assertTrue(ok)
```

---

## 11. Deployment Patterns

### 11.1 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### 11.2 Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ods-store
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ods-store
  template:
    spec:
      containers:
      - name: ods-store
        image: ods/store:1.0.0
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: store-volume
          mountPath: /var/lib/ods
      volumes:
      - name: store-volume
        persistentVolumeClaim:
          claimName: ods-store-pvc
```

---

**Version:** 1.0.0
**Last Updated:** May 2026
**License:** Apache 2.0
