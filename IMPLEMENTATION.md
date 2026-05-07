# ODS v1.0 Implementation Guide

**Version:** 1.0  
**Audience:** Developers, System Architects, CIOs  
**Prerequisites:** Familiarity with [SPECIFICATION.md](./SPECIFICATION.md)  
**Estimated Implementation Time:** 4-12 weeks (depending on compliance level)

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Architecture Patterns](#2-architecture-patterns)
3. [Implementation Roadmap](#3-implementation-roadmap)
4. [Level 1 Implementation](#4-level-1-implementation)
5. [Level 2 Implementation](#5-level-2-implementation)
6. [Level 3 Implementation](#6-level-3-implementation)
7. [Storage Implementation](#7-storage-implementation)
8. [API Design](#8-api-design)
9. [Security Considerations](#9-security-considerations)
10. [Testing and Validation](#10-testing-and-validation)
11. [Deployment Patterns](#11-deployment-patterns)
12. [Reference Implementation](#12-reference-implementation)

---

## 1. Getting Started

### 1.1 Determine Your Compliance Level

Before implementing ODS, determine which compliance level your organization requires:

**Choose Level 1 if:**
- Internal governance only
- No regulatory requirements
- Basic accountability needed
- Limited audit scope

**Choose Level 2 if:**
- Regulated industry (finance, healthcare, energy)
- External audit requirements
- Multi-year retention needed
- Third-party oversight

**Choose Level 3 if:**
- Mission-critical decision systems
- Continuous improvement required
- Institutional intelligence goal
- Competitive advantage through decision quality

### 1.2 Assessment Checklist

Before starting implementation:

```markdown
□ Executive sponsorship secured
□ Compliance level determined
□ Budget allocated
□ Technical team assigned
□ Existing decision workflows mapped
□ Data retention policies reviewed
□ Storage infrastructure evaluated
□ Security requirements documented
```

### 1.3 Quick Start

The fastest path to ODS compliance:

1. **Week 1:** Install reference implementation
2. **Week 2:** Configure for your environment
3. **Week 3:** Integrate with decision workflows
4. **Week 4:** Test and validate

---

## 2. Architecture Patterns

### 2.1 Centralized Decision Vault

**Pattern:** Single central repository for all organizational decisions.

**Pros:**
- Simple governance
- Easy auditing
- Consistent schema
- Lower cost

**Cons:**
- Single point of failure
- Scaling challenges at very high volume
- Cross-region latency

**Best for:** Level 1-2, organizations < 10,000 decisions/day

```
┌─────────────────────────────────────────┐
│         Decision Vault                   │
│  ┌─────────────────────────────────┐    │
│  │   Append-Only Storage           │    │
│  │   - Decisions                   │    │
│  │   - Snapshots                   │    │
│  │   - Outcomes                    │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Verification Layer            │    │
│  │   - Cryptographic hashing       │    │
│  │   - Integrity checks            │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
           ▲            ▲            ▲
           │            │            │
     ┌─────┴───┐  ┌────┴────┐  ┌───┴─────┐
     │Trading  │  │ Risk    │  │Strategy │
     │System   │  │ Mgmt    │  │ Team    │
     └─────────┘  └─────────┘  └─────────┘
```

### 2.2 Distributed Decision Fabric

**Pattern:** Multiple vaults synchronized via consensus protocol.

**Pros:**
- High availability
- Geographic distribution
- Horizontal scaling
- Fault tolerance

**Cons:**
- Complex governance
- Higher cost
- Consistency challenges
- Operational overhead

**Best for:** Level 3, global organizations, > 50,000 decisions/day

### 2.3 Hybrid (Recommended for Most)

**Pattern:** Central vault with regional caching layers.

**Pros:**
- Balance of simplicity and performance
- Cost-effective
- Good for multi-region deployments
- Easier compliance

**Best for:** Level 2-3, most enterprise deployments

---

## 3. Implementation Roadmap

### 3.1 Phase-Based Approach

**Phase 1: Foundation (Weeks 1-2)**
- Set up append-only storage
- Implement core schema
- Basic logging functionality
- Unit tests

**Phase 2: Integration (Weeks 3-4)**
- Connect to decision systems
- API development
- Authentication/authorization
- Integration tests

**Phase 3: Governance (Weeks 5-6)**
- Audit trail implementation
- Verification mechanisms
- Compliance reporting
- Security hardening

**Phase 4: Meta-Learning (Weeks 7-12)** *(Level 3 only)*
- Outcome tracking automation
- Counterfactual generation
- Decision quality metrics
- Learning velocity dashboard

### 3.2 Team Structure

**Minimum team:**
- 1 Backend engineer (storage, API)
- 1 Integration engineer (connect to decision systems)
- 1 Security engineer (compliance, crypto)
- 0.5 Product manager (requirements, testing)

**Ideal team:**
- 2 Backend engineers
- 1 Frontend engineer (dashboard)
- 1 Integration engineer
- 1 Security engineer
- 1 Data engineer (analytics)
- 1 Product manager

---

## 4. Level 1 Implementation

### 4.1 Core Requirements

✅ Decision logging with identity layer  
✅ Immutability (append-only)  
✅ Basic audit trail  
✅ Minimum 1-year retention

### 4.2 Minimal Implementation (Python)

```python
# minimal_ods_vault.py

import json
import uuid
from datetime import datetime
from pathlib import Path
import hashlib

class DecisionVault:
    """
    Minimal ODS Level 1 compliant decision vault.
    """
    
    def __init__(self, vault_path="./decision_vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)
        self.decisions_path = self.vault_path / "decisions"
        self.decisions_path.mkdir(exist_ok=True)
        self.index_file = self.vault_path / "index.jsonl"
    
    def log_decision(self, decision_data):
        """
        Log a decision to the vault.
        
        Args:
            decision_data: Dict containing decision information
            
        Returns:
            decision_id: UUID of logged decision
        """
        # Generate decision ID
        decision_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Build ODS-compliant decision object
        decision = {
            "_schema_version": "1.0",
            "identity": {
                "decision_id": decision_id,
                "timestamp_utc": timestamp,
                "model_version": decision_data.get("model_version", "v1.0.0"),
                "policy_hash": self._calculate_policy_hash(decision_data)
            },
            "action": decision_data.get("action", {}),
            "cognition": decision_data.get("cognition", {}),
            "governance": {
                "audit_trail": [
                    {
                        "timestamp_utc": timestamp,
                        "event": "DECISION_CREATED",
                        "actor": decision_data.get("actor", "SYSTEM"),
                        "metadata": {}
                    }
                ]
            }
        }
        
        # Add optional layers if present
        if "context" in decision_data:
            decision["context"] = decision_data["context"]
        
        # Calculate decision hash
        decision_hash = self._calculate_decision_hash(decision)
        
        # Write to append-only storage
        decision_file = self.decisions_path / f"{decision_id}.json"
        with open(decision_file, 'w') as f:
            json.dump(decision, f, indent=2)
        
        # Append to index
        index_entry = {
            "decision_id": decision_id,
            "timestamp_utc": timestamp,
            "hash": decision_hash,
            "file_path": f"decisions/{decision_id}.json"
        }
        
        with open(self.index_file, 'a') as f:
            f.write(json.dumps(index_entry) + '\n')
        
        return decision_id
    
    def get_decision(self, decision_id):
        """Retrieve a decision by ID."""
        decision_file = self.decisions_path / f"{decision_id}.json"
        
        if not decision_file.exists():
            raise ValueError(f"Decision {decision_id} not found")
        
        with open(decision_file, 'r') as f:
            return json.load(f)
    
    def _calculate_policy_hash(self, decision_data):
        """Calculate hash of decision policy."""
        policy = decision_data.get("policy", {})
        policy_str = json.dumps(policy, sort_keys=True)
        return hashlib.sha256(policy_str.encode()).hexdigest()
    
    def _calculate_decision_hash(self, decision):
        """Calculate SHA-256 hash of decision."""
        normalized = json.dumps(decision, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def verify_integrity(self):
        """Verify integrity of all decisions."""
        with open(self.index_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                decision = self.get_decision(entry['decision_id'])
                current_hash = self._calculate_decision_hash(decision)
                
                if current_hash != entry['hash']:
                    return False, f"Tampered: {entry['decision_id']}"
        
        return True, "All decisions verified"

# Usage Example
vault = DecisionVault()

decision_id = vault.log_decision({
    "model_version": "v1.0.0",
    "actor": "TRADING_SYSTEM",
    "action": {
        "action_type": "BUY",
        "action_size": 0.25,
        "expected_value": 0.12
    },
    "cognition": {
        "confidence": 0.75,
        "rationale": "Strong momentum signal detected"
    }
})

print(f"Decision logged: {decision_id}")

# Verify integrity
is_valid, message = vault.verify_integrity()
print(f"Integrity check: {message}")
```

### 4.3 Storage Setup

**Option 1: Local filesystem (Development)**
```bash
mkdir -p /var/lib/decision_vault/decisions
chmod 600 /var/lib/decision_vault
```

**Option 2: AWS S3 (Production)**
```python
import boto3

s3 = boto3.client('s3')

# Enable versioning (immutability)
s3.put_bucket_versioning(
    Bucket='org-decision-vault',
    VersioningConfiguration={'Status': 'Enabled'}
)

# Enable Object Lock (WORM)
s3.put_object_lock_configuration(
    Bucket='org-decision-vault',
    ObjectLockConfiguration={
        'ObjectLockEnabled': 'Enabled',
        'Rule': {
            'DefaultRetention': {
                'Mode': 'GOVERNANCE',
                'Years': 7
            }
        }
    }
)
```

### 4.4 Level 1 Checklist

```markdown
□ Append-only storage configured
□ Decision schema implemented (identity + action + cognition)
□ log_decision() function working
□ get_decision() function working
□ Basic audit trail logging
□ File-based or S3 storage selected
□ 1-year retention policy documented
□ Integrity verification tested
□ Basic unit tests passing
```

**Time to Level 1 Compliance:** 1-2 weeks

---

## 5. Level 2 Implementation

### 5.1 Additional Requirements

✅ All Level 1 requirements  
✅ Complete context layer  
✅ Outcome tracking  
✅ Cryptographic verification  
✅ Minimum 7-year retention  
✅ Third-party audit capability

### 5.2 Context Layer Implementation

```python
class Level2DecisionVault(DecisionVault):
    """
    ODS Level 2 compliant vault with context and outcomes.
    """
    
    def log_decision(self, decision_data):
        """Enhanced decision logging with context."""
        decision_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        decision = {
            "_schema_version": "1.0",
            "identity": {
                "decision_id": decision_id,
                "timestamp_utc": timestamp,
                "model_version": decision_data["model_version"],
                "policy_hash": self._calculate_policy_hash(decision_data)
            },
            "context": {
                "regime_state": decision_data["context"]["regime_state"],
                "regime_confidence": decision_data["context"]["regime_confidence"],
                "volatility_state": decision_data["context"].get("volatility_state"),
                "macro_state_vector": decision_data["context"].get("macro_state_vector", [])
            },
            "action": decision_data["action"],
            "cognition": decision_data["cognition"],
            "outcomes": {},  # Populated later
            "governance": {
                "audit_trail": [
                    {
                        "timestamp_utc": timestamp,
                        "event": "DECISION_CREATED",
                        "actor": decision_data.get("actor", "SYSTEM"),
                        "metadata": decision_data.get("metadata", {})
                    }
                ],
                "compliance": {
                    "risk_limit_checks": decision_data.get("risk_checks", []),
                    "policy_violations": [],
                    "approvals": decision_data.get("approvals", [])
                }
            }
        }
        
        return super()._save_decision(decision)
    
    def log_outcome(self, decision_id, outcome_data):
        """
        Log outcome for a decision.
        CRITICAL: This is append-only.
        """
        decision = self.get_decision(decision_id)
        
        if decision.get("outcomes") and decision["outcomes"].get("actual_result"):
            raise ValueError("Outcome already logged. ODS is immutable.")
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        expected = decision["cognition"]["expected_value"]
        actual = outcome_data["actual_result"]
        delta = actual - expected
        
        outcome = {
            "actual_result": actual,
            "realized_at": timestamp,
            "delta_from_expected": delta,
            "outcome_quality": outcome_data.get("outcome_quality", 0.5)
        }
        
        decision["outcomes"] = outcome
        decision["governance"]["audit_trail"].append({
            "timestamp_utc": timestamp,
            "event": "OUTCOME_LOGGED",
            "actor": outcome_data.get("actor", "OUTCOME_TRACKER"),
            "metadata": {"source": outcome_data.get("source", "manual")}
        })
        
        self._save_decision_version(decision)
        return outcome
```

### 5.3 Cryptographic Verification

```python
class CryptoVerifier:
    """Cryptographic verification for Level 2 compliance."""
    
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.merkle_tree_file = self.vault_path / "merkle_tree.json"
    
    def build_merkle_tree(self, decision_ids):
        """Build Merkle tree for batch verification."""
        decisions = [self._load_decision(did) for did in decision_ids]
        leaves = [self._hash_decision(d) for d in decisions]
        
        tree = [leaves]
        while len(tree[-1]) > 1:
            level = tree[-1]
            parent_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else left
                parent = self._hash_pair(left, right)
                parent_level.append(parent)
            tree.append(parent_level)
        
        merkle_root = tree[-1][0]
        self._save_merkle_tree({
            "merkle_root": merkle_root,
            "tree": tree,
            "decision_count": len(decision_ids),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        return merkle_root
```

### 5.4 Level 2 Checklist

```markdown
□ All Level 1 requirements met
□ Context layer fully implemented
□ Regime detection integrated
□ Outcome logging functional
□ Merkle tree verification working
□ 7-year retention configured
□ Audit API endpoints created
□ Third-party audit documentation prepared
□ Compliance reporting dashboard built
□ Security audit completed
```

**Time to Level 2 Compliance:** 4-6 weeks

---

## 6. Level 3 Implementation

### 6.1 Additional Requirements

✅ All Level 2 requirements  
✅ Counterfactual tracking  
✅ Meta-learning framework  
✅ Decision quality metrics  
✅ Learning velocity measurement  
✅ Real-time governance  
✅ Permanent retention

### 6.2 Counterfactual Engine

```python
class CounterfactualEngine:
    """Generate and track counterfactuals for Level 3 compliance."""
    
    def generate_counterfactuals(self, decision, num_alternatives=5):
        """Generate alternative actions and their expected outcomes."""
        action_type = decision["action"]["action_type"]
        action_size = decision["action"]["action_size"]
        
        counterfactuals = []
        
        # Alternative 1: Opposite action
        if action_type == "BUY":
            alt_action = "SELL"
        elif action_type == "SELL":
            alt_action = "BUY"
        else:
            alt_action = "HOLD"
        
        counterfactuals.append({
            "alternative_action": alt_action,
            "expected_outcome": self._estimate_outcome(alt_action, decision),
            "regret": 0.0
        })
        
        # Alternative sizes
        for size_factor in [0.5, 1.5, 2.0]:
            alt_size = action_size * size_factor
            counterfactuals.append({
                "alternative_action": f"{action_type}_{alt_size:.2f}",
                "expected_outcome": self._estimate_outcome(action_type, decision, alt_size),
                "regret": 0.0
            })
        
        return counterfactuals[:num_alternatives]
    
    def calculate_regret(self, decision, actual_outcome):
        """Calculate regret for each counterfactual."""
        counterfactuals = decision.get("counterfactuals", [])
        for cf in counterfactuals:
            cf["regret"] = cf["expected_outcome"] - actual_outcome["actual_result"]
        return counterfactuals
```

### 6.3 Meta-Learning Framework

```python
class MetaLearning:
    """Meta-learning framework for Level 3 compliance."""
    
    def __init__(self, vault):
        self.vault = vault
    
    def calculate_dpi(self, decision, outcome):
        """
        Calculate Decision Performance Index.
        DPI = f(calibration, attribution, accuracy, risk_alignment, latency)
        """
        scores = {
            "calibration": self._score_calibration(decision, outcome),
            "attribution": self._score_attribution(decision, outcome),
            "accuracy": self._score_accuracy(decision, outcome),
            "risk_alignment": self._score_risk_alignment(decision),
            "latency": self._score_latency(decision)
        }
        
        dpi = (
            scores["calibration"] * 0.30 +
            scores["attribution"] * 0.25 +
            scores["accuracy"] * 0.25 +
            scores["risk_alignment"] * 0.15 +
            scores["latency"] * 0.05
        )
        
        return dpi, scores
    
    def calculate_learning_velocity(self, time_window_days=30):
        """
        Calculate rate of decision quality improvement.
        LV = Δ(DQI) / Δ(Time)
        Negative is good (errors decreasing).
        """
        decisions = self.vault.get_decisions_with_outcomes(days=time_window_days)
        
        if len(decisions) < 10:
            return None
        
        dpis = []
        for d in decisions:
            dpi, _ = self.calculate_dpi(d, d["outcomes"])
            dpis.append({
                "timestamp": d["identity"]["timestamp_utc"],
                "dpi": dpi
            })
        
        dpis.sort(key=lambda x: x["timestamp"])
        
        import numpy as np
        timestamps = [self._parse_timestamp(d["timestamp"]) for d in dpis]
        dpi_values = [d["dpi"] for d in dpis]
        
        start_time = min(timestamps)
        days = [(t - start_time).total_seconds() / 86400 for t in timestamps]
        
        coeffs = np.polyfit(days, dpi_values, 1)
        return coeffs[0]  # Slope
```

### 6.4 Level 3 Checklist

```markdown
□ All Level 2 requirements met
□ Counterfactual engine implemented
□ DPI calculation automated
□ CFR (Counterfactual Regret) tracked
□ Learning Velocity dashboard built
□ Observer Drift monitoring active
□ Real-time governance alerts configured
□ Permanent retention infrastructure
□ Continuous third-party monitoring arranged
□ Meta-learning feedback loops operational
```

**Time to Level 3 Compliance:** 8-12 weeks

---

## 7. Storage Implementation

### 7.1 Production Storage Options

#### Option A: AWS S3 with Object Lock

**Pros:** Fully managed, WORM compliance, 99.999999999% durability

```python
import boto3

class S3DecisionVault:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
    
    def save_decision(self, decision):
        key = f"decisions/{decision['identity']['decision_id']}.json"
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(decision),
            ObjectLockMode='GOVERNANCE',
            ObjectLockRetainUntilDate=datetime.utcnow() + timedelta(days=2555)
        )
```

#### Option B: PostgreSQL with Append-Only Pattern

```sql
CREATE TABLE decisions (
    decision_id UUID PRIMARY KEY,
    timestamp_utc TIMESTAMP NOT NULL,
    decision_data JSONB NOT NULL,
    decision_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION prevent_modifications()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'ODS decisions are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_updates
    BEFORE UPDATE OR DELETE ON decisions
    FOR EACH ROW
    EXECUTE FUNCTION prevent_modifications();
```

---

## 8. API Design

### 8.1 RESTful API Specification

```yaml
openapi: 3.0.0
info:
  title: ODS Decision Vault API
  version: 1.0.0

paths:
  /v1/decisions:
    post:
      summary: Log a new decision
      responses:
        '201':
          description: Decision logged
    
    get:
      summary: Query decisions
      parameters:
        - name: start_date
          in: query
        - name: end_date
          in: query
        - name: regime_state
          in: query
  
  /v1/decisions/{decision_id}:
    get:
      summary: Get specific decision
  
  /v1/decisions/{decision_id}/outcome:
    put:
      summary: Log outcome for decision
  
  /v1/decisions/{decision_id}/verify:
    get:
      summary: Verify decision integrity
```

### 8.2 Flask Implementation

```python
from flask import Flask, request, jsonify
from decision_vault import DecisionVault

app = Flask(__name__)
vault = DecisionVault()

@app.route('/v1/decisions', methods=['POST'])
def log_decision():
    decision_data = request.json
    try:
        decision_id = vault.log_decision(decision_data)
        decision = vault.get_decision(decision_id)
        decision_hash = vault.calculate_hash(decision)
        return jsonify({
            "decision_id": decision_id,
            "hash": decision_hash,
            "timestamp": decision["identity"]["timestamp_utc"]
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 9. Security Considerations

### 9.1 Authentication

```python
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        return f(*args, **kwargs)
    return decorated
```

### 9.2 Encryption at Rest

```python
from cryptography.fernet import Fernet

class EncryptedDecisionVault(DecisionVault):
    def __init__(self, vault_path, encryption_key):
        super().__init__(vault_path)
        self.cipher = Fernet(encryption_key)
    
    def _save_decision(self, decision):
        decision_json = json.dumps(decision)
        encrypted = self.cipher.encrypt(decision_json.encode())
        decision_file = self.decisions_path / f"{decision['identity']['decision_id']}.enc"
        decision_file.write_bytes(encrypted)
```

---

## 10. Testing and Validation

### 10.1 Unit Tests

```python
import unittest

class TestDecisionVault(unittest.TestCase):
    def setUp(self):
        self.vault = DecisionVault(vault_path="./test_vault")
    
    def test_log_decision(self):
        decision_id = self.vault.log_decision({
            "model_version": "v1.0.0",
            "action": {"action_type": "BUY", "action_size": 0.25},
            "cognition": {"confidence": 0.75, "rationale": "Test"}
        })
        
        self.assertIsNotNone(decision_id)
    
    def test_immutability(self):
        decision_id = self.vault.log_decision({...})
        with self.assertRaises(Exception):
            self.vault.modify_decision(decision_id, {...})
    
    def test_integrity_verification(self):
        decision_id = self.vault.log_decision({...})
        is_valid, message = self.vault.verify_integrity()
        self.assertTrue(is_valid)
```

---

## 11. Deployment Patterns

### 11.1 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```yaml
version: '3.8'

services:
  vault:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./decision_vault:/var/lib/decision_vault
    environment:
      - VAULT_PATH=/var/lib/decision_vault
      - SECRET_KEY=${SECRET_KEY}
```

### 11.2 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decision-vault
spec:
  replicas: 3
  selector:
    matchLabels:
      app: decision-vault
  template:
    metadata:
      labels:
        app: decision-vault
    spec:
      containers:
      - name: vault
        image: ods/decision-vault:1.0
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: vault-storage
          mountPath: /var/lib/decision_vault
      volumes:
      - name: vault-storage
        persistentVolumeClaim:
          claimName: vault-pvc
```

---

## 12. Reference Implementation

### 12.1 ORPI Decision Vault™

The reference implementation is the **ORPI Decision Vault™** by ORPI Systems.

**Features:**
- Complete ODS Level 3 compliance
- Production-ready architecture
- Comprehensive test suite
- Docker deployment
- API documentation
- Real-world validation: 1,786 decisions logged

For partnership inquiries: contact ORPI Systems.

---

## Appendix: Troubleshooting

### Common Issues

**Issue:** "Permission denied" when writing decisions  
**Solution:** Check file permissions: `chmod 755 /var/lib/decision_vault`

**Issue:** "Integrity verification failed"  
**Solution:** Check for file system corruption or unauthorized modifications

**Issue:** "Out of disk space"  
**Solution:** Implement log rotation and archival to cold storage

---

## Support

**Documentation:** [SPECIFICATION.md](./SPECIFICATION.md)  
**Community:** [GitHub Discussions](https://github.com/ODS-Foundation/ods-specification/discussions)  
**Issues:** [GitHub Issues](https://github.com/ODS-Foundation/ods-specification/issues)

---

**Version:** 1.0  
**Last Updated:** April 2026  
**License:** Apache 2.0

---

*Building institutional decision memory, one decision at a time.*
