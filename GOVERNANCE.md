# ODS Governance

The Operational Decision Standard is governed as an open specification with a clear, lightweight, transparent process.

This document describes how decisions about ODS itself are made.

---

## Mission

To maintain ODS as a credible, neutral, executable specification for institutional decision memory — useful across sectors, vendor-independent, and built to last.

---

## Principles

1. **Neutrality.** ODS belongs to no single vendor or implementation. The standard is independent of any specific company.

2. **Executability over assertion.** Every requirement in the specification should be verifiable through tooling — schema validation, conformance tests, reproducible examples.

3. **Stability over novelty.** Once shipped, fields and semantics do not change without explicit deprecation cycles. Implementers can rely on backward compatibility within a major version.

4. **Open process.** All substantive changes go through public RFC review. Decisions and their rationale are recorded in the repository.

5. **Real-world grounding.** Schema decisions must be informed by actual implementations and real decision-logging needs, not theoretical purity.

---

## Roles

### Maintainers

Responsible for day-to-day stewardship of the repository:
- Triaging issues
- Reviewing contributions
- Merging accepted changes
- Maintaining release hygiene

### Technical Committee

Responsible for substantive decisions about the specification:
- Accepting or rejecting RFCs
- Approving major and minor version releases
- Setting conformance certification standards
- Resolving disputes

The initial Technical Committee is appointed by the founding maintainers. Future membership is based on contribution history and community standing.

### Contributors

Anyone who participates — by opening issues, proposing RFCs, submitting pull requests, reviewing changes, or implementing the standard.

All contributors are bound by the [Code of Conduct](./CODE_OF_CONDUCT.md).

---

## RFC Process

Substantive changes to the specification follow the RFC (Request for Comments) process:

1. **Draft.** A contributor opens an RFC issue using the [RFC template](.github/ISSUE_TEMPLATE/rfc.md), describing the proposed change, motivation, alternatives considered, and impact.

2. **Review.** The RFC is reviewed publicly for at least 30 days. Anyone can comment. The author iterates.

3. **Decision.** The Technical Committee accepts, rejects, or requests changes. Rationale is recorded in the issue.

4. **Implementation.** Accepted RFCs are implemented in the next appropriate release (minor or major depending on impact).

5. **Tracking.** Accepted RFCs are recorded in the [rfcs/](./rfcs/) directory with their final form and decision history.

See [rfcs/README.md](./rfcs/README.md) for full process details.

---

## Versioning

ODS follows semantic versioning. See [VERSIONING.md](./VERSIONING.md) for the full policy.

In short:
- **Major** versions may include breaking schema changes (rare, well-justified)
- **Minor** versions add backward-compatible capabilities
- **Patch** versions clarify language without changing semantics

---

## Backward Compatibility

ODS commits to backward compatibility within major versions. See [COMPATIBILITY.md](./COMPATIBILITY.md) for the full policy, including:

- Field stability commitments
- Deprecation procedures
- Migration support windows

---

## Conflict Resolution

Disagreements are resolved in this order:

1. **Discussion.** Most disputes resolve through public technical conversation.
2. **Maintainer decision.** For day-to-day matters, maintainers decide.
3. **Technical Committee decision.** For substantive matters, the Technical Committee decides by consensus, escalating to majority vote if needed.
4. **Public record.** All decisions and their rationale are documented.

---

## Funding and Independence

ODS is currently maintained by volunteer contributors and the founding implementation team (ORPI Systems).

The standard is intentionally independent of any single funder or vendor. As the ecosystem grows, the Foundation may seek funding from multiple parties to ensure sustainability — always with safeguards to preserve the neutrality of the specification itself.

---

## Communication

- **Issues** — bug reports, RFCs, feature requests
- **Discussions** — open community conversation
- **Pull Requests** — concrete changes proposed for review

---

## Amending This Document

This governance document itself follows the RFC process. Proposed changes to governance go through the same review and acceptance procedure as changes to the specification.

---

🏛️ ODS Foundation
