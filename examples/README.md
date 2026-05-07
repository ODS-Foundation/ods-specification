# ODS Examples

This directory contains example ODS-compliant decision records for reference.

## Files

### [minimal_decision.json](./minimal_decision.json)

**Compliance Level:** L1 (Basic)

The minimum viable ODS decision. Contains only required fields:
- Identity layer (decision_id, timestamp, model_version, policy_hash)
- Action layer (action_type, expected_value)
- Cognition layer (confidence, rationale)
- Governance layer (audit_trail, compliance)

**Use case:** Simple credit approval decision

---

### [complete_decision.json](./complete_decision.json)

**Compliance Level:** L3 (Meta-Learning)

A full ODS decision with all seven layers populated:
- Identity ✅
- Context ✅
- Action ✅
- Cognition ✅
- Outcomes ✅ (logged after the fact)
- Counterfactuals ✅
- Governance ✅ (with audit trail, explainability, compliance)

**Use case:** Trading system decision with regime context, outcome tracking, and counterfactual analysis

---

## Validation

To validate these examples against the ODS schema:

### Using Python (jsonschema library)

```python
import json
import jsonschema

# Load schema
with open('../schema/ods_decision_v1.json') as f:
    schema = json.load(f)

# Load and validate decision
with open('complete_decision.json') as f:
    decision = json.load(f)

try:
    jsonschema.validate(decision, schema)
    print("✅ Valid ODS v1.0 decision")
except jsonschema.ValidationError as e:
    print(f"❌ Validation failed: {e.message}")
```

### Using JavaScript (ajv library)

```javascript
const Ajv = require('ajv');
const fs = require('fs');

const ajv = new Ajv();
const schema = JSON.parse(fs.readFileSync('../schema/ods_decision_v1.json'));
const decision = JSON.parse(fs.readFileSync('complete_decision.json'));

const validate = ajv.compile(schema);
const valid = validate(decision);

if (valid) {
  console.log('✅ Valid ODS v1.0 decision');
} else {
  console.log('❌ Validation failed:', validate.errors);
}
```

---

## Creating Your Own Decisions

When creating ODS-compliant decisions:

1. **Always include required fields** — See schema for requirements
2. **Use UTC timestamps** — ISO 8601 format with timezone
3. **Generate UUID v4** for decision_id
4. **Calculate SHA-256** for policy_hash
5. **Be specific in rationale** — 50-500 character explanation
6. **Log outcomes when realized** — Immutable append, never modify decisions

See [IMPLEMENTATION.md](../IMPLEMENTATION.md) for full implementation guidance.
