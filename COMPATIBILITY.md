# ODS Compatibility Policy

This document describes the backward compatibility commitments of the Operational Decision Standard.

Compatibility is the foundation of trust in any infrastructure standard. Organizations that adopt ODS need to know that records they produce today will remain readable, valid, and verifiable in the future.

---

## Core Commitment

**Once a field is declared in ODS, it stays.**

For any major version (e.g., the entire v1.x series), the Foundation commits to:

1. **Field stability** — Required fields will not be removed or renamed
2. **Type stability** — Field types will not change incompatibly
3. **Semantic stability** — The meaning of a field will not change
4. **Validation stability** — Existing records will not become invalid due to stricter rules
5. **Conformance stability** — Levels (Basic, Standard, Full) will not change in ways that demote conformant implementations

---

## What Compatibility Guarantees

### Records Stay Valid

A record produced under v1.0 is **valid** under any v1.x release.

```
v1.0 record → v1.0 validator: ✓ valid
v1.0 record → v1.1 validator: ✓ valid
v1.0 record → v1.2 validator: ✓ valid
```

### Implementations Stay Conformant

An implementation conformant with v1.0 at a given level (Basic, Standard, or Full) remains conformant at that level under any v1.x release.

The Foundation will not retroactively raise the bar.

### Schema Validators Stay Useful

Validators built for v1.0 may not understand new optional fields introduced in v1.1, but they will not falsely reject v1.1-aware records that include them. (Validators MUST treat unknown optional fields as compatible, per the schema.)

---

## What Changes Across Minor Versions

Minor versions add capabilities **additively**:

- New optional fields can be introduced
- New conformance extensions can be defined
- New verification options can be added
- New examples and clarifications can be published

What does **not** change in minor versions:
- Required field definitions
- Required field types
- Conformance level requirements
- Validation rules for existing records

---

## Deprecation Cycle

When a field, requirement, or capability is to be removed or replaced, ODS uses a **deprecation cycle**:

### Phase 1: Marked Deprecated (Minor Release)
- The item is marked as deprecated in the specification
- Documentation explains the replacement (if any)
- Tooling continues to support it
- Validators emit deprecation warnings (optional)

### Phase 2: Migration Period (Minimum 12 Months)
- Both old and new approaches are valid
- Migration tooling is published
- Community is notified through release notes and direct communication
- Implementers have time to migrate

### Phase 3: Removed (Next Major Release)
- The deprecated item is removed
- The next major version no longer recognizes it
- Records using deprecated fields require migration to remain valid

**Total time from deprecation to removal: minimum 12 months, typically longer.**

---

## Major Version Migrations

Crossing a major version (1.x → 2.0) is the only time backward compatibility may be broken.

When this happens:

1. **RFC review** — All breaking changes are reviewed publicly
2. **Advance notice** — At least 6 months before the major release
3. **Migration guide** — Step-by-step migration documentation published with the release
4. **Tooling** — Automated migration tools where feasible
5. **Coexistence** — Both major versions remain valid during transition periods
6. **Long support** — The previous major version continues to receive security and clarification updates for at least 18 months

The Foundation treats major version transitions as serious commitments. They are rare and never undertaken lightly.

---

## What Implementers Can Rely On

If you implement ODS v1.0 today:

✅ Records you produce will be valid for the entire v1.x lifecycle
✅ Your implementation will remain conformant at its declared level
✅ You will have at least 12 months notice before any deprecated capability is removed
✅ Major version transitions will come with migration tooling and guides
✅ The schema validator in the repository will remain compatible with all v1.x records

---

## What Implementers Should Plan For

If you implement ODS v1.0 today:

⚠️ New optional fields may appear in minor releases — your implementation can choose to adopt them or ignore them
⚠️ Tooling and ecosystem capabilities will grow — staying current is recommended but not required
⚠️ A future v2.0 will eventually arrive, with migration support — plan for it as part of long-term operations

---

## Security Updates

Security-related changes that require breaking compatibility (e.g., a fundamentally insecure construction that must be deprecated quickly) follow an **expedited deprecation cycle**:

- Immediate disclosure to implementers
- Reduced migration window (3-6 months instead of 12)
- Strong public communication

These exceptions are extremely rare and only invoked when the alternative is leaving implementers exposed.

---

## See Also

- [VERSIONING.md](./VERSIONING.md) — version numbering policy
- [GOVERNANCE.md](./GOVERNANCE.md) — how decisions are made
- [SECURITY.md](./SECURITY.md) — security policy and reporting
- [ROADMAP.md](./ROADMAP.md) — what's coming next
