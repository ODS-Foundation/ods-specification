# ODS Profile Registry

Profiles extend ODS Core with domain-specific field requirements. Each profile has a canonical namespace, an independent version history, and a status tracked in this registry.

This document is normative. Claims of profile conformance are evaluated against this registry.

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| `reserved` | Namespace is registered but no profile schema exists. Conformance claims against reserved profiles are PROHIBITED. |
| `under-review` | Profile RFC is active. Schema is in draft and subject to change. Not yet stable for production use. |
| `authored` | Profile has met the authoring bar (see §Profile Authoring Bar) and is stable for production use. |
| `deprecated` | Profile has been superseded. Existing implementations remain valid; new implementations should migrate. |

---

## Registry

| Profile | Status | Maintainer | Core Dependency | RFC | First Published | Latest |
|---------|--------|------------|-----------------|-----|-----------------|--------|
| ODS-Finance/v1 | `authored` | ODS Foundation | ODS Core v2 | Migration — Council Resolution 2026-05-09 | 2026-05-09 | v1.0.0 |
| ODS-Healthcare | `reserved` | — | — | — | — | — |
| ODS-Insurance | `reserved` | — | — | — | — | — |
| ODS-Government | `reserved` | — | — | — | — | — |
| ODS-Cybersecurity | `reserved` | — | — | — | — | — |
| ODS-Hiring | `reserved` | — | — | — | — | — |
| ODS-Supply-Chain | `reserved` | — | — | — | — | — |

> **Reserved profiles:** No implementation may claim conformance with a profile whose status is `reserved`. Conformance claims require a profile with status `authored` or higher. Validators MUST emit an error (not a warning) when they encounter a `profile` field referencing a reserved namespace.

---

## Out of Scope for v2.0

The following domain namespaces have been explicitly considered and excluded from the v2.0 reserved registry. They are not prohibited from future authoring — any community may propose them via RFC for v2.x. Their absence from the v2.0 registry is a deliberate Council decision to prevent premature RFCs during v2.0 stabilization.

| Namespace | Reason for Exclusion |
|-----------|---------------------|
| ODS-Legal / ODS-Judicial | Politically sensitive framing risks; defer to community-led RFC if/when appropriate |
| ODS-Education | Insufficient regulatory pressure for v2.0 prioritization |
| ODS-Energy | Critical infrastructure governance not yet aligned with ODS scope |
| ODS-Manufacturing | Lower regulatory pressure for AI decision audit; defer |

Communities interested in any of the above are welcome to propose RFCs for v2.x consideration.

---

## Profile Field Format

The `profile` field in a record stores the profile namespace and major version:

```
"profile": "ODS-Finance/v1"
```

Major version only. Minor and patch versions are not stored in the record. Auditors resolve the precise version in effect for a given `timestamp_utc` by consulting this registry, which records publication dates for each semver entry.

---

## Conformance Declaration Format

Conformance is declared independently for core and profile:

> "ODS Core v2 Standard + ODS-Finance v1 Full"

A core-only conformance declaration (for governance-only implementations) is valid:

> "ODS Core v2 Basic"

A profile conformance level may not exceed the core conformance level. See [CONFORMANCE.md](./CONFORMANCE.md) for the full justification.

---

## Profile Authoring Bar

The bar for promoting a profile from `reserved` or `under-review` to `authored` status operates in two phases:

### Early-stage bar (active until 2028-05-08 or ODS Core v3.0, whichever comes first)

A profile may reach `authored` status upon meeting one of:
- 1 organization with a documented production implementation, OR
- 1 academic working group with a published technical report, OR
- 2 organizations with documented intent to implement (letters of intent accepted)

Migration profiles (those whose content is migrated from prior ODS Core versions, e.g., ODS-Finance/v1 in v2.0) are exempt from this bar — they reach `authored` status by Council resolution at the time of the architectural migration.

### Mature bar (active from 2028-05-08 or ODS Core v3.0, whichever comes first)

A profile may reach `authored` status upon:
- 3 organizations with committed production implementations

The transition date is normative and not subject to Council re-interpretation. It lapses automatically.

### Reservation expiry

Reservations lapse 18 months after registration without progression to `under-review`, unless explicitly extended by Council vote. Lapsed reservations return the namespace to the unregistered pool.

---

## Backward Compatibility Within a Profile Major Version

Within a profile major version (e.g., `ODS-Finance/v1`), the following are PERMITTED:

- Adding new optional fields
- Relaxing constraints on existing fields (e.g., removing a `minimum` bound)
- Adding new valid values to an `enum` that is not used as a discriminator
- Adding new optional sections

The following are PROHIBITED within a profile major version:

- Removing required fields
- Adding new required fields (this requires a major version increment)
- Changing the type of an existing field
- Tightening constraints on existing fields (e.g., adding `minimum`, reducing `maxLength`)
- Renaming fields
- Changing the semantics of a field in a way that breaks existing record interpretation

A major version increment is REQUIRED for any prohibited change, accompanied by a migration RFC. Profile major version increments are independent of ODS Core major version increments.

---

## Contributing a Profile

To register a new profile namespace:

1. Open an RFC via GitHub issue using the profile RFC template
2. Namespace is reserved upon RFC acceptance
3. Profile schema and documentation submitted per RFC
4. Profile promoted to `authored` upon meeting the authoring bar

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full RFC process.
