# RFC-XXXX: [Short Title]

| Field | Value |
|-------|-------|
| **RFC Number** | XXXX (assigned on acceptance) |
| **Title** | [Short, descriptive title] |
| **Author(s)** | [Name(s) and contact] |
| **Status** | Draft |
| **Created** | YYYY-MM-DD |
| **Updated** | YYYY-MM-DD |
| **Affects** | [SPECIFICATION / IMPLEMENTATION / GOVERNANCE / etc.] |
| **Supersedes** | [None or RFC-XXXX] |

---

## Summary

A 2-3 sentence summary of what is proposed. Plain language. Anyone reading just this section should understand what the RFC is about.

---

## Motivation

Why is this change needed?

- What problem does it solve?
- Who experiences this problem?
- What's the cost of not addressing it?
- Why now?

Concrete examples are encouraged. Cite real-world cases where possible.

---

## Proposed Change

The detailed specification of the proposed change.

### Schema Changes (if applicable)

```json
{
  "example": "of the proposed schema",
  "with_new_field": "demonstrating the change"
}
```

### Conformance Changes (if applicable)

Describe how this affects each conformance level:
- **Basic:** [no change / specific change]
- **Standard:** [no change / specific change]
- **Full:** [no change / specific change]

### Behavioral Changes (if applicable)

Describe any changes to how implementations must behave.

### Documentation Changes (if applicable)

List sections of the spec that would need updating.

---

## Alternatives Considered

What other approaches did you consider? Why were they rejected?

### Alternative 1: [Name]

**Description:** [What is this alternative?]

**Why rejected:** [Specific reasons]

### Alternative 2: [Name]

**Description:** [What is this alternative?]

**Why rejected:** [Specific reasons]

### Alternative 3: Do Nothing

**Description:** Keep the spec as-is.

**Why rejected:** [What is the cost of inaction?]

---

## Drawbacks

What are the downsides of this proposal? Be honest.

- [Drawback 1]
- [Drawback 2]
- [Drawback 3]

How do these drawbacks compare to the benefits?

---

## Backward Compatibility

How does this affect existing ODS implementations?

- [ ] **Fully backward compatible** — no migration needed
- [ ] **Backward compatible with deprecation** — old behavior remains valid for migration period
- [ ] **Breaking change** — requires major version bump

If backward compatible:
- How do v1.0 records remain valid?
- How do v1.0 implementations remain conformant?

If breaking:
- What is the migration path?
- What tooling will be provided?
- What is the deprecation timeline?

---

## Reference Implementation

If you have a proof-of-concept, link or describe it here.

```python
# Example code demonstrating the proposed change
def example_implementation():
    pass
```

---

## Impact Analysis

### Affected Parties

- **Specification readers:** [How are they affected?]
- **Implementers:** [What do they need to do?]
- **Auditors:** [How does verification change?]
- **Tool developers:** [What tooling needs updating?]

### Effort Estimate

- **Specification changes:** [hours/days]
- **Reference implementation updates:** [hours/days]
- **Documentation updates:** [hours/days]
- **Tooling updates:** [hours/days]

### Risk Assessment

- [ ] **Low risk** — well-understood change with clear precedent
- [ ] **Medium risk** — novel but well-bounded
- [ ] **High risk** — fundamental change with broad implications

Rationale for risk level: [explanation]

---

## Adoption Plan

When and how should this be rolled out?

- [ ] **Immediate** — patch release (1.0.x)
- [ ] **Next minor version** — 1.x.0
- [ ] **Next major version** — 2.0
- [ ] **Optional extension** — implementations can adopt at their own pace

Phasing (if applicable):
1. Phase 1: [Description]
2. Phase 2: [Description]
3. Phase 3: [Description]

---

## Open Questions

Questions that the RFC author has not yet resolved and would like community input on:

1. [Question 1?]
2. [Question 2?]
3. [Question 3?]

---

## References

- Related RFCs: [RFC-XXXX, RFC-XXXX]
- External standards: [Links to relevant external work]
- Academic references: [Citations]
- Industry examples: [Real-world implementations]
- Prior discussions: [Issue links, discussion threads]

---

## Decision (To be filled by Technical Committee)

| Field | Value |
|-------|-------|
| **Decision** | [Accepted / Rejected / Postponed / Returned for revision] |
| **Decision Date** | YYYY-MM-DD |
| **Decided By** | [Technical Committee members involved] |
| **Implementation Target** | [v1.x.0 / v2.0 / Patch / N/A] |

### Rationale

[Detailed explanation of the decision, including:]
- Key arguments for and against
- How concerns were resolved (or why they prevailed)
- Connection to broader ODS principles
- Any conditions on acceptance

---

## Author Checklist

Before submitting for review, confirm:

- [ ] Motivation is clear and concrete
- [ ] Proposed change is fully specified
- [ ] Backward compatibility is addressed
- [ ] At least 2 alternatives have been considered
- [ ] Drawbacks are honestly disclosed
- [ ] Impact analysis is thorough
- [ ] References are provided where relevant
- [ ] Document is well-formatted and proofread

---

**Note:** This RFC will be reviewed for at least 30 days before any decision is made. See [README.md](./README.md) in this directory for the full RFC process.
