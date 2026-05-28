# ADR-0002: Immutability via Append-Only + parent_id

- **Status**: Accepted (retrospective)
- **Date**: 2025 (early v1.x design through v2.0 codification)
- **Documented**: 2026-05-26
- **Retrospective**: true
- **Decision makers**: Steward + Council
- **Supersedes**: N/A (foundational decision)

## Context

ODS records document decisions that may need correction (errors discovered later, new information, revised judgment). Two approaches to handling corrections were available:

1. **In-place edits**: mutate the existing record to reflect corrections.
2. **Append-only with linkage**: leave the original record intact, create a new record that references it via `parent_id`.

The first approach is incompatible with audit-grade infrastructure. If records can be mutated silently, the audit trail loses its assurance — an auditor cannot distinguish "this is what was actually decided at time T" from "this is what someone said was decided at time T after the fact."

Additionally, in-place edits via git (`commit --amend`, `rebase`, etc.) can rewrite history, further weakening the audit trail and breaking any externally-published hash chains.

## Decision

ODS records are immutable once committed. Corrections happen via NEW records (typically with `record_type: CORRECTION` or via dedicated correction semantics in profiles) that reference the prior record via a top-level `parent_id` field. The original record is never modified.

Implementation constraints:

- ODS implementations MUST treat records as immutable after creation.
- File system stores MUST be append-only.
- Git operations on record files MUST NOT use `git commit --amend`, `git rebase --interactive` over committed records, or any history-rewriting operation.
- Any change to a previously-committed record's content is a fault condition, not a feature.

## Alternatives Considered

1. **In-place mutation**: rejected because it breaks the audit trail. If records can change without history, no auditor can verify what was decided when.
2. **Versioning within record (e.g., `version: 2` on same record_id)**: rejected because it conflates "this is a corrected version" with "this is what's currently true." Also makes downstream consumers' invalidation logic complex.
3. **Full audit history within record (`history: [...]`)**: rejected because it duplicates filesystem/git history within record content, increasing fragility and storage cost.
4. **Append-only with parent_id (adopted)**: matches Event Sourcing patterns in audit-grade systems; `parent_id` provides explicit linkage; original is never touched.

## Consequences

### Positive

- Audit trail is verifiable: the timestamp of each record is the timestamp of decision, not of last edit.
- Implementations can use simple append-only stores (JSONL files, append-only databases, immutable object storage).
- Counterfactual reasoning is preserved: prior records remain in their original form, available for reference.
- Git as a backing store is sufficient and natural (no rebase needed).
- External hash chains can be computed and published with confidence they won't be invalidated.

### Negative

- Correcting many records (e.g., a systematic error) requires many new records, not a single mutation.
- Downstream consumers must apply `parent_id`-aware logic to "see latest state" for a record chain.
- Disk usage grows monotonically (acceptable for audit-grade data, where retention is the point).

### Neutral

- Adopters migrating from mutable logging conventions face a one-time mental shift; once internalized, the pattern is simpler than versioned-in-place.

## Implementation

- `parent_id` field defined at top level in `schema/ods_record_v2.json`
- CLAUDE.md (repo discipline) prohibits `git commit --amend` and force-push on record files
- Validator enforces uniqueness of `record_id` within a record store
- Documentation in SPECIFICATION.md explains correction pattern

## Related

- ADR-0001 (Core + Profiles Separation)
- SPECIFICATION.md §3 (record envelope including `parent_id`)
- CLAUDE.md (record discipline rules: immutability, no force-push)
- CONFORMANCE.md §Operational Stance on Missing Records (related operational discipline)

## Validation

A clone of the repo at any past timestamp should produce identical record contents to the same clone today, for all records that existed at that timestamp. Any post-hoc edit to a committed record file is detectable via `git log -p` of the file. An auditor can reconstruct the decision sequence chronologically without ambiguity.
