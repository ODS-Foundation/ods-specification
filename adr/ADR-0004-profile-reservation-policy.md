# ADR-0004: Profile Reservation Policy + Out-of-Scope List

- **Status**: Accepted (retrospective)
- **Date**: 2025 (during v2.0 profile architecture work)
- **Documented**: 2026-05-26
- **Retrospective**: true
- **Decision makers**: Steward + Council
- **Supersedes**: N/A (foundational decision following ADR-0001)

## Context

ODS Core is domain-neutral by design (per ADR-0001). Domain extension happens via Profiles. Without governance over the Profile namespace, two failure modes emerge:

1. **Name conflicts**: two independent working groups both create profiles named (e.g.) "ODS-Healthcare," producing incompatible vocabularies and breaking interoperability for adopters who claim Healthcare conformance.
2. **Scope creep**: profiles claim namespaces inappropriate for their actual content (e.g., a tax-software-specific schema published as "ODS-Government"), diluting the meaning of profile names and confusing adopters in adjacent domains.

Mature standards handle this via reservation policy (IETF for media types, ICANN for TLDs, HL7 for FHIR Implementation Guides). ODS needs an explicit policy covering: which profile namespaces are reserved (and for whom), which are explicitly out-of-scope (won't ever be Profile namespaces), how new reservations are granted, and what expiry conditions apply.

## Decision

ODS-Foundation maintains, in PROFILES.md:

1. **Reserved Profile Namespace**: a list of profile names reserved for eventual authoring by domain working groups. As of v2.0, six profiles are reserved: ODS-Healthcare, ODS-Insurance, ODS-Government, ODS-Cybersecurity, ODS-Hiring, ODS-Supply-Chain. Reservations include an 18-month expiry; if no working group emerges to author within that window, the reservation lapses and the namespace becomes available for re-reservation or alternative use.

2. **Out-of-Scope List**: a list of namespaces explicitly NOT to be used as Profiles, documented to prevent name collision with similar-sounding but conceptually different efforts (third-party tools, general-purpose vocabularies, ODS-Foundation projects that are not profiles).

3. **Reservation Process**: new reservation requires Council acknowledgment of (a) domain coherence (the profile would cover a coherent decision domain), (b) regulatory tailwind or practitioner pull (there is external demand), and (c) commitment of at least one credible domain expert to author the profile.

## Alternatives Considered

1. **Free-for-all (no reservation policy)**: rejected — guarantees name conflicts and chaos at scale; first major adopter conflict would damage standard credibility.
2. **Closed list of profiles, no future expansion**: rejected — defeats the purpose of being a multi-domain standard; precludes growth as new regulated decision domains emerge.
3. **Profile creation requires Foundation membership fee**: rejected — incompatible with open standard governance and would signal vendor-led structure (the opposite of ADR-0005).
4. **Reservation without expiry (permanent claims)**: rejected — allows squatting on namespaces by parties who never deliver. Permanent reservations also make the registry unmaintainable over decade timescales.
5. **Reservation with expiry (adopted)**: balances openness with discipline; lapsing reservations prevent permanent squatting while giving working groups reasonable time to form and author.

## Consequences

### Positive

- Profile namespace is governed; name conflicts are prevented structurally.
- Strategic signaling: which domains the standard cares about (and which it explicitly doesn't) is publicly visible.
- Expiry forces working group emergence or namespace release — no permanent dead claims.
- Out-of-Scope list prevents accidental adjacent-meaning collisions (e.g., a third-party "ODS" with different scope).

### Negative

- Council maintenance burden (reviewing reservation requests, tracking expiries, processing lapses).
- Potential gatekeeping perception (mitigated by published criteria and transparent process).
- Lapsed reservations create churn if working groups partially form then dissolve.

### Neutral

- First adopters in a domain may push for premature reservation; Council must hold the line on criteria. This is governance discipline, not a defect.

## Implementation

- PROFILES.md §Registry (Authored profiles + Reserved profiles tables)
- PROFILES.md §Out of Scope (explicit list with rationale)
- PROFILES.md §Profile Authoring Bar (criteria for reservation and authoring)
- 18-month expiry codified in PROFILES.md
- `profiles/registry.json` provides machine-readable view (future BACKLOG: full machine-readable reservation lifecycle)

## Related

- ADR-0001 (Core + Profiles Separation): this policy operates on the Profiles layer
- PROFILES.md (authoritative registry and policies)
- Future BACKLOG candidate: machine-readable reservation expiry tracking

## Validation

The PROFILES.md file contains the authoritative registry. Any profile name in active use (in records, in tooling, in adopter documentation) should appear in either Authored or Reserved sections. Any name in the Out-of-Scope list must not appear as a Profile in any conformance claim. An auditor verifying the policy reviews the PROFILES.md state and the timestamps of reservation entries against the 18-month expiry.
