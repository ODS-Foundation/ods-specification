# Design Memo 001: Merkle Tree Construction Specification

| Field | Value |
|-------|-------|
| **Memo ID** | DESIGN-MEMO-001 |
| **Title** | Merkle Tree Construction Specification for ODS Batch Verification |
| **Author** | ORPI Steward |
| **Status** | DRAFT — Pending Council Review |
| **Created** | 2026-05-18 |
| **Addresses** | Audit Finding #5 — Merkle Tree Underspecification |
| **Affects** | SPECIFICATION.md, CONFORMANCE.md, VERSIONING.md |
| **Path** | Design Memo → Council Review → Amendments → Final Memo → Authorization → Implementation → Pre-merge Review → Ship |

---

## 1. Problem Statement

ODS v2.0 SPECIFICATION.md §10 states:

> "Merkle tree construction is specified in a separate document (pending RFC). For v2.0, per-record SHA-256 hashing is required at Standard conformance; Merkle tree batch verification is required at Full conformance."

The phrase "Merkle tree or equivalent" (appearing in the cap-justification text of CONFORMANCE.md) is not a specification — it is a placeholder. The construction has never been defined. This produces two concrete failure modes:

1. **Cross-implementation verification is impossible.** Two independent Standard-conformant implementations computing a Merkle root over the same store may arrive at different roots if they differ on any of: leaf pre-image construction, node combining function, canonical ordering, or odd-tree split strategy. Neither is wrong under the current spec; neither can verify the other.

2. **The conformance cap claim is hollow.** CONFORMANCE.md states "Merkle chain at Standard" as a justification for the profile conformance cap. A requirement that is not specified cannot be evaluated; an audit against that requirement cannot be passed or failed.

This audit finding disqualifies ODS from serious cryptographic audit until resolved.

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

Each ODS record maps to exactly one Merkle leaf. The leaf hash is:

```
leaf_hash = SHA-256(0x00 || UTF-8(JCS(record)))
```

Where:
- `0x00` is the single-byte domain separation prefix specified in RFC 6962 §2.1
- `JCS(record)` is the RFC 8785 (JCS) canonical JSON serialization of the complete record object as written to the store — every field present in the stored record, in JCS canonical key order
- `UTF-8(...)` is the byte encoding of the JCS output string (JCS output is always valid UTF-8)
- `SHA-256(...)` is the standard 32-byte SHA-256 digest

**Rationale for hashing the complete record:**
- Consistent with how ODS already uses `SHA-256(JCS(policy_object))` for `policy_hash` in the identity envelope — JCS is the canonical serialization for all ODS hashing
- Binds every field of the record to its leaf position, including `_schema_version`, `record_type`, `record_id`, and `timestamp_utc`; no field can be altered without invalidating the leaf and thus the root
- Simple and deterministic: any conformant implementation already has a JCS library

**What is NOT hashed as the leaf pre-image:**
- Only `record_id` (insufficient binding — content can change while ID remains fixed)
- Only selected fields (selective binding creates audit gaps)
- A separately computed record fingerprint (double-hashing without added security)

The complete `JCS(record)` is the leaf data. No abbreviation.

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

Canonical ordering determines which record occupies which leaf index. It must be **deterministic and derivable solely from record content**, so that two independent implementations reading the same store always build the same tree.

**Proposed canonical ordering:**

```
Primary:   timestamp_utc  ASCENDING  (ISO 8601 lexicographic; microsecond precision makes this a numeric sort)
Secondary: record_id      ASCENDING  (lexicographic on UUID string representation)
```

**Rationale:**

- `timestamp_utc` ascending is the natural append-order proxy. Records appear in temporal sequence in the tree, matching the semantic model of an append-only log.
- `record_id` as a tiebreaker eliminates ambiguity when two records share an identical `timestamp_utc`. UUID v4 lexicographic order is defined and consistent across all implementations. The sort key is the UUID string as written in the JSON field (e.g., `"78ca73b1-a4fd-46a5-855a-770af55091c9"`), not a binary encoding.
- Both sort keys are present in every ODS record as required fields — no implementation can claim a record without them.

**Clock-skew consideration (open question O-1):** Bulk imports or records generated from systems with clock skew may arrive out of `timestamp_utc` order relative to their store insertion order. Under the proposed canonical ordering, such records will sort by their claimed timestamp regardless of when they were inserted. This is the correct audit behavior (the tree reflects what was decided and when, not when the record was written to the store). Council should confirm this is the intended semantics or redirect to a store-sequence-number model if a future store API guarantees monotonic sequence numbers.

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
MTH({d(0)}) = SHA-256(0x00 || UTF-8(JCS(d(0))))
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

