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

### BACKLOG-003 — Counterfactual provenance fields (`methodology`, `evidence_quality`)

- **Identified**: 2026-05-26, via Council re-analysis of pre-spec architectural notes
- **Description**: ODS Core v2 `counterfactuals[]` items contain only `alternative_action` and `expected_outcome`. Records lack any indication of how the expected_outcome value was derived (expert estimate, observed analog, simulated, modeled via causal inference) or the epistemic quality of that derivation. Regulatory auditors evaluating ODS records under frameworks requiring "explainability of considered alternatives" (e.g., EU AI Act Article 13/14) need this distinction to assess record credibility. Candidate additions: `counterfactuals[].methodology` (enum, controlled vocabulary including but not limited to `propensity_score_matching`, `synthetic_control`, `observed_similar_case`, `simulation`, `expert_consensus`, `assumed`) and `counterfactuals[].evidence_quality` (enum: `observed | inferred | simulated | expert_estimate | assumed`).
- **Candidate version**: v2.1
- **Status**: `open`

### BACKLOG-004 — `governance.generation_method` field

- **Identified**: 2026-05-26
- **Description**: ODS Core v2 has no field indicating how a record was produced. Distinguishing manual entry, semi-automated production (system + human review), fully automated emission (system action with logged justification), and simulated synthesis (synthetic for testing/training) is necessary for downstream conformance assessment. Auditors and verifiers should be able to filter or weight records by generation pathway. Candidate field: `governance.generation_method` (enum: `manual | semi_automated | automated | simulated`).
- **Candidate version**: v2.1
- **Status**: `open`

### BACKLOG-005 — `cognition.actionable_until_utc` field for time-bounded decisions

- **Identified**: 2026-05-26
- **Description**: Many high-stakes decisions are valid only within a specific time window — after which the optimal choice changes or the decision becomes moot. ODS Core v2 captures decision timestamp (`timestamp_utc`) but has no field for time-criticality. An optional `cognition.actionable_until_utc` (ISO-8601 datetime) would let records express that the documented decision should be enacted before that point, enabling downstream measurement of decision-to-action latency vs. allowed window. Useful for fraud detection, healthcare emergency, supply chain disruption response, incident response, and similar time-sensitive domains.
- **Candidate version**: v2.1
- **Status**: `open`

### BACKLOG-006 — Formal deprecation lifecycle with expiry enforcement

- **Identified**: 2026-05-26
- **Description**: ODS currently deprecates record formats and fields (e.g., v1.x → v2.0 transition documented in VERSIONING.md) without a formal lifetime policy. A deprecated feature can technically remain in use indefinitely. Mature standards bodies (SemVer ecosystem, Apache, IETF) typically require expiry windows for deprecations to force migration. Candidate additions to VERSIONING.md: (a) machine-readable registry of deprecated features in `DEPRECATIONS.json` with fields `feature_id`, `deprecated_in_version`, `removal_target_version`, `migration_path_url`; (b) CI gate that fails if a `removal_target_version` is reached but the feature is still present in normative artifacts; (c) maximum lifetime cap as policy (proposed: 3 minor versions or 18 months from deprecation announcement, whichever is later).
- **Candidate version**: v2.1 (governance addition, non-breaking)
- **Status**: `open`

### BACKLOG-007 — Audit-trail deviations in PR #1 (gitleaks secret scanning)

- **Identified**: 2026-06-07, during merge of PR #1 (`chore/secret-scanning`, merge commit `38d291e`) — the repository `CLAUDE.md` was not in the Operator's context until after the merge (Operator working directory was `~`, not the repo root), so the L2 operations were executed against the Steward's explicit shell instructions without prior reference to the documented governance discipline.
- **Description**: Two deviations from the Operator discipline in `CLAUDE.md` were recorded in permanent history and surfaced honestly per the repository's honesty principle. (1) **Commit/merge message convention**: `CLAUDE.md` requires every L2 commit and merge message to end with the authorizing Council session reference; the three commits (`ecbf964`, `694cd4d`, `7be8aa0`) end with a `Co-Authored-By` trailer instead, and the merge commit (`38d291e`) carries GitHub's autogenerated message. (2) **Authorization model**: L2 operations are documented to require per-operation Council authorization; here they were authorized by direct Steward shell instruction, with no Council session record in-conversation. Compliant aspects, for the record: no normative artifact was touched (the changed files — `.pre-commit-config.yaml`, `.github/workflows/gitleaks.yml` — are non-normative, so no design memo was required); no direct commit to `main`; no force-push or history rewrite; and the merge preserved a real 2-parent merge commit (`--no-ff` satisfied). Remediating the message convention would require rewriting pushed history (L3, forbidden to the Operator); it is therefore left for the Steward to decide. This entry exists to preserve an auditable trace of the deviation rather than to silently absorb it.
- **Candidate version**: n/a (process/governance finding, not a specification gap)
- **Status**: `open`
