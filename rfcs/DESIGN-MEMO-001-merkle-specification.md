# Design Memo 001: Merkle Tree Construction Specification

| Field | Value |
|-------|-------|
| **Memo ID** | DESIGN-MEMO-001 |
| **Title** | Merkle Tree Construction Specification for ODS Batch Verification |
| **Author** | ORPI Steward |
| **Status** | DRAFT v2 — Pending Council Re-review |
| **Created** | 2026-05-18 |
| **Updated** | 2026-05-18 |
| **Addresses** | Audit Finding #5 — Merkle Tree Underspecification |
| **Affects** | SPECIFICATION.md, CONFORMANCE.md, VERSIONING.md |
| **Path** | Design Memo → Council Review → Amendments → Final Memo → Authorization → Implementation → Pre-merge Review → Ship |

### Amendment History

| Version | Date | Summary |
|---------|------|---------|
| v1 | 2026-05-18 | Initial draft — adopted RFC 6962 construction; proposed timestamp-based canonical ordering; raised O-1 through O-5 as open questions |
| v2 | 2026-05-18 | **Critical structural fix:** timestamp ordering removed and replaced with store-assigned sequence_number (see §5). All five open questions resolved by Council directive. §10.5 inconsistency resolved. Signed CHECKPOINT deferred to DESIGN-MEMO-002. |

---

## 1. Problem Statement

ODS v2.0 SPECIFICATION.md §10 states:

> "Merkle tree construction is specified in a separate document (pending RFC). For v2.0, per-record SHA-256 hashing is required at Standard conformance; Merkle tree batch verification is required at Full conformance."

The phrase "Merkle tree or equivalent" (appearing in the cap-justification text of CONFORMANCE.md) is not a specification — it is a placeholder. The construction has never been defined. This produces two concrete failure modes:

1. **Cross-implementation verification is impossible.** Two independent Standard-conformant implementations computing a Merkle root over the same store may arrive at different roots if they differ on any of: leaf pre-image construction, node combining function, canonical ordering, or odd-tree split strategy. Neither is wrong under the current spec; neither can verify the other.

2. **The conformance cap claim is hollow.** CONFORMANCE.md states "Merkle chain at Standard" as a justification for the profile conformance cap. A requirement that is not specified cannot be evaluated; an audit against that requirement cannot be passed or failed.

This audit finding disqualifies ODS from serious cryptographic audit until resolved.

### 1.1 Additional Structural Flaw Identified in v1 Council Review

The v1 draft (2026-05-18) proposed ordering records by `timestamp_utc` (client-supplied). Council review identified that this creates a fundamental incompatibility with RFC 6962 consistency proofs (§2.1.2): client-supplied timestamps allow backdated records to be inserted at arbitrary positions within an already-checkpointed tree, breaking the prefix-extension property that consistency proofs require mathematically. This flaw is corrected in §5 of this version. The correction materially strengthens the security model and has implications for versioning analysis (§9) and the stored record schema (§3).

---

## 2. Resolution: Adopt RFC 6962 Merkle Hash Tree Construction

The Council has directed adoption of **RFC 6962 (Certificate Transparency), §2.1** as the normative Merkle construction. This anchors ODS in a battle-tested IETF lineage — the same philosophy that drove adoption of RFC 8785 (JCS) for canonical serialization. ODS does not invent cryptographic constructions; it adopts well-specified ones.

RFC 6962 §2.1 defines:

- A domain-separated leaf hash using prefix **`0x00`**
- A domain-separated internal node hash using prefix **`0x01`**
- A specific recursive split rule for trees of arbitrary size

The domain separation prefixes prevent second-preimage attacks (an internal node hash cannot be mistaken for a leaf hash). This is the same property Certificate Transparency relies on for log security.

The following sections specify exactly how RFC 6962 §2.1 maps onto ODS records.

---

## 3. Leaf Hash Construction

**Normative reference:** RFC 6962 §2.1, leaf hash definition.

Each Merkle-eligible ODS record (see §5.4 for eligibility definition) maps to exactly one Merkle leaf. The leaf hash is:

```
leaf_hash = SHA-256(0x00 || UTF-8(JCS(stored_record)))
```

