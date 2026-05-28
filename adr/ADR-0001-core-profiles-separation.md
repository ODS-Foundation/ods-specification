# ADR-0001: Architecture — Core + Profiles Separation

- **Status**: Accepted (retrospective)
- **Date**: 2025 (during v1.x → v2.0 audit work; precise dates in VERSIONING.md changelog)
- **Documented**: 2026-05-26
- **Retrospective**: true
- **Decision makers**: Steward + Council
- **Supersedes**: ODS v1.x monolithic schema architecture

## Context

ODS v1.x had a monolithic schema mixing two categories of fields:

1. **Domain-neutral decision fields**: `record_type`, `identity`, `cognition`, `counterfactuals`, `governance` — applicable to any decision in any domain.
2. **Finance-specific fields**: `action_type` with finance vocabulary (BUY/SELL/HOLD), `capital_at_risk_bps`, `regime_state` — applicable only to financial decisions.

Audit findings during the v1.x → v2.0 work identified this as structurally incompatible with the standard's claim of being domain-neutral. The mixed architecture had several concrete problems:

- **Adoption blocker outside finance**: a Healthcare, Insurance, or Government practitioner reading the v1.x schema would see finance vocabulary as required or central, signaling the standard was finance-only despite naming itself "Operational Decision Standard."
- **No extension model**: profile-based domain extension was impossible without breaking the schema, because new domains would need to either fit into finance-shaped fields or modify the core.
- **Implementer confusion**: nothing in v1.x distinguished what was universal from what was finance-specific. Implementers in other domains would either reject the standard or shoehorn their domain into finance vocabulary.
- **Cross-domain conformance verification impossible**: a Healthcare adopter and a Finance adopter could not be evaluated against the same conformance criteria because the schema mixed concerns.

## Decision

Refactor ODS into two architectural layers:

1. **ODS Core** (v2.0+): domain-neutral, minimal, stable. Contains only fields that apply universally across all decision domains. The Core schema is the kernel — every conformant record validates against it first.

2. **ODS Profiles**: domain-specific extensions. Each profile is an authored or reserved namespace that adds domain-specific fields. The first authored profile is ODS-Finance/v1, which contains the migrated finance fields from v1.x.

Constraints enforced by this architecture:

- ODS Core MUST NOT contain domain-specific vocabulary or fields.
- Profiles MUST NOT contradict Core invariants (immutability, schema validation, audit trail).
- Records MUST validate against Core first; profile validation is additional.
- One record MAY apply at most one profile (One Profile Per Record rule).

## Alternatives Considered

1. **Keep monolithic schema, add Healthcare/Insurance/etc. fields directly to Core**: rejected because Core would grow unboundedly and lose claim to domain-neutrality. Schema would become a union of all domains' needs, making it unwieldy and incoherent.

2. **Multiple independent standards (ODS-Finance, ODS-Healthcare, etc.) with no shared core**: rejected because it would lose the value of cross-domain governance (audit trail format, counterfactual structure, immutability semantics) and force each domain to reinvent these.

3. **Single schema with optional domain fields**: rejected because "optional domain fields" still encodes assumptions about which domains exist; the same problem as alternative 1 in a softer form.

4. **Core + Profiles separation (adopted)**: matches the architectural pattern of HL7 FHIR (Resources + Implementation Guides), OpenAPI (core spec + extensions), Kubernetes (Kind/apiVersion + typed extensions), and other mature standards. Proven extension model.

## Consequences

### Positive

- Multi-domain adoption is structurally possible.
- Reserved profile namespace (Healthcare, Insurance, Government, Cybersecurity, Hiring, Supply-Chain) signals architectural breadth from day one of v2.0.
- Clear extension model for domain working groups.
- Auditable kernel + auditable profile extensions, each verifiable independently.
- Aligns with mature standards architecture patterns.

### Negative

- v1.x deprecation requires migration path for any existing v1.x adopters.
- Additional architectural layer increases conceptual complexity for first-time readers.
- Profile authoring requires sustained governance discipline (Working Groups, RFC process per profile).
- Reserved-but-unauthored profiles create expectation of eventual authoring.

### Neutral

- Existing finance-focused implementations must migrate from monolithic v1.x to Core + ODS-Finance/v1, but the migration is mechanical (no semantic changes to finance fields).

## Implementation

- ODS Core v2.0 shipped (SPECIFICATION.md, `schema/ods_record_v2.json`).
- ODS-Finance/v1 shipped as first authored profile (`profiles/ods-finance-v1.json`).
- Six reserved profiles declared in PROFILES.md: ODS-Healthcare, ODS-Insurance, ODS-Government, ODS-Cybersecurity, ODS-Hiring, ODS-Supply-Chain.
- Out-of-Scope namespaces explicitly listed in PROFILES.md to prevent name collision.
- Validator (`validator/validate.py`) enforces Core validation first, then optional profile validation.

## Related

- SPECIFICATION.md §3 (Record envelope), §8 (Profile extension mechanism)
- PROFILES.md (authoring bar, registry, reservation policy)
- VERSIONING.md (v1.x → v2.0 changelog and migration notes)
- Future ADR-0002 (candidate): Immutability via append-only + parent_id
- Future ADR-0003 (candidate): Conformance levels Basic/Standard/Full
- Future ADR-0004 (candidate): Profile reservation policy + Out-of-Scope list
- Future ADR-0005 (candidate): Foundation-style governance model

## Validation

This decision is validated by the present state of the repo: a Core schema that contains no finance vocabulary, an ODS-Finance/v1 profile that contains all migrated finance fields, and a PROFILES.md registry that distinguishes authored from reserved profile names. Any future architectural change that violates the Core/Profiles separation MUST proceed through a superseding ADR.
