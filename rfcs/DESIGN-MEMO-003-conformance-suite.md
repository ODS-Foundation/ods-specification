# DESIGN-MEMO-003 — Conformance Suite (Layer 1 + Layer 3)

**Status:** FINAL (Steward-approved 2026-06-23)
**Date:** 2026-06-23
**Author:** Council
**Affects:** CONFORMANCE (operationalizes), IMPLEMENTATION (new tooling), GOVERNANCE (certification)
**Related:** CONFORMANCE.md, SPECIFICATION.md, DESIGN-MEMO-001 (Merkle invariants)

---

## 1. Context

ODS already defines conformance normatively (CONFORMANCE.md: two-axis core + profile,
levels Basic/Standard/Full, the profile≤core cap) and ships a validator
(`validator/validate.py`) that checks record schema, profile schema (two-pass), and
store-level invariants (`parent_id` existence, one-FINAL-per-chain).

What is missing is the layer that turns a conformance *claim* into a *certifiable,
reproducible result*. Today an implementer can assert "ODS Core v2 Standard" but cannot
hand a regulator or adopter a report they can run independently and confirm. This is the
gap FHIR closes with its conformance materials, and it is the difference between "we have
a published standard" and "we have a standard that is adoptable and verifiable." The
conformance suite is the project's primary moat.

A behavioral-invariants conformance suite is already a committed Next-tier roadmap item.

## 2. Goals and non-goals

**Goals.** Provide a standardized, level-tagged, clause-traceable battery of fixtures and
a runner that any implementation can execute to produce a conformance report stating which
core/profile levels it satisfies, traceable to the specific normative clauses exercised.

**Non-goals.** The suite does NOT introduce new normative requirements — it operationalizes
existing ones. It does NOT certify the *quality* or *correctness* of decisions, only
conformance of records and verification to the standard. It does NOT (in this version) test
write-time behavior.

## 3. Decisions

**D1 — Three-layer model; v1 ships Layer 1 + Layer 3; Layer 2 deferred.**
- *Layer 1 — Record & store conformance (static fixtures).* A corpus of ODS records run
  against the validator: single-record fixtures (schema + structural rules) and store-level
  fixtures (multi-record sets exercising the `--store` invariants), plus Merkle
  verification fixtures (a log + CHECKPOINT + inclusion/consistency proofs, valid and
  tampered). Each fixture is a positive (MUST accept) or negative (MUST reject) case.
- *Layer 3 — Profile conformance.* ODS-Finance/v1 fixtures per level, reusing the Layer 1
  mechanism, validating the profile second pass.
- *Layer 2 — Behavioral/write-time conformance (DEFERRED).* Invariants enforced at write
  time (store-assigned `sequence_number`, rejection of client-supplied `sequence_number`,
  write-time FINAL rejection, append-only enforcement) require the implementation to expose
  a thin adapter interface. Defining that contract is itself a design decision, deferred to
  a follow-up memo. Rationale: Layer 1 delivers the bulk of certifiable value without a new
  contract — infrastructure before features. Resolved direction for that contract (see §7):
  it MUST be language-neutral (e.g., CLI/JSON over stdin/stdout) so any implementation in
  any language can certify; a Python prototype against the reference implementation is
  permitted for iteration but is not the conformance contract.

**D2 — Fixture corpus structure.** Fixtures are clean, valid-or-intentionally-invalid ODS
records, kept free of test metadata. A separate `manifest.json` maps each fixture file to
its `{ clause, level, expect: accept|reject, rationale }`. This keeps fixtures usable as
real examples and makes clause coverage auditable.

**D3 — Runner and conformance report.** A runner drives the validator across the in-scope
corpus for a declared target level and emits a structured report (machine-readable JSON +
human-readable summary) giving a per-level verdict and per-clause pass/fail, e.g.
"ODS Core v2 Standard: PASS (n/n clauses) + ODS-Finance v1 Standard: PASS (m/m)." The JSON
report is emitted in deterministic, canonicalizable form (JCS-ready, RFC 8785) and
accompanied by its SHA-256 digest, giving a verifiable fingerprint of the result without
embedding it in the ODS record model. Wrapping the report as a full ODS-style verifiable
artifact is deferred to v2 of the suite (§7).

