# ODS Architecture

- **Status**: Descriptive / non-normative
- **Audience**: Implementers, profile authors, auditors, potential contributors
- **Last updated**: 2026-05-26

This document describes the architecture of the Operational Decision Standard: how it is structured, what dependency rules govern its layers, what invariants hold across all versions, and what the architecture treats as failure. It is descriptive, not normative — the normative content lives in `SPECIFICATION.md`, `CONFORMANCE.md`, and `PROFILES.md`. This document explains the reasoning behind that structure.

A system is defined as much by what it cannot do as by what it can. This document emphasizes the constraints — the invariants and the prohibited dependency directions — because those are what make ODS auditable and durable.

## 1. System Purpose

ODS exists to make high-stakes decisions auditable. A conformant ODS record captures not just what was decided, but the reasoning, the alternatives considered, the confidence held, and the governance trail — in a structured, immutable, verifiable form.

### What ODS is

- A schema for decision records (Core)
- An extension mechanism for domain-specific decision vocabularies (Profiles)
- A set of conformance levels for adopters to declare against
- A governance model for evolving the standard

### What ODS is not

- **Not a decision-making engine.** ODS records decisions; it does not make them.
- **Not a logging library.** ODS is a schema and a set of disciplines, not an implementation.
- **Not a database.** ODS does not prescribe storage; it prescribes record structure and semantics.
- **Not domain-specific.** Core is domain-neutral; domain specificity lives in Profiles.

The distinction between recording decisions and making them is fundamental. ODS is the audit layer, not the decision layer. A system that makes decisions may emit ODS records; the records are the ODS-conformant artifact, not the decision logic.

## 2. The Layered Model

ODS has three architectural layers with strict, one-way dependency directions.

### Layer 1: Core

The domain-neutral kernel. Defines the universal record envelope: `record_type`, `identity`, `cognition`, `counterfactuals`, `governance`, `parent_id`. Every conformant record validates against Core first. Core contains no domain-specific vocabulary.

### Layer 2: Profiles

Domain-specific extensions. Each profile (authored or reserved) adds vocabulary for a specific decision domain — ODS-Finance defines trading action types; a future ODS-Healthcare would define clinical decision types. Profiles extend Core; they never modify it.

### Layer 3: Tooling

Validators, generators, viewers, and other software that consumes Core and Profiles. Tooling reads the schema and records; it does not define them.

### Dependency rules

The dependency direction is strict and one-way:
Tooling  --depends on-->  Profiles  --depends on-->  Core

- **Core depends on nothing.** It is the kernel.
- **Profiles depend on Core.** They extend it, constrained by its invariants.
- **Tooling depends on both.** It consumes them.

Reverse dependencies are prohibited:

- Core MUST NOT contain profile-specific vocabulary (would couple the kernel to a domain).
- Core MUST NOT depend on any tool's behavior (the schema is tool-independent).
- Profiles MUST NOT contradict Core invariants (a profile cannot make a Core-invalid record valid).

This is the same separation-of-concerns discipline found in HL7 FHIR (Resources + Implementation Guides), OpenAPI (core + extensions), and Kubernetes (Kind/apiVersion + typed extensions). See `adr/ADR-0001` for the decision rationale.

## 3. The Kernel Principle

ODS Core functions as a kernel: minimal, stable, and protected.

- **Minimal**: Core contains only fields that apply universally across all decision domains. Anything domain-specific belongs in a Profile.
- **Stable**: Core changes rarely and only through governance (RFCs, design memos, ADRs). Adopters and profile authors build on the assumption that Core is a fixed foundation.
- **Protected**: changes to Core face the highest scrutiny in the standard, because every record and every profile depends on it.

The kernel principle is why the v1.x → v2.0 refactor mattered (see `adr/ADR-0001`): v1.x had finance vocabulary in the kernel, coupling the foundation to one domain. Extracting it into ODS-Finance restored the kernel's domain-neutrality and made multi-domain adoption structurally possible.

A useful test for any proposed Core change: *does this apply to every decision domain, or only some?* If only some, it belongs in a Profile.

## 4. Architectural Invariants

Five properties hold across all versions of ODS. A change that violates any of them is not a normal evolution — it is a re-foundation, requiring a superseding ADR and broad governance review.

### Invariant 1: Records are immutable

Once committed, a record is never modified. Corrections happen via new records linked by `parent_id`. (See `adr/ADR-0002`.)

### Invariant 2: Core is domain-neutral

The kernel contains no domain-specific vocabulary. Domain specificity lives only in Profiles. (See `adr/ADR-0001`.)

### Invariant 3: Profiles cannot weaken Core

A profile may extend Core but may never make a Core-invalid record valid, nor remove a Core constraint. (See `adr/ADR-0001`, `adr/ADR-0004`.)

### Invariant 4: Audit trails are complete within declared scope

For any decision in an adopter's declared ODS scope, a record exists. A missing in-scope record is a fault, not a gap. (See `CONFORMANCE.md` §Operational Stance on Missing Records.)

### Invariant 5: Versioning preserves backward conformance

A minor version (v2.0 → v2.1) does not break records valid under the prior minor version. Breaking changes require a major version with a documented migration path. (See `VERSIONING.md`, `adr/ADR-0003`.)

These five invariants are the architectural contract. Implementers can build on them with confidence that they will not silently change.

## 5. Failure Modes

The architecture treats certain conditions as failures by design — making them visible rather than tolerable.

- **Missing in-scope record**: a fault equivalent to silent execution failure (Invariant 4). Not a data-quality issue.
- **Mutated record**: any post-commit change to a record is a fault, detectable via the immutability invariant and version-control history (Invariant 1).
- **Core coupled to a domain**: domain vocabulary appearing in Core is an architectural fault caught in review (Invariant 2).
- **Profile weakening Core**: a profile that makes Core-invalid records valid is an architectural fault caught in profile review (Invariant 3).
- **Silent breaking change**: a minor version that breaks prior-version records is a versioning fault (Invariant 5).

The design philosophy: silent failure is the enemy. The architecture's job is to convert what would be silent failures into loud, visible faults.

## 6. How the Architecture Evolves

ODS evolves through explicit governance, never through silent drift.

- **RFCs / design memos** propose changes to normative artifacts.
- **ADRs** document architectural and governance decisions, with their alternatives and consequences.
- **Versioning** (per `VERSIONING.md`) governs how changes ship: minor versions are additive and backward-compatible; major versions may break with documented migration.
- **Profiles** are added through the reservation and authoring process (`PROFILES.md`, `adr/ADR-0004`), not by modifying Core.

Any change to an architectural invariant (Section 4) is, by definition, a re-foundation event: it requires a superseding ADR and the highest level of governance scrutiny, because the invariants are what adopters build on.

## 7. Philosophy

A standard is defined more by what it cannot do than by what it can.

ODS's value comes from its constraints: records that cannot be silently changed, a kernel that cannot be coupled to one domain, profiles that cannot weaken the foundation, audit trails that cannot tolerate undeclared gaps, versions that cannot silently break what came before.

These constraints are not limitations to be worked around. They are the source of the assurance the standard provides. An adopter who fully internalizes the constraints produces decision records that withstand institutional and regulatory scrutiny — which is the entire point.

## Related

- `SPECIFICATION.md` — normative Core schema and field semantics
- `CONFORMANCE.md` — normative conformance levels and operational stances
- `PROFILES.md` — normative profile authoring and registry
- `VERSIONING.md` — normative version policy
- `BEST-PRACTICES.md` — non-normative implementation guidance
- `adr/ADR-0001` through `adr/ADR-0005` — architectural and governance decisions