A new `record_type` value `CHECKPOINT` is introduced. A CHECKPOINT record is an ODS record that attests to the Merkle root of a specific prefix of the store.

**CHECKPOINT records are subject to the same immutability rules as all ODS records.** They are included as leaves in subsequent Merkle trees (i.e., future CHECKPOINTs cover the records preceding them, including prior CHECKPOINTs). They are NOT included in the tree they themselves describe — that would be circular, since the root is not known until the tree is computed.

### 7.3 CHECKPOINT Record Schema

```json
{
  "_schema_version": "2.1.0",
  "record_type": "CHECKPOINT",
  "record_id": "<uuid-v4>",
  "timestamp_utc": "<iso-8601-microseconds>",
  "identity": {
    "model_version": "<string>",
    "policy_hash": "<sha256-hex>"
  },
  "checkpoint": {
    "tree_size": 42,
    "tree_root": "<sha256-hex-64-chars>",
    "covers_through_record_id": "<uuid-of-last-included-record>",
    "ordering": "timestamp_utc ASC, record_id ASC"
  }
}
```

**Field semantics:**

- `checkpoint.tree_size` — the number of records included as leaves in this tree (all record types, including prior CHECKPOINTs, ordered canonically)
- `checkpoint.tree_root` — the 64-character lowercase hex encoding of the 32-byte SHA-256 Merkle root
- `checkpoint.covers_through_record_id` — the `record_id` of the last record included in this tree by canonical ordering; unambiguously defines the covered set without requiring the verifier to know the full ordering in advance
- `checkpoint.ordering` — the literal string `"timestamp_utc ASC, record_id ASC"` for v2.1.0; reserved for future ordering strategies

