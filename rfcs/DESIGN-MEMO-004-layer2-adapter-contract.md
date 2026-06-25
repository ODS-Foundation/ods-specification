# Design Memo 004: Layer 2 Adapter Contract for Write-Time Behavioral Conformance

| Field | Value |
|-------|-------|
| **Memo ID** | DESIGN-MEMO-004 |
| **Title** | Layer 2 Adapter Contract for Write-Time Behavioral Conformance |
| **Author** | ORPI Steward |
| **Status** | DRAFT |
| **Created** | 2026-06-25 |
| **Updated** | 2026-06-25 |
| **Addresses** | DESIGN-MEMO-003 Addendum (2026-06-24) — Layer 2 elevation; the 17 behavioral clauses enumerated in `conformance/manifest.json` `not_covered` |
| **Affects** | CONFORMANCE.md (adds Layer 2 conformance method), conformance/ (new Layer 2 runner + reference adapter), new document `conformance/ADAPTER-CONTRACT.md` |
| **Path** | Design Memo → Council Review → Amendments → Final Memo → Authorization → Implementation → Pre-merge Review → Ship |

### Amendment History

| Version | Date | Summary |
|---------|------|---------|
| 0.1 | 2026-06-25 | Initial DRAFT — adapter transport, operation set, time-clause scope, reference adapter, state isolation. |

---

## 1. Purpose and context

The static conformance suite (DESIGN-MEMO-003, Layers 1 + 3, on `main` at the conformance
merge) certifies **record and store** conformance: properties decidable by validating a
record, or a candidate against a small store, with the reference validator. Empirical
measurement during SD-2/SD-3 established that the majority of Core Standard, Core Full, and
profile Standard/Full requirements are **behavioral** — they describe what an implementation
does at write time and over its lifecycle, not what a single record looks like. The static
suite enumerates these in its machine-readable `not_covered` list (17 clauses) and labels
every level verdict "(statically-decidable clauses)" so a static PASS never overstates.

Per the DESIGN-MEMO-003 Addendum (2026-06-24, ORPI-2026-06-24), Layer 2 (write-time
behavioral conformance) is the next normative item, in two steps: **(1) a language-neutral
adapter contract** — this memo — **and (2) write-time fixtures** that drive it. This memo
defines step 1 only. It writes no fixtures and changes no existing suite bytes.