Where:
- `0x00` is the single-byte domain separation prefix specified in RFC 6962 §2.1
- `JCS(stored_record)` is the RFC 8785 (JCS) canonical JSON serialization of the **stored representation** of the record — the complete record object as returned by `GET /records/{id}`, including the store-assigned `sequence_number` field (see §5.3)
- `UTF-8(...)` is the byte encoding of the JCS output string (JCS output is always valid UTF-8)
- `SHA-256(...)` is the standard 32-byte SHA-256 digest

**Critical distinction — stored representation vs. submitted payload:** Clients submit records without a `sequence_number` field. The store adds `sequence_number` at write time before persisting. The leaf hash is computed over the stored representation (which includes `sequence_number`), not the client-submitted payload. An auditor computing a leaf hash MUST fetch the record from the store and use the stored representation exactly as returned.

**Rationale for hashing the complete stored record:**
- Consistent with how ODS already uses `SHA-256(JCS(policy_object))` for `policy_hash` in the identity envelope — JCS is the canonical serialization for all ODS hashing
- Including `sequence_number` in the hashed content binds each record to its position in the log; an attacker cannot reorder records without changing leaf hashes and thus the tree root
- Binds every field of the record to its leaf, including `_schema_version`, `record_type`, `record_id`, and `timestamp_utc`; no field can be altered without invalidating the leaf and thus the root
- Simple and deterministic: any conformant implementation already has a JCS library

**What is NOT hashed as the leaf pre-image:**
- Only `record_id` (insufficient binding — content can change while ID remains fixed)
- Only selected fields (selective binding creates audit gaps)
- `sequence_number` encoded as raw bytes outside the JCS representation (inconsistent with the JCS-for-everything approach; complexity without benefit)

The complete `JCS(stored_record)` is the leaf data. No abbreviation.

---

## 4. Internal Node Construction

**Normative reference:** RFC 6962 §2.1, internal node hash definition.

For any two child hashes `left` and `right` (each 32 bytes):

```
node_hash = SHA-256(0x01 || left || right)
```

Where:
- `0x01` is the single-byte domain separation prefix specified in RFC 6962 §2.1
- `left` and `right` are the 32-byte SHA-256 digests of the left and right subtrees respectively, concatenated in that order
- Total pre-image length: 65 bytes (1 prefix + 32 left + 32 right)

This construction is identical to the Certificate Transparency log hash function. No deviation from RFC 6962 §2.1 is introduced.

---

## 5. Canonical Ordering

### 5.1 Why timestamp_utc Ordering Is Incompatible with Consistency Proofs

The v1 draft proposed ordering by `timestamp_utc` (client-supplied). This ordering is **incompatible with RFC 6962 consistency proofs** (§2.1.2) and must be rejected.

The incompatibility is structural, not incidental:

RFC 6962 consistency proofs (§2.1.2) prove that a tree `T₂` (tree_size=m) is a **prefix extension** of an earlier tree `T₁` (tree_size=n, n < m): the first n leaves of T₂ are identical to the n leaves of T₁, and T₂ simply appends m-n new leaves at the right. This property holds if and only if the canonical ordering is **monotonically assigned by the log at write time**, so that no new record can ever be inserted at a position less than the current tree_size.

`timestamp_utc` is client-supplied and therefore not monotonic at the log level. A record submitted at wall-clock time T₂ may carry `timestamp_utc` of T₁ (clock skew, bulk import, retrospective logging). Under timestamp ordering, this backdated record would be assigned a canonical position before records already included in a prior CHECKPOINT. The result:

- **The prefix-extension property is violated.** Leaves at positions [backdated_position, old_tree_size-1] in T₂ differ from the same positions in T₁, because the backdated record was inserted mid-tree.
- **Consistency proofs fail for non-tampered stores.** A verifier applying the RFC 6962 §2.1.2 algorithm would conclude the store was tampered with, when it was not.
- **Tamper detection becomes unreliable.** Because legitimate operations can produce consistency proof failures, genuine tampering cannot be distinguished from legitimate backdated inserts.

