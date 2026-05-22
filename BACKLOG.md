# ODS Specification — Backlog

This file tracks specification gaps, latent design issues, and candidate RFCs identified during ODS-Foundation work but not addressed in the current published version. Inclusion here is acknowledgment, not commitment: items may be addressed in a future minor version, deferred indefinitely, or rejected after deeper analysis.

The file follows the same transparency principle as the rest of ODS-Foundation: known limitations are documented publicly rather than hidden.

## Format

Each entry includes:
- **Identified**: date and context of identification
- **Description**: what is missing or wrong
- **Candidate version**: earliest version that could plausibly address it
- **Status**: `open`, `under-discussion`, `accepted-for-rfc`, `deferred`, `rejected`

## Gaps

### BACKLOG-001 — `identity.model_name` field for namespaced model identifiers

- **Identified**: 2026-05-11, during initialization of the ORPI Steward journal practice
- **Description**: ODS Core v2 `identity.model_version` enforces a pure SemVer pattern (`^v?\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$`). Users who need to identify which model or process produced a record (distinct from its version) must currently encode the model name into the pre-release identifier (e.g., `v1.0.0-ORPI-Steward`). This pollutes the semantic of SemVer pre-release identifiers, which are intended for alpha/beta/rc designation, not namespacing. A proper solution is to add an optional `identity.model_name` field (free-form string) and let `model_version` remain pure SemVer.
- **Candidate version**: v2.2.0 (additive, backward-compatible field addition)
- **Status**: open

### BACKLOG-002 — `references[]` field for explicit relations between records

- **Identified**: 2026-05-20, during logging of partial-outcome attestations in the ORPI Steward journal
- **Description**: ODS Core v2 provides `parent_id` as a top-level field semantically designed for OUTCOME records pointing to the DECISION they are outcomes of. Records that need to express other relations between records (e.g., a DECISION that clarifies, extends, or supersedes a prior DECISION; an attestation that references multiple parents) currently overload `parent_id` beyond its original intent. A proper solution is an optional `references[]` array, where each entry is `{ "record_id": "<uuid>", "relation": "<enum>" }` with enum values such as `outcomes_of`, `extends`, `supersedes`, `clarifies`, `attests_partial_outcome_of`. The existing `parent_id` would remain for backward compatibility and be defined as semantically equivalent to a single `references` entry with `relation: outcomes_of`.
- **Candidate version**: v2.2.0 (additive, backward-compatible field addition)
- **Status**: open
