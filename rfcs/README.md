# ODS RFC Process

This directory contains active and accepted Requests for Comments (RFCs) for the Operational Decision Standard.

The RFC process is how substantive changes to ODS are proposed, reviewed, and accepted into the specification.

---

## When to Open an RFC

Open an RFC if you want to propose any of the following:

- **Schema changes** — new required fields, modified field semantics, removed fields
- **New conformance requirements** — additions or modifications to Basic, Standard, or Full levels
- **Verification mechanisms** — new ways to verify or attest to ODS records
- **Governance changes** — modifications to the RFC process itself, role definitions, or Foundation structure
- **Major clarifications** — changes that, while non-breaking, significantly shift how implementers interpret the spec

You do **not** need an RFC for:

- Typo fixes (open a PR directly)
- Documentation improvements that don't change requirements
- Bug reports against the validator or examples
- Feature requests that haven't been thought through (open a Discussion first)

---

## RFC Lifecycle

```
┌───────┐    ┌────────┐    ┌──────────┐    ┌─────────────┐    ┌─────────────┐
│ Draft │ →  │ Review │ →  │ Accepted │ →  │ Implemented │ →  │ Deprecated  │
└───────┘    └────────┘    └──────────┘    └─────────────┘    └─────────────┘
   ↓             ↓               ↓                ↓                  ↓
   │             │          (in next         (shipped in       (replaced or
   │             │           release)         release)          removed in
   │             │                                              future version)
   │             ↓
   │         Rejected  (with rationale recorded)
   ↓
Withdrawn  (author chooses to stop)
```

### Draft

The author opens an RFC issue using the [RFC template](.github/ISSUE_TEMPLATE/rfc.md) or by submitting a markdown file in this directory.

The RFC is in **Draft** status until the author marks it ready for review.

### Review

Once submitted for review, the RFC enters a **minimum 30-day public comment period**.

During review:
- Anyone can comment
- The author iterates based on feedback
- Stakeholders are notified (maintainers, sector experts, implementers)
- Open questions are documented

The review period may be extended if substantial revisions are needed.

### Accepted / Rejected

After review, the **Technical Committee** evaluates the RFC and reaches a decision:

- **Accepted** — The RFC will be implemented in a future release
- **Rejected** — The RFC will not be implemented; rationale is recorded
- **Postponed** — Decision deferred pending more information or maturity
- **Returned for revision** — Substantial changes needed; back to Draft

All decisions are documented publicly with rationale.

### Implemented

Accepted RFCs are implemented in the next appropriate release:

- Schema additions → next minor version (1.x)
- Breaking changes → next major version (2.0)
- Documentation/clarifications → next patch version (1.0.x)

The RFC is updated to **Implemented** status when shipped, with a reference to the release.

### Deprecated

If an Implemented RFC's capability is later removed or replaced, the RFC moves to **Deprecated** status.

The RFC remains in this directory permanently as a historical record.

---

## RFC Numbering

RFCs are numbered sequentially as they are accepted: RFC-0001, RFC-0002, etc.

Numbers are assigned **on acceptance**, not at draft time. Drafts use a placeholder identifier.

---

## RFC File Structure

When an RFC is accepted, it is added to this directory as:

```
rfcs/
├── README.md          (this file)
├── TEMPLATE.md        (template for new RFCs)
├── RFC-0001-name.md   (accepted RFCs)
├── RFC-0002-name.md
└── ...
```

Each RFC includes:
- Number and title
- Status and dates
- Summary, motivation, proposal
- Alternatives considered
- Backward compatibility analysis
- Implementation plan
- Decision and rationale

See [TEMPLATE.md](./TEMPLATE.md) for the full structure.

---

## How to Submit an RFC

### Option 1: Issue (Recommended for First-Time Contributors)

1. Open an issue using the [RFC template](.github/ISSUE_TEMPLATE/rfc.md)
2. Fill in motivation, proposed change, alternatives, and impact
3. Engage with reviewers during the comment period
4. If accepted, the issue is converted to an RFC file by maintainers

### Option 2: Pull Request (For Experienced Contributors)

1. Copy [TEMPLATE.md](./TEMPLATE.md) to a new file: `RFC-XXXX-short-title.md`
2. Fill in all sections
3. Open a pull request adding the file to this directory
4. Engage with reviewers
5. On acceptance, the file is renamed with the assigned RFC number

---

## Decision Process

The Technical Committee makes RFC decisions by:

1. **Consensus first** — most RFCs reach agreement through discussion
2. **Majority vote** — when consensus is not reached, formal vote
3. **Documented rationale** — every decision (accept, reject, postpone) includes reasoning
4. **Public record** — all decisions are visible in the RFC and issue history

The Technical Committee is bound by the [GOVERNANCE.md](../GOVERNANCE.md) document.

---

## RFC Quality Standards

A strong RFC includes:

- ✅ Clear problem statement
- ✅ Concrete proposed change (with examples)
- ✅ Multiple alternatives considered
- ✅ Honest assessment of drawbacks
- ✅ Backward compatibility analysis
- ✅ Implementation plan
- ✅ References to related work, prior RFCs, external standards

A weak RFC has:

- ❌ Vague problem statement
- ❌ Solution before motivation
- ❌ No alternatives considered
- ❌ No discussion of trade-offs
- ❌ No implementation plan
- ❌ No relationship to existing spec

Weak RFCs will be returned for revision before review begins.

---

## See Also

- [TEMPLATE.md](./TEMPLATE.md) — RFC template
- [GOVERNANCE.md](../GOVERNANCE.md) — overall governance model
- [VERSIONING.md](../VERSIONING.md) — how RFC outcomes affect versions
- [CONTRIBUTING.md](../CONTRIBUTING.md) — how to contribute to ODS
