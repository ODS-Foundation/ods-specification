# ODS Roadmap

This document describes what ODS has released, what is committed next, and what
is under exploration. It is organized by maturity, not dates: the Foundation
prioritizes quality and real-world feedback over fixed timelines. A roadmap is a
promise — so items appear here only at the confidence level their tier states.

---

## Released

Shipped and verifiable against the published specification and validator.

- **v2.1.0 — 2026-05-19.** Normative Merkle tree construction (RFC 6962); the
  `CHECKPOINT` record type and store-assigned `sequence_number`; Merkle
  verification promoted from Full to Standard conformance; inclusion and
  consistency proof APIs.
- **v2.0.0 — 2026-05-09.** ODS Core + Profiles architecture; domain-neutral core;
  `ODS-Finance/v1` as the first authored profile.
- **v1.1.0 — 2026-05-08.** Event-sourcing semantics (append-only log; OUTCOME
  records linked by `parent_id`, never mutating the DECISION); RFC 8785 (JCS)
  canonicalization for `policy_hash`; formal metric definitions. Deprecated v1.0.

A reference implementation (ORPI Decision Vault) tracks the published Core; its
records validate against the standard's own schema using the standard's own
validator.

---

## Next

Committed directions, RFC-driven, with no fixed dates (per the versioning
policy's no-cadence principle). Each proceeds through the RFC process before
release.

- **Signed CHECKPOINT records.** v2.1.0 CHECKPOINTs are unsigned: tamper-evident
  but not tamper-proof in attribution. Signed CHECKPOINTs are the next planned
  addition, targeted as a Full-conformance requirement.
- **Empirical DPI weight validation.** The Decision Process Integrity component
  weights are provisional and were committed for empirical revision via RFC.
- **`references[]` field.** A field allowing a decision record to reference
  related records, for cross-decision linkage (BACKLOG-002).
- **A second authored profile.** To demonstrate the Core + Profiles model beyond
  finance, via RFC. `ODS-Healthcare/v1` is the leading candidate.
- **CORRECTION / ANNOTATION record types** *(RFC candidate)* — append-only ways
  to correct or annotate the record graph without mutating prior records.

---

## Exploration

Directions under active consideration. These are not commitments, carry no
version or date, and are stated here to invite the expertise they require.

- **ODS-Edge.** Extending verifiable decision records to AI systems that operate
  on third-party edge devices — vehicles, robots, medical equipment — where the
  recording device cannot be assumed trustworthy. The approach builds on the
  existing Merkle/CHECKPOINT substrate (local hash chains anchored periodically to
  an external append-only store), but a full integrity guarantee depends on
  hardware-rooted trust (secure element / TEE) and specialized security
  expertise that the project does not yet have in place. We are seeking RFC
  proposals and contributors in this area. Until that expertise is engaged,
  ODS-Edge remains exploratory by design — a hard frontier named honestly, not a
  promised feature.

---

## Other directions

Capabilities raised in discussion but not on the committed roadmap — including
public-ledger anchoring, federated learning, formal verification, streaming-
platform integrations, zero-knowledge fields, and multi-party or hierarchical
decision structures — are tracked through the [RFC process](./rfcs/README.md),
not promised here. They advance only if and when a concrete RFC and real-world
need support them.

---

## Out of Scope

ODS deliberately does not include:

- **Decision-making algorithms** — ODS records decisions; it does not prescribe
  how to make them.
- **Specific storage technologies** — ODS is storage-agnostic.
- **User interfaces** — ODS is a data and verification standard.
- **Authentication systems** — ODS records actor identifiers but does not
  standardize identity.
- **Sector-specific regulations** — ODS supports compliance; it does not replace
  regulatory frameworks.

The standard's value comes from being focused and interoperable.

---

## How items move between tiers

Exploration → Next → Released is driven by the RFC process: a concrete proposal,
public review, Technical Committee evaluation of impact (breaking/additive/
clarifying), and implementation in an appropriate release. There is no schedule
pressure; items advance when reviewed, accepted, and ready.

---

## See Also

- [CHANGELOG.md](./CHANGELOG.md) — full release history
- [VERSIONING.md](./VERSIONING.md) — how versions are numbered and decided
- [COMPATIBILITY.md](./COMPATIBILITY.md) — what stays stable across versions
- [GOVERNANCE.md](./GOVERNANCE.md) — how decisions are made
- [rfcs/](./rfcs/) — proposed and accepted changes
