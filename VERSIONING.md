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
"_schema_version": "1.1.0"
```

Implementations:
- MUST validate this field
- MUST reject records with unknown major versions
- SHOULD accept records with newer minor versions of the same major
- SHOULD log a warning when reading newer minor versions to surface compatibility considerations

---

## Version Status

### v2.0.0 — Current stable release

v2.0.0 introduces the ODS Core + Profiles architecture. The core specification is now domain-agnostic. Finance-domain fields are defined in the ODS-Finance/v1 profile. Implementations SHOULD target v2.0.0.

Conformance is declared as a two-axis statement: core level + optional profile level (e.g., "ODS Core v2 Standard + ODS-Finance v1 Full").

### v1.1.0 — Previous stable release

v1.1.0 remains a valid release. v1.1.0 records need not be re-logged; v2.0.0 implementations SHOULD support reading both schema versions. New implementations SHOULD target v2.0.0.

See [CHANGELOG.md](./CHANGELOG.md) for the migration path from v1.1.0 to v2.0.0.

### v1.0 — Deprecated

**v1.0 is deprecated and MUST NOT be used for new implementations.**

v1.0 contained a fundamental immutability contradiction: the specification required that records never be modified, while the reference implementation modified DECISION records in place to append outcome data. This rendered any v1.0-compliant system cryptographically unauditable — the hash of the original record would change after the first outcome was logged.

There is no migration path that preserves existing v1.0 record hashes. Implementers with v1.0 systems should treat existing records as non-conformant and re-log from source data where possible.

See [CHANGELOG.md](./CHANGELOG.md) for a full account of the findings.

### Pre-1.0 Versions

ODS versions prior to 1.0 are **not stable** and may change without notice.

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
