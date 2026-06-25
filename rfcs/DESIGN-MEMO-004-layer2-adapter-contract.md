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
| 0.2 | 2026-06-25 | Resolved the four §7 open questions into the body (Steward-approved 2026-06-25): optional presence-only `metrics` op; `checkpoint` returns current head; closed reject-code taxonomy; step-2 governed under this memo. §7 converted from open questions to a decisions record. |

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
  the optional injectable-clock capability (§5.3); the **count** trigger (every 1000
  records) is testable and in scope.
- Metric **value correctness** for DPI / CFR / Learning Velocity — definitional. The
  contract checks presence/well-formedness only, via the optional `metrics` op (§4.2), never
  that a computed number is "right".

## 3. Transport and invocation (Decision 1)

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

## 4. Operation set (Decision 2)

### 4.1 Core operations

Each operation defines a request shape, a response shape, and exit semantics. Shapes below
are the contract sketch; exact JSON Schemas are fixed at step 2 against this memo.

| Op | Request (stdin) | Response (stdout) | Exit |
|----|-----------------|-------------------|------|
| `init` | `{}` (optional config) | `{ "ok": true }` | 0 / 2 |
| `submit` | a client record (DECISION/OUTCOME/CHECKPOINT) **without** `sequence_number` | accept: `{ "accepted": true, "stored_record": { … } }`; reject: `{ "accepted": false, "code": "...", "reason": "..." }` | 0 / 1 / 2 |
| `get` | `{ "record_id": "…" }` | `{ "found": true, "record": { …canonical state… } }` or `{ "found": false }` | 0 / 2 |
| `checkpoint` | `{}` | `{ "checkpoint": { "merkle_root": "…", "tree_size": N, "sequence_range": [a,b], … } }` | 0 / 2 |
| `proof` | `{ "record_id": "…", "checkpoint": "…"? }` | `{ "proof": { "leaf_index": i, "tree_size": N, "audit_path": ["…"], "checkpoint_root": "…" } }` | 0 / 2 |
| `consistency` | `{ "from": "…", "to": "…" }` | `{ "proof": { "first_size": m, "second_size": n, "nodes": ["…"] } }` | 0 / 2 |

**`checkpoint` semantics (Decision 2).** `checkpoint` returns the **current head
checkpoint** — auto-emitted by the implementation if its cadence (e.g. the count trigger) has
been reached, or freshly produced on demand otherwise. This single shape covers both
auto-emitting and on-demand implementations: the suite reads the head and asserts on its
structure and `sequence_range`, without prescribing when emission happens internally.

The suite, not the adapter, **verifies** Merkle inclusion and consistency: the adapter
*produces* a proof, and the suite recomputes the root per RFC 6962 and compares. This keeps
proof verification in the trusted suite and tests the implementation's proof *generation*.

### 4.2 Optional operation — `metrics` (Decision 1, Full-level, presence-only)

| Op | Request (stdin) | Response (stdout) | Exit |
|----|-----------------|-------------------|------|
| `metrics` | `{ "record_id": "…" }` | `{ "dpi": <number>, "cfr": <number>, "learning_velocity": <number> }` | 0 / 2 |

`metrics` is **optional**. When an implementation exposes it, the Full-level suite checks the
fields are **present and well-formed** (correct types/ranges) — it never asserts a value is
"correct", because correctness depends on the metric definition, which this memo deliberately
does not pin. Implementations that do not expose `metrics` leave the DPI/CFR/Learning
Velocity computation clauses in `not_covered`.

### 4.3 Reject codes (Decision 3 — closed taxonomy)

A `submit` rejection (exit 1) MUST carry a `code` from this closed set, so fixtures assert on
`code` rather than free-text `reason`. The set is extended only by amendment to this memo.