**D4 — Location and relationship to the validator.** Lives in `conformance/` in the spec
repo. The suite *uses* `validator/validate.py` as the system under test for Layer 1/3; it
does not replace it. Directory sketch:
- `conformance/fixtures/core/{basic,standard,full}/{valid,invalid}/`
- `conformance/fixtures/stores/` and `conformance/fixtures/merkle/`
- `conformance/fixtures/profiles/ods-finance-v1/{basic,standard,full}/{valid,invalid}/`
- `conformance/manifest.json`
- `conformance/runner/run_conformance.py`
- `conformance/CONFORMANCE-SUITE.md` (how to run; how to declare conformance from results)

**D5 — Conformance claim semantics.** Passing the in-scope corpus for a level demonstrates
record/verification conformance to that level's testable clauses. The report states exactly
which clauses were exercised; clauses that are inherently write-time (Layer 2) are listed as
"not covered in this version" so a v1 report never overstates what it proves. Honest scope is
a normative-grade requirement of the report itself. A conformance result is a
measurement/attestation, not a decision under human authority; it MUST NOT be coerced into
DECISION/OUTCOME semantics. If a verifiable-artifact form is adopted later (v2), it uses an
attestation/checkpoint model, not the decision record types.

## 4. Scope of edits (when FINAL → implementation)

Net-new files only, under `conformance/`. No edits to existing normative files are
anticipated.

## 5. Out of scope

- Layer 2 behavioral/write-time conformance (follow-up memo; contract direction fixed in D1).
- Emitting the conformance report as a full ODS-style verifiable artifact (v2 of the suite).
- Any change to conformance *requirements* themselves.

## 6. Implementation

Single `rfc/` branch. If building the suite surfaces a genuine ambiguity in CONFORMANCE.md
or SPECIFICATION that needs clarification, that change is added as an amendment commit to
this memo (and only then touches a normative file), preserving the memo gate. Commits and
merge carry `Council-Authorized: ORPI-2026-06-23`. This memo, once FINAL, satisfies the
normative-file gate for any conformance-clarification edits it explicitly authorizes.

## 7. Resolved directions (this session)

1. **Conformance report format.** v1 emits a deterministic, JCS-ready JSON report plus its
   SHA-256 digest; the full ODS-style verifiable-artifact form is deferred to v2 and, when
   adopted, uses an attestation/checkpoint model — a conformance result is not a DECISION.
2. **Layer 2 adapter contract.** Language-neutral (CLI/JSON over stdin/stdout), not a Python
   ABC; a Python prototype is permitted for iteration but does not define conformance.

## 8. References

- CONFORMANCE.md (levels, two-axis, cap, validator behavior)
- SPECIFICATION.md §§ immutability, FINAL uniqueness, sequence_number, Merkle/CHECKPOINT
- DESIGN-MEMO-001 (Merkle construction, conformance impact)
- RFC 6962 (Merkle proofs); RFC 8785 (JCS)
---

## Addendum — 2026-06-24 (Steward-authorized re-scope)

Recorded as a new commit; the original decisions above are unchanged.

During SD-2 authoring, empirical measurement against the reference validator established
that the majority of Standard and Full requirements are **behavioral** (runtime APIs,
retention, CHECKPOINT cadence, Merkle proof generation/verification, metric computation,
real-time signaling) and are **not statically decidable**. The static suite (Layers 1 + 3)
therefore certifies record and store conformance only.

Consequences, authorized by the Steward (ORPI-2026-06-24):

1. **Honest reporting.** The runner labels every level verdict with the scope qualifier
   "(statically-decidable clauses)" and emits a machine-readable `not_covered` list
   enumerating every behavioral clause. A static PASS is necessary but not sufficient for a
   full Standard/Full conformance claim.

2. **Layer 2 elevated.** Layer 2 (write-time behavioral conformance) moves from
   "deferred without date" to the **next normative item after SD-3**. This is a *sequence*
   commitment, not a public-date commitment; no public signal until the static base is on
   `main`. The Layer 2 memo proceeds in two steps: (1) a language-neutral adapter contract,
   then (2) write-time fixtures.

This addendum amends DESIGN-MEMO-003 additively and is never applied via amend/force-push.
