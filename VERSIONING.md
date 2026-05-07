# ODS Versioning Policy

ODS follows [Semantic Versioning 2.0.0](https://semver.org).

This document describes how versions are assigned, what each component means, and what implementers can rely on within and across versions.

---

## Version Format

```
MAJOR.MINOR.PATCH
```

Example: `1.0.0`, `1.1.0`, `2.0.0`.

---

## What Each Component Means

### MAJOR (X.0.0)

A major version increment indicates a **breaking change** to the specification.

Triggers a major version bump:
- Removing or renaming required schema fields
- Changing the type or constraints of a required field in incompatible ways
- Removing a previously declared conformance level
- Changing fundamental semantics that would invalidate existing records

Major versions are **rare** and **well-justified**. Each major version comes with:
- A clear migration guide
- A deprecation cycle (at least 12 months)
- Tooling support for record migration

### MINOR (1.X.0)

A minor version increment indicates **backward-compatible additions** to the specification.

Triggers a minor version bump:
- New optional schema fields
- New conformance options
- New verification mechanisms
- Clarifications that strengthen the spec without breaking existing records
- Extensions to the seven-layer schema (always optional)

Minor versions are **safe to adopt**. Records produced under v1.0 remain valid under v1.1, v1.2, and so on.

### PATCH (1.0.X)

A patch version increment indicates **clarifications** without changing semantics.

Triggers a patch version bump:
- Typographical fixes
- Improved language for clarity
- Better examples
- Tightened wording without changing requirements
- Fixed inconsistencies between sections

Patches **never change** what implementations must or may do. They only improve the documentation of the same standard.

---

## Stability Guarantees

### Within a Major Version (1.x → 1.y)

Implementations conformant with v1.0 MUST remain conformant with v1.1, v1.2, etc.

The Foundation commits that:
- Required fields will not be removed or renamed
- Field types will not change incompatibly
- Validation rules will not become stricter on existing fields
- Conformance levels (Basic, Standard, Full) will not change in ways that demote existing implementations

### Across Major Versions (1.x → 2.0)

Major version transitions provide:
- **Advance notice** — at least 6 months before publication
- **RFC review** — major changes go through public RFC process
- **Migration guide** — explicit path from previous major version
- **Tooling** — automated migration tools where feasible
- **Coexistence period** — both versions valid during transition

---

## How Versions Are Decided

All version increments go through the [RFC process](./rfcs/README.md):

1. Proposed change is documented as RFC
2. Public review (minimum 30 days)
3. Technical Committee evaluates impact:
   - Breaking? → Major
   - Additive? → Minor
   - Clarification? → Patch
4. Decision recorded with rationale
5. Implementation in next appropriate release

---

## Reading the Schema Version Field

Every ODS record includes:

```json
"_schema_version": "1.0"
```

Implementations:
- MUST validate this field
- MUST reject records with unknown major versions
- SHOULD accept records with newer minor versions of the same major
- SHOULD log a warning when reading newer minor versions to surface compatibility considerations

---

## Pre-1.0 Versions

ODS versions prior to 1.0 are **not stable** and may change without notice.

ODS v1.0 is the first **stable** release with the guarantees described in this document.

---

## Release Cadence

There is **no fixed cadence** for ODS releases. The Foundation prioritizes:
- Quality over speed
- Real-world feedback over theoretical purity
- Stability over feature velocity

Releases happen when meaningful improvements have been reviewed and accepted.

---

## Communication

Each release is accompanied by:
- An entry in [CHANGELOG.md](./CHANGELOG.md)
- A signed git tag
- A GitHub release with notes
- For major versions: a migration guide

---

## See Also

- [COMPATIBILITY.md](./COMPATIBILITY.md) — backward compatibility commitments
- [ROADMAP.md](./ROADMAP.md) — planned future versions
- [GOVERNANCE.md](./GOVERNANCE.md) — how decisions are made
- [rfcs/](./rfcs/) — active and accepted RFCs