The central reframe: the **validator is read-time** (one record in, accept/reject out); the
**adapter is write-time** (drive an implementation's write path, observe what it does). A
correct OUTCOME-FINAL-uniqueness check at write, a store-assigned `sequence_number`, an
append-only refusal, a CHECKPOINT's Merkle root, an inclusion proof — none of these can be
read off a file. They require operating the implementation as a live process. That is why
Layer 2 needs a contract, not another schema.

## 2. Scope

**In scope (this memo):** the contract an ODS implementation implements so a single Layer 2
suite can drive it identically regardless of language or storage backend — transport,
operation set, result shapes, exit semantics, state isolation — plus a reference adapter
over the reference store so the Layer 2 suite is itself verifiable.

**Out of scope (this memo):** the write-time fixtures and the Layer 2 runner (step 2,
implementation under this memo); any change to the static suite; any public signal. The
Addendum's discipline holds — sequence commitment, not a public date; no announcement until
and beyond the static base landing on `main`.

**Out of automated scope even for Layer 2 (honest ceiling).** The two-axis honesty of
SD-2/SD-3 continues: some clauses are not testable even by driving the implementation, and
the contract says so rather than implying coverage. These remain in `not_covered`:

- Retention duration (≥ 7 years / permanent) — a wall-clock policy with no bounded test.
- Real-time governance/compliance signaling **latency/SLA** — a timing guarantee, not a
  structural one. The contract can observe that a signal is emitted; it does not certify
  how fast.
- CHECKPOINT cadence by **wall-clock** (the "or every 24h" trigger) — testable only behind
  an optional injectable-clock capability (§5.3); the **count** trigger (every 1000 records)
  is testable and in scope.
- Metric **value correctness** for DPI / CFR / Learning Velocity — definitional; the
  contract MAY check presence/well-formedness at Full (§4, optional `metrics`), not that a
  computed number is "right".

## 3. Transport and invocation (Default 1)

The adapter is a single executable exposing **subcommands**, taking a JSON request on
**stdin** and emitting a single JSON response on **stdout**, with **exit codes mirroring the
validator**: `0` = operation succeeded / record accepted, `1` = record rejected by a
write-time invariant, `2` = operational error (bad input, adapter fault). Human-readable
diagnostics, if any, go to stderr and are never parsed.

```
ods-adapter <subcommand> --workdir <DIR>   < request.json   > response.json
```

Rationale: subcommands + JSON over stdio is the lowest-common-denominator that any
language and any deployment (local binary, container entrypoint, thin shim over a SaaS API)
can satisfy without imposing a network protocol, a Python ABC, or a shared runtime. It is
the connectathon model: the suite speaks one wire format; each implementation brings its own
adapter. All requests and responses are UTF-8 JSON; the response MUST be a single JSON
object; field ordering is irrelevant (the suite parses structurally).

## 4. Operation set (Default 2)

Each operation defines a request shape, a response shape, and exit semantics. Shapes below
are the DRAFT contract sketch; exact JSON Schemas are fixed during review before step 2.

| Op | Request (stdin) | Response (stdout) | Exit |
|----|-----------------|-------------------|------|
| `init` | `{}` (optional config) | `{ "ok": true }` | 0 / 2 |
| `submit` | a client record (DECISION/OUTCOME/CHECKPOINT) **without** `sequence_number` | accept: `{ "accepted": true, "stored_record": { … } }`; reject: `{ "accepted": false, "code": "...", "reason": "..." }` | 0 / 1 / 2 |
| `get` | `{ "record_id": "…" }` | `{ "found": true, "record": { …canonical state… } }` or `{ "found": false }` | 0 / 2 |
| `checkpoint` | `{}` | `{ "checkpoint": { "merkle_root": "…", "tree_size": N, "sequence_range": [a,b], … } }` | 0 / 2 |
| `proof` | `{ "record_id": "…", "checkpoint": "…"? }` | `{ "proof": { "leaf_index": i, "tree_size": N, "audit_path": ["…"], "checkpoint_root": "…" } }` | 0 / 2 |
| `consistency` | `{ "from": "…", "to": "…" }` | `{ "proof": { "first_size": m, "second_size": n, "nodes": ["…"] } }` | 0 / 2 |

The suite, not the adapter, **verifies** Merkle inclusion and consistency: the adapter
*produces* a proof, and the suite recomputes the root per RFC 6962 and compares. This keeps
proof verification in the trusted suite and tests the implementation's proof *generation*.

**Behavioral clauses → operations.** This mapping is how Layer 2 retires `not_covered`
entries:

- Store-assigned `sequence_number`, monotonic — `submit` (accept) returns a `stored_record`
  carrying it; the suite asserts monotonicity across a sequence of submits.
- Reject client-submitted `sequence_number` — `submit` a record that includes one → exit 1.
- Writes OUTCOME records / parent linkage at write — `submit` OUTCOME with a valid/invalid
  `parent_id` → accept / exit 1.
- FINAL uniqueness at write — `submit` a second FINAL OUTCOME for a parent → exit 1.
- Append-only enforcement — `submit` a record reusing an existing `record_id`, or any
  mutation of a stored record → exit 1.
- Canonical read protocol / state — `get` returns the canonical stored form.
- Per-record SHA-256 via RFC 8785 (JCS) — `stored_record` (or `get`) exposes the record
  hash; the suite recomputes JCS + SHA-256 and compares.
- Merkle tree computation (RFC 6962) — `checkpoint` returns `merkle_root` / `tree_size`; the
  suite recomputes from the leaves it submitted.
- CHECKPOINT cadence (**count** trigger) — after the configured number of submits, a
  CHECKPOINT is available (auto-emitted or via `checkpoint`); the suite asserts it exists and
  covers the expected `sequence_range`.
- Inclusion proof generation — `proof`; suite verifies.
- Consistency proof generation — `consistency`; suite verifies.

**Optional, deferred to review:** a `metrics` op (`{ "record_id" }` → `{ "dpi": …, "cfr": …,
"learning_velocity": … }`) for Full-level **presence/well-formedness** checks only. Listed
as an open question (§7), not a required operation in this DRAFT.

## 5. State isolation and determinism (Default 5)

### 5.1 Working directory
The adapter operates entirely within a caller-supplied `--workdir`. `init` establishes a
clean, empty store there. Each fixture scenario begins with `init` on a fresh `--workdir`,
so scenarios are independent and order-free.

### 5.2 Scenario form
A write-time fixture (step 2) is an ordered sequence of operations with expected results,
e.g.: `init`; `submit P` (accept); `submit O1-FINAL` (accept); `submit O2-FINAL` (expect
reject, code `FINAL_NOT_UNIQUE`). The Layer 2 runner drives the sequence and compares each
observed `(exit, response)` to the fixture's expectation, emitting a deterministic,
scope-qualified report exactly as the static runner does.

### 5.3 Determinism and the clock
Responses MUST be deterministic given the same operation sequence, **except** fields that are
intrinsically environmental (wall-clock timestamps the implementation assigns). The suite
asserts on structure and on suite-supplied values, not on adapter-minted timestamps. To make
the wall-clock CHECKPOINT trigger testable, the contract MAY define an **optional**
injectable clock (`init` accepts `{ "clock": "manual" }` and a `tick` op advances it).
Implementations that do not expose it simply leave the wall-clock cadence clause in
`not_covered`; the count trigger remains covered for everyone.

## 6. Reference adapter (Default 4)

The repository ships a **reference adapter** over the reference store, analogous to
`validator/validate.py` being the Layer 1 reference. Its role is to make the Layer 2 suite
self-verifiable: the suite is developed and regression-tested against the reference adapter,
exactly as the static suite is run against the reference validator. The reference adapter is
a conformance witness, not a production store. Its location and language are an
implementation detail of step 2 (likely `conformance/adapters/reference/`), to be fixed when
step 2 is authored.

## 7. Open questions (for Council/Steward review)

1. **`metrics` op.** Include an optional `metrics` operation for Full-level presence checks,
   or leave DPI/CFR/Learning Velocity entirely in `not_covered`? Council leans toward
   *optional, presence-only* — never asserting value correctness.
2. **Auto-emit vs explicit `checkpoint`.** Should the count-trigger CHECKPOINT be observed by
   polling `checkpoint`, or must the adapter auto-emit and the suite read it back? Council
   leans toward: `checkpoint` returns the current head checkpoint (auto-emitted if cadence
   was reached), covering both styles.
3. **Error taxonomy.** Fix a small closed set of reject `code` values
   (`FINAL_NOT_UNIQUE`, `PARENT_NOT_FOUND`, `CLIENT_SEQUENCE_FORBIDDEN`, `APPEND_ONLY_VIOLATION`,
   …) so fixtures assert on `code`, not on free-text `reason`. Council recommends yes.
4. **Step-2 governance.** Are write-time fixtures implementation under this memo (the
   DESIGN-MEMO-003 → SD-1/2/3 pattern), or do they warrant their own memo? Council recommends
   implementation under this memo unless step 2 surfaces new design decisions.

## 8. Next step

On FINAL approval of this contract, step 2 proceeds: author `conformance/ADAPTER-CONTRACT.md`
(the normative contract text), the reference adapter, the Layer 2 runner, and the write-time
fixtures — as sub-deliveries, pre-merge byte-reviewed by Council, merged under this memo's
authorization. No public signal attaches to any of it. This memo does not authorize step 2;
it defines what step 2 must build against.