**What the CHECKPOINT record does NOT include:** a cryptographic signature over the root (unlike CT's STH). ODS does not mandate a signing key infrastructure in the core spec. If an implementation wishes to sign CHECKPOINTs, it may do so in the `governance` envelope using existing ODS extension patterns. A signing profile can be specified in a future RFC.

### 7.4 CHECKPOINT Emission Cadence

Implementations MUST emit at least one CHECKPOINT:
- After every 1,000 records appended to the store, OR
- After every 24 hours of operation, whichever comes first

Implementations MAY emit CHECKPOINTs more frequently. Auditors may request on-demand CHECKPOINTs via the API.

The cadence is a conformance floor, not a ceiling. Mission-critical implementations are expected to checkpoint more aggressively.

### 7.5 Relationship to Existing Reserved Types

CHECKPOINT is proposed for addition to the **active** record types table (alongside DECISION and OUTCOME), not the reserved/planned table. It is functional from v2.1.0. CORRECTION and ANNOTATION remain in the reserved/planned table (planned for a future 2.x release) — this memo does not change their status.

**Council decision required (open question O-2):** Should CHECKPOINT be added to the active types table in v2.1.0, or should it first go through the reserved/planned staging? Given that CHECKPOINT is a cryptographic infrastructure record (not a domain semantic record), the Council may prefer to treat it as an infrastructure primitive and authorize it immediately rather than staging it.

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

- `leaf_index` — the zero-based position of the record in the canonical ordering (0 = first record in tree)
- `tree_size` — total number of leaves in the tree; must match `checkpoint.tree_size`
- `audit_path` — ordered list of SHA-256 hashes constituting the audit path per RFC 6962 §2.1.1

### 8.3 Verification Procedure

A verifier receiving an inclusion proof MUST:

1. Fetch the record identified by `record_id`
2. Compute `leaf_hash = SHA-256(0x00 || UTF-8(JCS(record)))`
3. Fetch the CHECKPOINT record identified by `checkpoint_record_id`; extract `tree_root`
4. Starting from `leaf_hash` at position `leaf_index` in a tree of `tree_size` leaves, apply the RFC 6962 §2.1.1 path-following algorithm:
   - At each step, determine whether the current node is a left or right child from `leaf_index` and the current subtree size
   - Combine using `SHA-256(0x01 || left || right)`
5. Compare the computed root with `tree_root` from the CHECKPOINT record
6. Accept the proof if and only if the roots match

### 8.4 Consistency Proofs (Informational)

RFC 6962 §2.1.2 defines **consistency proofs** that demonstrate a newer tree is a prefix extension of an older tree (i.e., no records were deleted or reordered between checkpoints). ODS implementations MAY implement:

```
GET /checkpoints/{new_checkpoint_id}/consistency?from={old_checkpoint_id}
```

Consistency proofs are not required for Standard or Full conformance in v2.1.0 but are RECOMMENDED for Full-conformant implementations as part of continuous audit support. A future RFC may elevate this to a requirement.

---

## 9. Versioning Analysis

### 9.1 What This Change Introduces

| Change | Type |
|--------|------|
| New `CHECKPOINT` record_type with `checkpoint` field block | Additive |
| New Merkle construction spec (leaf hash, node hash, split rule) | New verification mechanism |
| New API endpoint `GET /records/{id}/proof` | Additive |
| Tightening of Standard conformance to require Merkle computation | Conformance tightening |
| Resolution of SPECIFICATION.md §10 placeholder text | Clarification |

### 9.2 The Semver Question: v2.1.0 or v3.0.0

**Argument for v3.0.0 (major):**
Adding Merkle as a requirement at Standard changes the definition of Standard conformance. An implementation currently claiming Standard must now implement Merkle computation and CHECKPOINT emission to retain that claim. This is a new mandatory capability.

**Argument for v2.1.0 (minor):**
1. No existing record is invalidated. DECISION and OUTCOME records with `_schema_version: "2.0.0"` remain valid and complete. Nothing about their schemas, semantics, or required fields changes.
2. VERSIONING.md §MINOR explicitly lists "New conformance options" and "New verification mechanisms" as minor-bump triggers.
3. VERSIONING.md §MINOR states: "Clarifications that strengthen the spec without breaking existing records." Specifying the Merkle construction that was always intended (the spec text says "pending RFC") is precisely this kind of clarification.
4. The SPECIFICATION.md itself flags the Merkle spec as pending RFC — the ecosystem expects a 2.x clarification, not a breaking 3.0 revision.
5. CHECKPOINT is a new, optional record type. A v2.0 implementation encountering a v2.1.0 CHECKPOINT in the store will emit a warning (per VERSIONING.md: "SHOULD accept records with newer minor versions") but will not fail to read DECISION/OUTCOME records.
6. The profile conformance cap rationale in CONFORMANCE.md already cites "Merkle chain at Standard" — this resolution makes the spec self-consistent; it does not introduce a semantic shift.

**Council-recommended position: v2.1.0.**

The decisive factor is that no existing record schema changes and no existing valid record is invalidated. The CHECKPOINT type is purely additive. The Merkle construction spec clarifies what was explicitly flagged as pending, not what was previously stable and complete. A v3.0.0 bump would overstate the disruption and impose unnecessary migration overhead on early adopters.

**Conformance grace period:** Regardless of version, implementations currently claiming Standard conformance without Merkle support should be given a 90-day grace period from the v2.1.0 release date to add CHECKPOINT emission and inclusion proof support before their Standard claim becomes non-conformant.

---

## 10. Conformance Impact

The following changes to CONFORMANCE.md are proposed. These are subject to Council authorization before implementation.

### 10.1 Standard Level (Revised)

Current Standard requirements include:
> "Verifies record integrity with SHA-256 per record using RFC 8785 (JCS) canonical serialization"

Proposed additions to Standard:
- Computes Merkle trees per RFC 6962 §2.1 using the leaf and node construction specified in DESIGN-MEMO-001 (canonicalized in SPECIFICATION.md §X upon acceptance)
- Emits CHECKPOINT records at minimum every 1,000 records or 24 hours
- Exposes inclusion proof API: `GET /records/{id}/proof`
- Verifies inclusion proofs against CHECKPOINT roots

### 10.2 Full Level (Revised)

Current Full requirements do not explicitly mention Merkle (inconsistent with SPECIFICATION.md §10 which assigns Merkle to Full). This inconsistency is resolved as follows:

Proposed additions to Full (above Standard):
- Implements consistency proof generation (RFC 6962 §2.1.2) between any two sequential CHECKPOINTs
- Exposes consistency proof API: `GET /checkpoints/{new_id}/consistency?from={old_id}`
- Verifies consistency proofs on receipt of new CHECKPOINTs
- Supports real-time Merkle verification on record ingest (not just at checkpoint intervals)

### 10.3 Basic Level

No change. Basic implementations are not required to compute Merkle trees.

### 10.4 Profile Conformance Cap

The cap rationale in CONFORMANCE.md ("Merkle chain at Standard, full audit cryptography at Full") becomes accurate and substantiated once Standard is updated as above. No change to the cap rule itself is needed; the underlying requirements now match the stated justification.

### 10.5 Existing Inconsistency to Resolve

There is a current inconsistency between:
- SPECIFICATION.md §10: "Merkle tree batch verification is required at **Full** conformance"
- CONFORMANCE.md cap rationale: "Merkle chain at **Standard**"

The Council must decide which position is normative. This memo recommends **Merkle at Standard** (consistent with the CONFORMANCE.md cap text), which means SPECIFICATION.md §10 requires correction. If the Council prefers Merkle at Full, the CONFORMANCE.md cap rationale requires correction instead. Both documents cannot stand as written.

---

## 11. Open Questions for Council Review

**O-1 — Canonical ordering: timestamp-based vs. sequence-number-based**
The proposed ordering (`timestamp_utc ASC, record_id ASC`) is derivable from record content alone and requires no external store metadata. An alternative is to require stores to assign monotonic sequence numbers to records at write time and order by sequence number. The sequence-number approach is simpler but requires the store API to expose sequence numbers — adding an infrastructure requirement not present in v2.0. Council should confirm the timestamp-based ordering is acceptable given its clock-skew implications, or authorize a store sequence-number requirement.

**O-2 — CHECKPOINT as active type vs. reserved/planned staging**
Should CHECKPOINT be added directly to the active record types in v2.1.0, or first to the reserved/planned table? Argument for direct active: it is an infrastructure primitive required for conformance. Argument for staging: preserves the pattern that new semantic types go through reserved staging. Council call.

**O-3 — CHECKPOINT signing**
RFC 6962 §3.5 STHs are signed by the log's private key. ODS v2.1.0 CHECKPOINTs are not signed (no signing key infrastructure is mandated in core). Is unsigned CHECKPOINT sufficient for the audit use case, or should v2.1.0 mandate a signing key and include a `checkpoint.signature` field? If signatures are required, the key management architecture must also be specified.

**O-4 — CHECKPOINT records in their own tree**
This memo proposes that CHECKPOINT records are included as leaves in subsequent trees (not in the tree they describe). An alternative is to exclude CHECKPOINT records from all Merkle trees and treat them as pure metadata. Exclusion simplifies tree construction (the tree only covers DECISION/OUTCOME records) but reduces the cryptographic binding (a CHECKPOINT itself could be replaced without being detected by subsequent trees). Council should confirm the inclusive approach.

**O-5 — Grace period duration**
The memo proposes 90 days for existing Standard-claiming implementations to add Merkle support. Is this sufficient? Are there known implementers whose timelines should inform this window?

---

## 12. References

- **RFC 6962** — Laurie, Langley, Kasper. "Certificate Transparency." IETF, June 2013. Specifically §2.1 (Merkle Hash Trees), §2.1.1 (Merkle Audit Proofs), §2.1.2 (Merkle Consistency Proofs), §3.5 (Signed Tree Head).
- **RFC 8785** — Rundgren, Jordan, Erdtman. "JSON Canonicalization Scheme (JCS)." IETF, June 2020. Normative for leaf pre-image serialization.
- **ODS SPECIFICATION.md v2.0.0** — §10 (Merkle placeholder, "pending RFC"), §4 (canonical serialization), §2 (append-only store model).
- **ODS CONFORMANCE.md v2.0.0** — §Standard (current requirements), §Full (current requirements), §Profile Conformance Cap.
- **ODS VERSIONING.md v2.0.0** — §MINOR (triggers), §MAJOR (triggers).
- Kelsey, Schneier. "Second Preimages on n-bit Hash Functions for Much Less than 2ⁿ Work." 2005. (Motivates domain-separation prefixes in RFC 6962 §2.1.)

---

## 13. Checklist — Pre-Council Review

- [x] Problem statement is concrete and cites specific spec language
- [x] Resolution anchored in RFC 6962 as directed (not an original construction)
- [x] Leaf hash construction fully specified with exact byte layout
- [x] Internal node construction fully specified with exact byte layout
- [x] Canonical ordering specified and deterministic
- [x] All three edge cases addressed (empty, single, odd)
- [x] Root storage mechanism proposed (CHECKPOINT record type)
- [x] Inclusion proof format fully specified
- [x] Versioning impact argued with SemVer reasoning
- [x] Conformance impact specified for all three levels
- [x] Existing spec inconsistency surfaced for Council resolution
- [x] Open questions enumerated with options presented, not pre-decided
- [x] References provided with specific section citations

---

*Status: DRAFT v1 — Ready for Council Review*
*Next step: Council reviews, amends, and either returns for revision or authorizes as Final Memo*
