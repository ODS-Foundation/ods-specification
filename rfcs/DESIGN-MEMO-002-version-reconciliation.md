# DESIGN-MEMO-002 — Version Reconciliation & Roadmap Restructure

**Status:** FINAL (Steward-approved 2026-06-17)
**Date:** 2026-06-17
**Author:** Council
**Steward:** David Julian Rizo López
**Relates to:** DESIGN-MEMO-001 (v2.1.0 / Merkle; Council-approved 2026-05-19)

## 1. Context

The shipped artifacts and the descriptive documentation disagree about which
version of ODS is current, and the roadmap presents the release history
inverted. This memo reconciles the documentation to shipped reality and
restructures the roadmap. No specification semantics change.

## 2. Findings (source-grounded @ commit 6079127)

**Correct — source of truth, NOT edited:**
- `CHANGELOG.md` — accurate history: v1.1.0 (2026-05-08), v2.0.0 (2026-05-09),
  v2.1.0 (2026-05-19, Merkle/CHECKPOINT, governed by DESIGN-MEMO-001).
- `validator/validate.py` — v2.x; implements v2.1.0 (CHECKPOINT, sequence_number).
- `schema/ods_record_v2.json` — accepts `2.0.0` and `2.1.0`.

**Stale — reconciled by this memo:**
- `README.md` — badge `2.0.0` (L4); "Current version: v2.0.0" (L11); spec label
  "v2.0.0" (L52); embedded roadmap (L227–229).
- `VERSIONING.md` — "Version Status" (L118–144) omits v2.1.0.
- `ROADMAP.md` — presents deprecated v1.0 as "Current Phase … Released" (L9–24);
  lists v1.1/v2.0 as planned/future (L28, L59); attributes Merkle to v1.0 (L19).

**Policy-vs-tooling gap:** VERSIONING states v1.1.0 records remain valid and v2
implementations SHOULD read both schemas (L126–130), but the reference validator
loads only the v2 core schema; `schema/ods_record_v1.json` remains in-repo, unused
by the reference validator.

## 3. Decisions

**D1 — Canonical current version.** v2.1.0 is the current stable release across
all descriptive documents.

**D2 — v1.1.0 status & validator gap.** Retain policy (v1.1.0 valid; v1.0
deprecated). Add one honest clarification in VERSIONING: the reference validator
targets v2.x; `ods_record_v1.json` remains in-repo as the historical v1.x schema.
No semantic change.

**D3 — README & VERSIONING currency.** Update README version references and the
VERSIONING "Version Status" section to reflect v2.1.0 as current and v2.0.0 as
previous. README's embedded roadmap mirrors the new ROADMAP tiers (D4).

**D4 — ROADMAP restructure (Steward-approved 2026-06-17).** Replace the four-phase,
date-anchored model with a credibility-first three-tier structure:
  - **Released** — verifiable, dated: v1.1.0, v2.0.0, v2.1.0.
  - **Next** — committed, uncadenced, RFC-driven: signed CHECKPOINT records;
    empirical DPI weight validation; `references[]` field (BACKLOG-002); a second
    authored profile via RFC (ODS-Healthcare/v1 candidate); CORRECTION/ANNOTATION
    record types as an RFC candidate.
  - **Exploration** — under consideration, non-committal, dependency-flagged:
    ODS-Edge (trustworthy records from untrusted edge AI systems). No version,
    no date; explicit hardware-trust dependency; expertise-seeking.
  Speculative items previously listed (blockchain interop, federated learning,
  formal verification, streaming integrations, ZK fields, multi-party/hierarchical
  decisions) are pruned from roadmap commitments and redirected to the RFC process.

## 4. Scope of edits

Edited: `README.md`, `VERSIONING.md`, `ROADMAP.md` (full restructure).
NOT edited: `CHANGELOG.md` (source of truth), `validator/validate.py` logic and
`schema/*` (correct; D2 touches only descriptive documentation).

## 5. Out of scope

Specification semantics; conformance levels; any change to v2.1.0 behavior;
committing ODS-Edge to a dated deliverable.

## 6. Implementation

Single `rfc/` branch. Commits and merge commit carry
`Council-Authorized: ORPI-2026-06-17`. This memo satisfies the normative-file gate
for `VERSIONING.md`. The memo gate is respected, not suspended.
