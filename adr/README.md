# Architectural Decision Records (ADRs)

This directory contains Architectural Decision Records for ODS-Foundation. ADRs document significant architectural and governance decisions with their context, alternatives considered, decision rationale, and consequences. The pattern follows Michael Nygard's original ADR proposal and the MADR (Markdown Architectural Decision Records) format.

## Purpose

ADRs serve four institutional functions:

1. **Immutable decision provenance**: once an ADR is `Accepted`, its contents are not modified. Superseding decisions create new ADRs that explicitly cite the one they replace.
2. **Onboarding for new contributors**: someone joining ODS-Foundation can read the ADR sequence and understand why the architecture looks the way it does.
3. **External auditability**: auditors, regulators, and standards bodies can verify that significant decisions were deliberated, not accidental.
4. **Counterfactual record**: each ADR documents the alternatives considered, preserving the reasoning that led to the decision.

## Format

Each ADR is a Markdown file named `ADR-XXXX-short-slug.md`, where `XXXX` is a zero-padded sequential identifier. Use `template.md` as the starting point for new ADRs.

## Status Lifecycle

- `Proposed`: under Council deliberation; content may change
- `Accepted`: ratified; content frozen; future changes require superseding ADR
- `Superseded`: replaced by a later ADR; original content remains, header links to successor
- `Deprecated`: no longer in effect but not yet superseded; rare

## Retrospective ADRs

The initial corpus is retrospective — documenting significant decisions made before this practice was established. Retrospective ADRs are marked with `Retrospective: true` in their header and dated both to the original decision and to the documentation date.

Going forward, significant architectural decisions are documented via ADR before implementation.

## Index

| ID | Title | Status |
|---|---|---|
| ADR-0001 | Architecture: Core + Profiles Separation | Accepted (retrospective) |
| ADR-0002 | Immutability via Append-Only + parent_id | Accepted (retrospective) |
| ADR-0003 | Conformance Levels — Basic / Standard / Full | Accepted (retrospective) |
| ADR-0004 | Profile Reservation Policy + Out-of-Scope List | Accepted (retrospective) |
| ADR-0005 | Foundation-Style Governance Model | Accepted (retrospective) |

The retrospective corpus documenting major ODS-Foundation architectural and governance decisions from inception through v2.0 is now complete. Going forward, significant architectural decisions are documented via ADR before implementation, not retrospectively.
