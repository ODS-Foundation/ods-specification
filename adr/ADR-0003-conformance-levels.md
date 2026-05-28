# ADR-0003: Conformance Levels — Basic / Standard / Full

- **Status**: Accepted (retrospective)
- **Date**: 2025 (during CONFORMANCE.md authoring)
- **Documented**: 2026-05-26
- **Retrospective**: true
- **Decision makers**: Steward + Council
- **Supersedes**: N/A (foundational decision)

## Context

ODS as a standard needs to balance two pressures that pull in opposite directions:

- **Low barrier to entry**: so adopters can start with minimal infrastructure, growing into the standard over time.
- **Rigorous audit assurance**: so a conformance claim means something specific to external auditors and regulators.

A single conformance bar would either gate out small adopters (if set high) or weaken the standard's claims (if set low). Setting it low means any system producing JSON resembling ODS records could claim conformance, devaluing the claim. Setting it high means only large institutional adopters with complete audit infrastructure can claim conformance, excluding the long tail of practitioners who would otherwise contribute to the standard's adoption.

Three-level structure was identified as the right pattern, matching how other mature standards handle the same tension (HTTP/2 conformance levels, WCAG accessibility levels A/AA/AAA, ISO standards with conformance profiles).

## Decision

ODS defines three conformance levels for adopting systems:

- **Basic**: produces records that validate against ODS Core schema; minimum compliance with field semantics.
- **Standard**: Basic + correct implementation of immutability (per ADR-0002), `parent_id` linkage semantics, and audit trail completeness within declared scope.
- **Full**: Standard + cryptographic integrity (hash chains over records), comprehensive missing-record fault handling (per CONFORMANCE.md §Operational Stance), and formal external audit verification capability.

Adopters self-declare their level (per CONFORMANCE.md §Self-Declaration). The standard publishes the criteria for each level so external verification is possible.

## Alternatives Considered

1. **Single conformance level**: rejected — too rigid for tail adoption (if set high) or too loose for institutional credibility (if set low). Fails to address the underlying tension.
2. **Continuous conformance score (0-100%)**: rejected — adopters would game scores; auditors prefer discrete levels for clear, defensible claims.
3. **Two levels (Basic + Full)**: considered — but no middle ground for adopters who implement immutability discipline without yet adopting cryptographic infrastructure.
4. **Four or more levels**: considered — increases cognitive load on adopters and adds complexity to verification without proportional benefit.
5. **Three levels (adopted)**: matches mature standards practice (HTTP, WCAG, ISO); proven balance of expressiveness and clarity.

## Consequences

### Positive

- Adoption ramp is clear: small adopters start at Basic, grow to Standard, mature to Full.
- Honest claims become possible: "ODS Standard conformance" means a specific set of properties.
- Verification clarity: external auditors can verify level claims unambiguously against published criteria.
- The middle level (Standard) anchors most institutional adoption.

### Negative

- Three levels increase documentation burden (each needs explicit criteria, edge cases, examples).
- Adopters must choose level honestly; loose self-declarations can devalue the standard if not policed.
- Future pressure to add more levels (resistable if Council holds discipline).

### Neutral

- Existing adopters need to declare a level at adoption time; one-time onboarding cost.

## Implementation

- CONFORMANCE.md §Core Conformance Levels (Basic / Standard / Full definitions)
- CONFORMANCE.md §Self-Declaration (declaration format)
- CONFORMANCE.md §Why Three Levels (rationale section)
- Validator does not yet enforce level claims at machine level (future tooling tracked in BACKLOG)

## Related

- ADR-0001 (Core + Profiles Separation): Profile Conformance is orthogonal to Core levels
- ADR-0002 (Immutability): required for Standard and Full
- CONFORMANCE.md (authoritative level definitions)
- CONFORMANCE.md §Operational Stance on Missing Records: behavioral requirement for Standard+

## Validation

A claim of "ODS Standard conformance" by an adopter should be verifiable by reviewing the adopter's records: do they validate against Core schema? Do they implement `parent_id` correctly? Is their audit trail complete within declared scope? An external auditor with access to the standard's published level criteria can answer these without ambiguity.
