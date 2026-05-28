# CLAUDE.md

This file is read automatically by Claude Code at the start of every session in this repository. The rules below apply to all work here unless explicitly suspended by the Steward in-session.

## Universal rules

1. **Think before acting.** State assumptions explicitly before doing. Ask the Steward when unsure rather than guessing. Never invent context, requirements, or constraints that were not provided.

2. **Simplicity first.** Write the minimum change that fulfills the request. No speculative scaffolding. No premature abstraction. No "while I'm here" refactors. If something obviously needs cleanup beyond the request scope, report it as a finding instead of fixing it silently.

3. **Surgical changes.** Every changed line must trace back to a specific element of the Steward's request. If you change something the Steward did not ask for, name it explicitly in your report and let the Steward decide whether to keep it.

4. **Goal-driven.** Turn vague instructions into verifiable success criteria before starting. State what "done" means and how it will be verified.

## When in doubt

Report and ask. The cost of asking a clarifying question is small; the cost of an unauthorized change to versioned artifacts is real. Default to pausing and reporting over guessing.

## Operator Autonomy Levels (L0–L3)

This section defines the autonomy levels governing how Claude Code (the Operator) acts within repositories governed by the Council / Operator / Steward pattern. The levels codify that pattern: the Council deliberates and drafts, the Steward authorizes, the Operator executes. These levels are operational discipline, not normative ODS content.

### L0 — Observational (autonomous)

Read-only operations. The Operator may perform these without authorization:

- Reading files, directory listings, `git log`, `git status`, `git diff`
- Running validators and tests in read-only mode
- Reporting findings, structure, and state to the Council

L0 operations carry no risk of altering the repository and require no approval.

### L1 — Supervised execution (autonomous within a single authorized task)

Local, reversible operations in service of an already-authorized task:

- Creating a branch from main
- Creating or editing files on a working branch
- Staging changes
- Running validation on proposed changes

The Operator performs L1 operations autonomously once a task is authorized, but PAUSES and reports to the Council before any L2 operation. Work product at L1 is not yet part of the repository's permanent record.

### L2 — Constrained record operations (explicit Council authorization required per operation)

Operations that write to permanent history or the shared remote:

- `git commit` (writing to branch history)
- `git push` (publishing to remote)
- `git merge` (integrating to main)
- Branch deletion (local and remote)

Each L2 operation requires explicit Council authorization in the conversation. The Operator never commits, pushes, or merges on its own initiative. After authorization, the Operator executes and reports back with the resulting commit hash and state verification. All merges use `--no-ff` to preserve audit trace; all commit and merge messages end with the authorizing Council session reference.

### L3 — Forbidden (never autonomous, regardless of instruction)

Operations the Operator must never perform autonomously, and which require the Steward to perform directly:

- History rewriting: `git commit --amend` on pushed commits, `git rebase` over published history, `git push --force` / `--force-with-lease` on shared branches
- Permanent deletions beyond routine branch cleanup
- Any operation touching credentials, tokens, or secrets (e.g., staging a recovery-codes or `.env` file)
- Modifying repository access controls, branch protection, or remote settings
- Any change to a previously-committed immutable artifact. In this repository, that includes ODS records and Accepted ADRs (see ARCHITECTURE.md Invariant 1)

L3 operations are not unlocked by Council or Steward instruction within the Operator's flow. If an L3 operation is genuinely needed, the Steward performs it directly, outside the Operator's autonomous scope.

### The discipline in one line

The Operator reads freely (L0), builds on a branch freely once a task is authorized (L1), writes to permanent history only with per-operation Council authorization (L2), and never rewrites history or touches secrets (L3).

## Repository-specific rules — ods-specification

This repository contains the ODS open standard specification. Modifications follow institutional discipline beyond the universal rules.

### Normative artifacts — memo-driven changes only

The following files are **normative**. Any proposed change requires a design memo first:

- `SPECIFICATION.md`
- `CONFORMANCE.md`
- `VERSIONING.md`
- `PROFILES.md`
- `CHANGELOG.md`
- `schema/*.json`
- `validator/*.py`

Documentation files (`BACKLOG.md`, `CLAUDE.md`, `README.md`, `GOVERNANCE.md`) follow branch + Council review, but do not require a design memo.

### Workflow for normative changes

1. Design memo committed to `rfcs/DESIGN-MEMO-NNN-<topic>.md` on a branch named `rfc/<topic>`
2. Council review via raw URL with cache-busting query parameter (`?cachebust=YYYYMMDDx`)
3. Council amendments applied via new commits on the same branch — NO `git commit --amend`, NO force-push; preserve full history
4. Memo marked FINAL by Council before implementation begins
5. Implementation on the same branch as the memo
6. Pre-merge review by Council, source-read via cache-busted raw URL of every changed file
7. Council authorization required before `git merge --no-ff` to main
8. Release decisions (tag, GitHub Release) only after main is updated

### Never commit to main directly

Even for trivial changes (typos, formatting) use a branch + Council review workflow. Direct commits to main bypass the institutional discipline that makes this standard auditable. There are no exceptions.

### Council reads source, not summaries

When reporting to the Council, never substitute description for content. If the Council needs to review a file, paste the cache-busted raw URL — not an index of the file, not a summary of changes, not a list of line numbers. The Council reviews the bytes that GitHub serves, not the report about them. This pattern is documented in `orpi-journal` as a permanent governance practice (2026-05-20).

### Test vector independence

Any test that claims to verify cross-implementation compatibility must derive expected values from sources independent of the implementation under test. Auto-referential tests (where expected values are computed by the same primitives being tested) are forbidden in this repository regardless of how green the test report looks. See `validator/test_merkle_rfc6962.py` for the canonical pattern: expected values are hardcoded hex constants independently computed with raw `hashlib.sha256` and the RFC 6962 byte construction.

### Honesty principle

- Deprecate publicly when errors are found (the v1.0.0 deprecation is the canonical example)
- Document known gaps in `BACKLOG.md` rather than hiding them
- Never claim implementers, adopters, or production use that does not exist
- When ODS-Foundation has no implementers, say so

### Forbidden actions

- NEVER commit to main directly
- NEVER force-push to any branch
- NEVER modify normative files without a design memo
- NEVER ship a test suite that is auto-referential
- NEVER claim adoption or implementation that does not exist