Certificate Transparency resolves this by assigning positions from a server-controlled, monotonically incrementing log index — not from certificate validity times, which are client-supplied and arbitrary. ODS must do the same.

### 5.2 Sequence-Number Ordering

**Canonical ordering for Merkle leaves is by `sequence_number` ascending.**

```
sequence_number  ASCENDING  (integer, store-assigned, monotonically increasing, gapless)
```

`sequence_number` is a unique, monotonically increasing integer assigned by the store to each Merkle-eligible record at write time, beginning at 1. There are no gaps. The record with `sequence_number: n+1` was always written after the record with `sequence_number: n`.

Under this ordering:
- Every new record is appended at the right of the current leaf sequence
- No record can ever be inserted at a position before an already-checkpointed record
- RFC 6962 §2.1.2 consistency proofs are mathematically valid at all times
- The Merkle log has the same structural guarantees as a Certificate Transparency log

**Tiebreaking is not needed.** `sequence_number` values are unique by construction; there can be no ties.

### 5.3 sequence_number: Storage, Assignment, and Non-Falsifiability

**Assignment:** `sequence_number` is assigned exclusively by the store. Clients MUST NOT include `sequence_number` in submitted record payloads. A store receiving a submitted record that contains a `sequence_number` field MUST reject the write with an appropriate error.

**Storage:** The store adds `sequence_number` to the record JSON before persisting it. The stored representation — as returned by `GET /records/{id}` — always includes `sequence_number` for Merkle-eligible records. This is the representation used for leaf hash computation (§3).

**Non-falsifiability:** Because `sequence_number` is store-assigned and rejected when client-submitted, clients cannot control their record's position in the Merkle log. A record's leaf position is determined entirely by the store's write-time assignment. This is the same non-falsifiability property that CT log operators provide.

**Schema position:** `sequence_number` is a top-level field in the stored record JSON, at the same level as `_schema_version`, `record_type`, and `record_id`. Its JCS key sort position (between `"record_id"` and `"record_type"` alphabetically) is determined by RFC 8785 key ordering and requires no special handling.

**Stored record example (DECISION, v2.1.0 store):**

```json
{
  "_schema_version": "2.1.0",
  "cognition": { "..." : "..." },
  "counterfactuals": [],
  "governance": { "..." : "..." },
  "identity": { "..." : "..." },
  "record_id": "<uuid-v4>",
  "record_type": "DECISION",
  "sequence_number": 42,
  "timestamp_utc": "<iso-8601-microseconds>"
}
```

*(Fields shown in JCS canonical key order — alphabetical, as RFC 8785 requires.)*

### 5.4 Merkle Log Genesis and v2.0 Record Exclusion

**v2.0 records do not participate in the v2.1.0 Merkle log.**

When an existing v2.0 store is upgraded to v2.1.0, pre-existing records (those written before the upgrade) have no `sequence_number` and are excluded from the Merkle log. The Merkle sequence begins with `sequence_number: 1` assigned to the first record written after the upgrade. Pre-existing records remain fully readable and are verified by per-record SHA-256 (the v2.0 Standard requirement), but they do not appear as leaves in any Merkle tree.

New v2.1.0 stores begin with `sequence_number: 1` from first write.

**Rationale for this boundary:** Retroactively assigning sequence numbers to v2.0 records would require modifying their stored representation (adding `sequence_number`), which violates ODS immutability. The clean forward boundary preserves record immutability unconditionally, and is the condition under which v2.1.0 remains a minor version rather than a major version (see §9).

---

## 6. Edge Cases

**Normative reference:** RFC 6962 §2.1, recursive definition.

### 6.1 Empty Tree

```
MTH({}) = SHA-256(b"")
```

The Merkle Tree Hash of zero records is the SHA-256 hash of the empty byte string. This is the value a CHECKPOINT with `tree_size: 0` would record.

Per RFC 6962 §2.1: "The hash of an empty list is the hash of an empty string."

### 6.2 Single Record

```
MTH({d(0)}) = SHA-256(0x00 || UTF-8(JCS(stored_record_0)))
```

A tree containing exactly one record reduces to that record's leaf hash. There is no internal node. The root equals the leaf.

### 6.3 Odd Number of Records (General Case)

