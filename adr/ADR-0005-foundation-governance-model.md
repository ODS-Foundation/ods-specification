# ADR-0005: Foundation-Style Governance Model

- **Status**: Accepted (retrospective)
- **Date**: 2025-2026 (developed in practice; codified retrospectively)
- **Documented**: 2026-05-26
- **Retrospective**: true
- **Decision makers**: Steward
- **Supersedes**: N/A (foundational decision)

## Context

A standard's credibility depends substantially on its governance model. Vendor-led standards (standards owned by a single commercial entity) are systematically discounted by potential adopters, regulators, and partner standards bodies because the perceived risk of self-dealing is high. Open standards bodies (IETF, W3C, HL7, ISO) earn credibility through governance transparency and independence from any single commercial interest.

ODS-Foundation, at its current stage (one Steward, no working groups yet authored, early outreach to domain experts), faced several governance options:

1. Single vendor ownership (one commercial entity owns and controls the spec)
2. Founder-only governance (the Steward decides everything unilaterally with no deliberative process)
3. Foundation-style independent body (Steward + advisory Council + community contributors + future working groups)
4. Foundation under an existing org (Apache, Linux Foundation, OASIS, etc.)

Option 4 is premature: established Foundations host mature projects with critical mass and substantial community traction, not nascent standards. Pursuing Foundation membership before ODS has working groups and adopters would be a category error. Option 1 is fatal to credibility — institutional adopters discount vendor-led standards heavily. Option 2 doesn't scale beyond Steward bandwidth and produces no auditable deliberation trail.

The Steward + Council + Operator pattern, developed in practice over 2026 work, provides the scaffolding for option 3 at solo-founder scale. It is governance preparation for eventual Foundation maturation rather than a final state.

## Decision

ODS-Foundation operates as an independent standards body with explicit governance roles:

- **Steward**: holder of governance authority; single point of final decision; publicly identified.
- **Council**: deliberative function; produces design memos, reviews proposals, surfaces tradeoffs and counterfactuals. Can be a single substantive advisor (currently an AI advisor used by the Steward) or multi-member (future state as the project matures). Council outputs are auditable artifacts (design memos, ADRs, review comments).
- **Operator**: execution function; applies authorized changes to artifacts; reports actions taken; never autonomous on architectural or normative changes.
- **Working Groups** (future): domain-specific authoring bodies for Profiles; chartered by Steward + Council; produce profile specifications and associated documentation.

Constraint: ODS-Foundation MUST NOT operate as a vendor-led entity. Specifically:

- No single commercial entity holds privileged rights to the spec, the schema, or any normative artifact.
- All normative changes proceed through public governance visible in the repository.
- Reference implementations may be commercial; the specification itself is open under the project's license.

## Alternatives Considered

1. **Vendor-led standard**: rejected — incompatible with credibility for institutional adoption, partner standards bodies, or regulator engagement.
2. **Solo Steward without Council**: rejected — doesn't scale, doesn't produce auditable deliberation trail; quality of decisions degrades without external review pressure.
3. **Pre-mature Foundation membership (Apache, Linux Foundation, OASIS, etc.)**: rejected — Foundations host mature projects with critical mass. Pursue if and when ODS reaches scale (adopters, working groups, sustained contribution velocity).
4. **Open consortium without Steward authority**: rejected — committee paralysis is common at early stage; the project needs a backstop decision-maker until critical mass forms.
5. **Steward + Council + Operator pattern (adopted)**: balances authority (Steward), deliberation (Council), and execution (Operator); scales by expanding Council membership when working groups emerge, and by graduating to Foundation membership when external critical mass is reached.

## Consequences

### Positive

- Credibility as an independent standards body (mirrors HL7, IETF, W3C governance patterns).
- Clear roles avoid confusion in contributions and reduce friction in governance.
- Audit trail of decisions: Council deliberations produce design memos and ADRs that are public.
- Pathway to scaling is explicit (Council expands; working groups form; Foundation membership becomes feasible).

### Negative

- Solo Steward at current stage is a bottleneck (mitigation: Council can be a substantive single-advisor like an AI collaborator during early phase; multiple human advisors as project matures).
- Foundation maturation requires sustained discipline; can decay if Steward attention lapses.
- Bus-factor risk: Steward continuity is single point of failure (mitigation: ADR practice + public journal + audit-grade artifacts make handoff possible to a successor Steward).

### Neutral

- The current configuration (one human Steward, an AI advisor as Council, an AI Operator) is unusual in standards governance but well-precedented in solo-founder + AI-collaborator patterns emerging in 2025-2026.

## Implementation

- Repositories are public: `ods-specification`, `orpi-journal`, etc.
- Steward identity is public.
- Council/Operator pattern is documented in CLAUDE.md (each repo).
- Governance artifacts (BACKLOG entries, ADRs, RFCs, design memos) are all public and traceable in git history.
- License is open (Apache 2.0) for all normative artifacts.

## Related

- ADR-0001, ADR-0002, ADR-0003, ADR-0004 (all governance and architectural artifacts of this project)
- CLAUDE.md (operational role definitions for Operator)
- Future ADR candidate: Working Group charter process (when first working group forms)
- Future ADR candidate: Council expansion process (multi-member Council)

## Validation

External observers (regulators, potential TC members, sponsor candidates) reading the repository should be able to: (a) identify the Steward and contact path, (b) find the Council's substantive contributions in design memos and ADRs, (c) trace any change in the repository to a documented governance event (BACKLOG entry, RFC, design memo, ADR, or commit message referencing one of these). Absence of any of these is a governance failure visible in repo state.