| Code | Meaning |
|------|---------|
| `CLIENT_SEQUENCE_FORBIDDEN` | The submitted record included a `sequence_number` (clients MUST NOT). |
| `PARENT_NOT_FOUND` | An OUTCOME's `parent_id` does not reference an existing record. |
| `FINAL_NOT_UNIQUE` | A second FINAL OUTCOME was submitted for a parent that already has one. |
| `APPEND_ONLY_VIOLATION` | A submit reused an existing `record_id` or attempted to mutate a stored record. |
| `PROFILE_MISMATCH` | An OUTCOME's `profile` does not match its parent DECISION's `profile`. |
| `RESERVED_PROFILE` | The record's `profile` references a registry-reserved namespace. |
| `SCHEMA_INVALID` | The record fails core or profile schema validation at write time. |

`reason` remains a free-text human aid and is never asserted on.

### 4.4 Behavioral clauses → operations

This mapping is how Layer 2 retires `not_covered` entries:

- Store-assigned `sequence_number`, monotonic — `submit` (accept) returns a `stored_record`
  carrying it; the suite asserts monotonicity across a sequence of submits.
- Reject client-submitted `sequence_number` — `submit` a record that includes one → exit 1,
  `CLIENT_SEQUENCE_FORBIDDEN`.
- Writes OUTCOME records / parent linkage at write — `submit` OUTCOME with a valid/invalid
  `parent_id` → accept / exit 1 `PARENT_NOT_FOUND`.
- FINAL uniqueness at write — second FINAL OUTCOME → exit 1 `FINAL_NOT_UNIQUE`.
- Append-only enforcement — reuse/mutate `record_id` → exit 1 `APPEND_ONLY_VIOLATION`.
- Canonical read protocol / state — `get` returns the canonical stored form.
- Per-record SHA-256 via RFC 8785 (JCS) — `stored_record`/`get` exposes the record hash; the
  suite recomputes JCS + SHA-256 and compares.
- Merkle tree computation (RFC 6962) — `checkpoint` returns `merkle_root`/`tree_size`; the
  suite recomputes from the leaves it submitted.
- CHECKPOINT cadence (**count** trigger) — after the configured number of submits, the head
  `checkpoint` covers the expected `sequence_range`.
- Inclusion proof generation — `proof`; suite verifies.
- Consistency proof generation — `consistency`; suite verifies.

## 5. State isolation and determinism (Decision 5)

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

## 6. Reference adapter (Decision 4 context)

The repository ships a **reference adapter** over the reference store, analogous to
`validator/validate.py` being the Layer 1 reference. Its role is to make the Layer 2 suite
self-verifiable: the suite is developed and regression-tested against the reference adapter,
exactly as the static suite is run against the reference validator. The reference adapter is
a conformance witness, not a production store. Its location and language are an
implementation detail of step 2 (likely `conformance/adapters/reference/`), to be fixed when
step 2 is authored.

## 7. Resolved decisions (Steward-approved 2026-06-25)

The four questions raised in the v0.1 DRAFT were resolved by the Steward and folded into the
body above. Recorded here so the FINAL memo carries decisions, not open questions:

1. **`metrics` op — optional, presence-only (§4.2).** DPI/CFR/Learning Velocity are checked
   for presence and well-formedness when exposed, never for value correctness; value
   correctness would require pinning the metric definitions, which is deliberately deferred.
2. **`checkpoint` returns the current head (§4.1).** Auto-emitted if cadence was reached,
   on-demand otherwise — one shape covers both implementation styles without forcing either.
3. **Closed reject-code taxonomy (§4.3).** Fixtures assert on a fixed `code` set, not on
   free-text `reason`, so they are robust against wording changes. The set grows only by
   amendment.
4. **Step-2 governance under this memo (§8).** Write-time fixtures are implementation under
   this memo (the DESIGN-MEMO-003 → SD-1/2/3 pattern), unless construction surfaces a new
   design decision warranting its own amendment or memo.

## 8. Next step

On FINAL approval of this contract, step 2 proceeds **as implementation under this memo**:
author `conformance/ADAPTER-CONTRACT.md` (the normative contract text), the reference
adapter, the Layer 2 runner, and the write-time fixtures — as sub-deliveries, pre-merge
byte-reviewed by Council, merged under this memo's authorization. Should construction surface
a genuinely new design decision, it is recorded as an amendment to this memo (new commit,
never amend/force-push) or, if large enough, its own memo. No public signal attaches to any
of it. This memo does not itself authorize step 2; it defines what step 2 must build against.