RFC 6962 §2.1 defines a specific **power-of-two split rule** rather than padding:

For `n` records `D[0..n-1]`:
1. Compute `k = 2^⌊log₂(n-1)⌋` — the largest power of 2 strictly less than `n`
2. Partition: left subtree covers `D[0..k-1]` (k records), right subtree covers `D[k..n-1]` (n-k records)
3. Recurse on each subtree, then combine: `MTH(D[0..n-1]) = SHA-256(0x01 || MTH(D[0..k-1]) || MTH(D[k..n-1]))`

**Worked examples:**

| n | k | Left size | Right size |
|---|---|-----------|------------|
| 3 | 2 | 2         | 1          |
| 5 | 4 | 4         | 1          |
| 6 | 4 | 4         | 2          |
| 7 | 4 | 4         | 3          |
| 9 | 8 | 8         | 1          |

**Critical note:** RFC 6962 does NOT pad the right subtree with zero hashes or duplicate the last leaf to make the tree "complete" in the balanced-binary-tree sense. The split is asymmetric by design. Any implementation that pads will produce a different root than one that follows the RFC 6962 split rule.

---

## 7. Root Storage: The CHECKPOINT Record Type

### 7.1 Problem

The ODS store is immutable and append-only. A Merkle root cannot be stored by modifying an existing record. The root must be persisted as a new append-only record in the store.

### 7.2 Design: CHECKPOINT Record Type

ODS adopts the conceptual structure of the Certificate Transparency **Signed Tree Head (STH)** (RFC 6962 §3.5) as the basis for root storage, adapted to the ODS append-only record model.

A new `record_type` value `CHECKPOINT` is introduced. A CHECKPOINT record is an ODS record that attests to the Merkle root of a specific prefix of the store's Merkle log.

**CHECKPOINT records are subject to the same immutability rules as all ODS records.** They are assigned `sequence_number` values by the store and are included as leaves in subsequent Merkle trees (i.e., future CHECKPOINTs cover the records preceding them, including prior CHECKPOINTs). They are NOT included in the tree they themselves describe — that would be circular, since the root is not known until the tree is computed.

**Rationale for the inclusive approach (O-4, resolved):** Including CHECKPOINT records as leaves in subsequent trees provides full cryptographic binding across the checkpoint chain. A CHECKPOINT that is not itself committed as a leaf in a later tree could be silently replaced by a different CHECKPOINT over the same record set (e.g., a CHECKPOINT with a doctored root hash), and no subsequent tree would detect the substitution. The inclusive approach forecloses this attack vector. The alternative — treating CHECKPOINTs as pure metadata excluded from all trees — reduces cryptographic binding without any implementation benefit, and is therefore rejected.

### 7.3 CHECKPOINT Record Schema

```json
{
  "_schema_version": "2.1.0",
  "record_type": "CHECKPOINT",
  "record_id": "<uuid-v4>",
  "sequence_number": 43,
  "timestamp_utc": "<iso-8601-microseconds>",
  "identity": {
    "model_version": "<string>",
    "policy_hash": "<sha256-hex>"
  },
  "checkpoint": {
    "tree_size": 42,
    "tree_root": "<sha256-hex-64-chars>",
    "covers_through_sequence_number": 42,
    "ordering": "sequence_number ASC"
  }
}
```

**Field semantics:**

- `sequence_number` — store-assigned sequence number for this CHECKPOINT record itself (it is a record in the store and receives a sequence number like any other); note that `sequence_number` (43 in the example) is strictly greater than `checkpoint.covers_through_sequence_number` (42), because the CHECKPOINT is written after the tree it describes
- `checkpoint.tree_size` — the number of records included as leaves in this tree
- `checkpoint.tree_root` — the 64-character lowercase hex encoding of the 32-byte SHA-256 Merkle root
- `checkpoint.covers_through_sequence_number` — the `sequence_number` of the last record included in this tree; equals `tree_size` when the Merkle log is gapless from sequence_number 1
- `checkpoint.ordering` — the literal string `"sequence_number ASC"` for v2.1.0; reserved for future ordering strategies

### 7.3.1 Security Limitation: Tamper-Evidence Without Attribution

**Unsigned CHECKPOINTs, as specified in v2.1.0, provide tamper-evidence but NOT tamper-proof attribution.**

- **Tamper-evidence:** Any modification to the content or ordering of included records, after a CHECKPOINT is emitted, changes the tree root. Recomputing the Merkle root from the stored records will produce a value that does not match `checkpoint.tree_root`, and verification fails. The modification is detected.

- **What is NOT provided:** Without a cryptographic signature from a key controlled by the store operator, it cannot be proven (a) who generated a given CHECKPOINT, or (b) that an adversary with write access has not replaced a legitimate CHECKPOINT with a different CHECKPOINT they computed over a tampered record set. Unsigned CHECKPOINTs do not prevent an adversary who can both modify records and append new records from constructing a self-consistent but fraudulent state.

This is the same architectural position as other provisional integrity mechanisms in the ODS security model: tamper-evidence for operational monitoring and audit, attribution and non-repudiation deferred to a higher tier. Signed CHECKPOINTs (including key management, signing procedure, and signature verification) are scoped to a future DESIGN-MEMO-002 and will be a Full-level conformance requirement.

### 7.4 CHECKPOINT Emission Cadence

Implementations MUST emit at least one CHECKPOINT:
- After every 1,000 Merkle-eligible records appended to the store, OR
- After every 24 hours of operation during which at least one Merkle-eligible record was written, whichever comes first

Implementations MAY emit CHECKPOINTs more frequently. Auditors may request on-demand CHECKPOINTs via the API.

The cadence is a conformance floor, not a ceiling. Mission-critical implementations are expected to checkpoint more aggressively.

### 7.5 Relationship to Existing Record Types

**Council decision (O-2, resolved):** CHECKPOINT is added directly to the **active** record types table in v2.1.0, alongside DECISION and OUTCOME. It does not go through the reserved/planned staging that semantic record types (CORRECTION, ANNOTATION) follow.

Rationale: the reserved/planned staging path exists for **domain-semantic record types** whose field semantics, relationships to other record types, and DPI/CFR metric interactions require deliberate design and ecosystem feedback before activation. CHECKPOINT is a **cryptographic infrastructure primitive** — its sole function is to attest to a Merkle root at a point in time. It has no semantic relationship to decisions or outcomes, does not affect DPI/CFR computation, and its schema is mechanically determined by the Merkle construction spec. Staging it would defer Merkle conformance with no design benefit.

CORRECTION and ANNOTATION remain in the reserved/planned table and are unaffected by this decision.

---

## 8. Inclusion Proof Format

**Normative reference:** RFC 6962 §2.1.1, Merkle Audit Proofs.

An inclusion proof demonstrates that a specific ODS record is a leaf in the tree attested by a specific CHECKPOINT, without requiring the verifier to reconstruct the full tree.

### 8.1 API Endpoint

```
GET /records/{record_id}/proof?checkpoint={checkpoint_record_id}
```

If `checkpoint` is omitted, the server returns a proof against the most recent CHECKPOINT that covers the record.

### 8.2 Response Format

```json
{
  "record_id": "<uuid>",
  "checkpoint_record_id": "<uuid>",
  "leaf_index": 41,
  "tree_size": 42,
  "audit_path": [
    "<sha256-hex>",
    "<sha256-hex>",
    "..."
  ]
}
```

**Field semantics:**

- `leaf_index` — the zero-based position of the record in the canonical ordering (= `sequence_number - 1`, since sequence_numbers begin at 1 and leaf indices begin at 0)
- `tree_size` — total number of leaves in the tree; must match `checkpoint.tree_size`
- `audit_path` — ordered list of SHA-256 hashes constituting the audit path per RFC 6962 §2.1.1

### 8.3 Verification Procedure

A verifier receiving an inclusion proof MUST:

1. Fetch the stored record identified by `record_id` from `GET /records/{record_id}`
2. Compute `leaf_hash = SHA-256(0x00 || UTF-8(JCS(stored_record)))` — the stored record as returned by the API, which includes the store-assigned `sequence_number` field
3. Fetch the CHECKPOINT record identified by `checkpoint_record_id`; extract `tree_root`
4. Confirm `leaf_index = stored_record.sequence_number - 1` and `tree_size = checkpoint.tree_size`
5. Starting from `leaf_hash` at position `leaf_index` in a tree of `tree_size` leaves, apply the RFC 6962 §2.1.1 path-following algorithm:
   - At each step, determine whether the current node is a left or right child from `leaf_index` and the current subtree size
   - Combine using `SHA-256(0x01 || left || right)`
6. Compare the computed root with `tree_root` from the CHECKPOINT record
7. Accept the proof if and only if the roots match

### 8.4 Consistency Proofs

**Normative reference:** RFC 6962 §2.1.2, Merkle Consistency Proofs.

Consistency proofs are **valid and well-defined** under sequence_number ordering because the Merkle log is append-only by construction (§5.1–5.2). A consistency proof between CHECKPOINT C₁ (tree_size=n) and CHECKPOINT C₂ (tree_size=m, m > n) proves that the first n leaves of C₂'s tree are identical to the n leaves of C₁'s tree — i.e., no previously-checkpointed record was modified, deleted, or reordered.

ODS implementations MAY implement:

```
GET /checkpoints/{new_checkpoint_id}/consistency?from={old_checkpoint_id}
```

Consistency proofs are RECOMMENDED for Full-conformant implementations as part of continuous audit support. A future RFC may elevate this to a Full-level requirement. They are not required for Standard conformance in v2.1.0.

---

## 9. Versioning Analysis

### 9.1 What This Change Introduces

| Change | Type |
|--------|------|
| New store-assigned field `sequence_number` in v2.1.0+ stored records | Additive (store-assigned; not a client schema change) |
| New `CHECKPOINT` record_type with `checkpoint` field block | Additive |
| New Merkle construction spec (leaf hash, node hash, split rule) | New verification mechanism |
| New API endpoint `GET /records/{id}/proof` | Additive |
| Tightening of Standard conformance to require Merkle computation | Conformance tightening (clarification of stated intent) |
| Resolution of SPECIFICATION.md §10 placeholder text | Clarification |

### 9.2 The SemVer Question: v2.1.0 or v3.0.0

**Council preliminary position: v2.1.0.** This section argues the position explicitly, as directed.

**Argument for v3.0.0 (major):**
Adding Merkle as a requirement at Standard changes the definition of Standard conformance. An implementation currently claiming Standard must now implement sequence_number assignment, Merkle computation, and CHECKPOINT emission to retain that claim. `sequence_number` is a new field in stored record representations.

**Argument for v2.1.0 (minor) — explicit construction:**

The VERSIONING.md major version triggers are:
1. Removing or renaming required schema fields — **not triggered**: no existing field is removed or renamed
2. Changing the type or constraints of a required field in incompatible ways — **not triggered**: no existing field changes type or constraints
3. Removing a previously declared conformance level — **not triggered**: Basic, Standard, and Full all remain
4. Changing fundamental semantics that would invalidate existing records — **not triggered** (see below)

**Do existing v2.0 records become invalid?** No, under the condition the Council specified: v2.0 records do not participate in the v2.1.0 Merkle log. A v2.0 DECISION record written today remains a valid, readable, SHA-256-verifiable record under v2.1.0. Its JSON is never touched. Its `_schema_version: "2.0.0"` remains accurate. The Merkle log is a new layer that begins at a forward boundary — it does not retroactively invalidate or require modification of anything written before that boundary.

**Does `sequence_number` constitute a breaking schema change?** `sequence_number` is store-assigned, not client-specified. Clients continue to submit records in exactly the same format as v2.0. The API contract for record submission is unchanged. Only the store's internal write protocol and the stored representation change, which is an implementation concern, not a schema-breaking change for record authors. A v2.0 reader encountering a stored record with a `sequence_number` field will encounter an unknown field and should (per forward-compatibility convention) ignore it rather than fail.

**What makes this definitively minor and not a judgment call:**
The SPECIFICATION.md already flagged Merkle as "pending RFC." The conformance text already stated "Merkle chain at Standard" in the cap rationale. The Merkle requirement was never absent from the spec's intent — it was absent from the spec's text. Resolving a documented placeholder is not a semantic shift; it is the completion of an explicitly incomplete specification. The ecosystem was warned that this RFC was coming.

**Conclusion: v2.1.0.** The decisive conditions are: (a) no v2.0 record is invalidated, (b) no existing required field changes, (c) the change is the resolution of a documented placeholder, and (d) `sequence_number` is store-assigned and transparent to record authors.

---

## 10. Conformance Impact

The following changes to CONFORMANCE.md are proposed. These are subject to Council authorization before implementation.

### 10.1 Standard Level (Revised)

Current Standard requirements include:
> "Verifies record integrity with SHA-256 per record using RFC 8785 (JCS) canonical serialization"

Proposed additions to Standard:
- Assigns monotonically increasing `sequence_number` to each record at write time; rejects client-submitted records that include a `sequence_number` field
- Computes Merkle trees per RFC 6962 §2.1 using the leaf and node construction specified in this memo (canonicalized in SPECIFICATION.md §X upon acceptance), ordering by `sequence_number ASC`
- Emits CHECKPOINT records at minimum every 1,000 Merkle-eligible records or every 24 hours of operation with at least one write, whichever comes first
- Exposes inclusion proof API: `GET /records/{id}/proof`
- Verifies inclusion proofs against CHECKPOINT roots on auditor request

### 10.2 Full Level (Revised)

Current Full requirements do not explicitly mention Merkle (inconsistent with SPECIFICATION.md §10 which assigns Merkle to Full). This inconsistency is resolved by §10.5. Full builds on Standard and adds:

Proposed additions to Full (above Standard):
- Implements consistency proof generation (RFC 6962 §2.1.2) between any two sequential CHECKPOINTs
- Exposes consistency proof API: `GET /checkpoints/{new_id}/consistency?from={old_id}`
- Verifies consistency proofs on receipt of new CHECKPOINTs
- Supports real-time Merkle verification on record ingest (not just at checkpoint intervals)
- Signed CHECKPOINTs (key management, signing procedure, and verification): deferred to DESIGN-MEMO-002

### 10.3 Basic Level

No change. Basic implementations are not required to compute Merkle trees or assign sequence numbers.

### 10.4 Profile Conformance Cap

The cap rationale in CONFORMANCE.md ("Merkle chain at Standard, full audit cryptography at Full") is accurate and substantiated once Standard is updated as above. No change to the cap rule itself is needed; the underlying requirements now match the stated justification.

### 10.5 Inconsistency Resolution: Merkle at Standard

**Resolved.** There was a contradiction between:
- SPECIFICATION.md §10: "Merkle tree batch verification is required at **Full** conformance"
- CONFORMANCE.md cap rationale: "Merkle chain at **Standard**"

**Council decision: Merkle at Standard is normative.** SPECIFICATION.md §10 will be corrected to "Standard" during the implementation step.

Rationale: per-record SHA-256 hashing without Merkle provides per-record integrity (each record's hash can be verified in isolation) but does not provide **log-level tamper-evidence**. An attacker who can write to a store could delete records, reorder records, or insert fabricated records, and per-record SHA-256 would not detect any of these attacks — each surviving record would still verify against its own hash. Merkle trees close this gap: the root commits to the entire ordered set of records, and any deletion, insertion, or reordering changes the root. "Standard" must genuinely mean audit-grade. Audit-grade requires log-level tamper-evidence. Therefore Merkle is a Standard requirement.

### 10.6 Grace Period

Implementations currently claiming Standard conformance without Merkle support are given a **90-day grace period** from the v2.1.0 release date to add sequence_number assignment, CHECKPOINT emission, and inclusion proof support before their Standard claim becomes non-conformant.

**Honesty note:** As of v2.1.0, there are no known external implementers. The grace period is precautionary and formalizes the transition norm for the record. It ensures that if an external implementer appears between now and the v2.1.0 ship date, they have a documented migration window rather than an abrupt conformance break.

---

## 11. Council Decisions Recorded

All five open questions from v1 are resolved. No open questions remain in this memo.

| ID | Question | Decision | Rationale Summary |
|----|----------|----------|-------------------|
| O-1 | Canonical ordering: timestamp vs. sequence_number | **Sequence_number, mandatory** | Timestamp ordering is structurally incompatible with RFC 6962 consistency proofs; see §5.1 |
| O-2 | CHECKPOINT: active type vs. reserved/planned staging | **Active type direct in v2.1.0** | Infrastructure primitive, not a domain-semantic type; staging provides no design benefit |
| O-3 | CHECKPOINT signing | **Unsigned OK for v2.1.0 Standard; signing deferred to DESIGN-MEMO-002 for Full** | Same pattern as other provisional integrity mechanisms; security limitation explicitly stated in §7.3.1 |
| O-4 | CHECKPOINT records included in subsequent trees | **Inclusive approach confirmed** | Exclusive approach would allow silent replacement of CHECKPOINTs; see §7.2 |
| O-5 | Grace period duration | **90 days, with honesty note** | No known external implementers; period is precautionary; see §10.6 |

---

## 12. References

- **RFC 6962** — Laurie, Langley, Kasper. "Certificate Transparency." IETF, June 2013. Specifically §2.1 (Merkle Hash Trees), §2.1.1 (Merkle Audit Proofs), §2.1.2 (Merkle Consistency Proofs), §3.5 (Signed Tree Head).
- **RFC 8785** — Rundgren, Jordan, Erdtman. "JSON Canonicalization Scheme (JCS)." IETF, June 2020. Normative for leaf pre-image serialization.
- **ODS SPECIFICATION.md v2.0.0** — §10 (Merkle placeholder, "pending RFC"), §4 (canonical serialization), §2 (append-only store model).
- **ODS CONFORMANCE.md v2.0.0** — §Standard (current requirements), §Full (current requirements), §Profile Conformance Cap.
- **ODS VERSIONING.md v2.0.0** — §MINOR (triggers), §MAJOR (triggers).
- Kelsey, Schneier. "Second Preimages on n-bit Hash Functions for Much Less than 2ⁿ Work." 2005. (Motivates domain-separation prefixes in RFC 6962 §2.1.)
- **DESIGN-MEMO-001 v1** — 2026-05-18, same branch, commit `2964574`. Preserved for Council review history.
- **DESIGN-MEMO-002** (future) — Signed CHECKPOINTs: key management, signing procedure, Full-level conformance requirement.

---

## 13. Checklist — Pre-Council Re-review

- [x] Amendment history documents v1 → v2 changes
- [x] v1 structural flaw (timestamp / consistency-proof incompatibility) identified and corrected
- [x] sequence_number: assignment, storage, non-falsifiability, and Merkle-eligibility boundary fully specified
- [x] Leaf hash updated to use stored representation (includes sequence_number)
- [x] Leaf hash formula unchanged in structure; pre-image definition updated
- [x] Internal node construction unchanged from v1
- [x] Canonical ordering section completely rewritten (§5.1–5.4)
- [x] Edge cases unchanged (split rule is independent of ordering mechanism)
- [x] CHECKPOINT schema updated (covers_through_sequence_number, ordering field)
- [x] Security limitation statement for unsigned CHECKPOINT explicit (§7.3.1)
- [x] CHECKPOINT as active type (O-2 resolved) with rationale in §7.5
- [x] Inclusive approach (O-4 resolved) with rationale in §7.2
- [x] Verification procedure updated (step 4 confirms sequence_number / leaf_index relationship)
- [x] Consistency proofs: validity argument added (§8.4 updated)
- [x] Versioning analysis updated for sequence_number model; argument made explicitly (§9.2)
- [x] Conformance impact specified for all three levels (§10.1–10.4)
- [x] §10.5 inconsistency resolved (Merkle at Standard, SPECIFICATION.md §10 to be corrected)
- [x] Grace period with honesty note (§10.6)
- [x] All open questions replaced with resolved decisions table (§11)
- [x] References updated (v1 memo preserved, DESIGN-MEMO-002 noted as future)

---

*Status: DRAFT v2 — Pending Council Re-review*
*Next step: Council reviews v2; if no further amendments required, authorizes as Final Memo and opens implementation*
