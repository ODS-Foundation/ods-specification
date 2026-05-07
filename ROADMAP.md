# ODS Roadmap

This document outlines the planned evolution of the Operational Decision Standard.

The roadmap is organized in phases, not fixed dates. The Foundation prioritizes quality and real-world feedback over arbitrary timelines.

---

## Current Phase: Foundation (v1.0 — Released)

**Status:** Published

The Foundation phase establishes the core specification and reference tooling.

Delivered:
- ✅ v1.0 specification (seven-layer schema)
- ✅ Three conformance levels (Basic, Standard, Full)
- ✅ Six core principles (immutability, verifiability, attribution, temporal integrity, explainability, outcome tracking)
- ✅ Cryptographic verification model (SHA-256, Merkle trees)
- ✅ Reference implementation (ORPI Decision Vault™)
- ✅ Executable validator (`validator/validate.py`)
- ✅ Governance model and RFC process
- ✅ Versioning and compatibility policies
- ✅ Apache 2.0 license

---

## Phase 2: Interoperability (v1.1 — Q3 2026)

**Status:** Planned

The Interoperability phase strengthens ecosystem compatibility and broadens the spec's applicability.

Planned additions:

### Schema Extensions (Optional)
- **Multi-party decisions** — committee, board, and panel decisions where multiple actors share responsibility
- **Hierarchical decisions** — parent/child decision relationships for delegated authority
- **Privacy-preserving fields** — zero-knowledge friendly representations for sensitive contexts

### Verification Enhancements
- **Streaming verification** — protocols for real-time decision streams
- **Cross-implementation verification** — proofs that travel between ODS implementations
- **Attestation profiles** — signed conformance claims from third parties

### Tooling
- **Richer validator errors** — structured error reports with remediation hints
- **CLI tool** — installable Python package with `ods` command-line interface
- **Schema migration tooling** — automated upgrades between minor versions
- **Conformance test suite** — comprehensive test cases for all three levels

### Documentation
- **Industry-specific extensions** — guidance for finance, healthcare, supply chain, government
- **Pattern catalog** — common implementation patterns and anti-patterns
- **Translated specification** — community-driven translations of core documents

---

## Phase 3: Ecosystem Expansion (v2.0 — 2027)

**Status:** Long-term planning

The Ecosystem Expansion phase brings ODS into deeper integration with adjacent infrastructure.

Planned directions:

### Causal Inference Integration
- **Causal layer** — explicit causal graphs alongside decision records
- **Counterfactual generation** — standardized methods for generating alternatives
- **Treatment effect tracking** — attribution of outcomes to specific decision factors

### Cross-Organizational Capabilities
- **Decision benchmarking** — privacy-preserving comparison across organizations
- **Shared learning protocols** — federated improvement of decision quality
- **Industry consortia support** — shared schemas for sector-specific decisions

### Security and Trust
- **Adversarial decision detection** — identifying decisions made under coercion or manipulation
- **Hardware-backed attestation** — TPM and HSM-based integrity proofs
- **Formal verification** — machine-checkable conformance proofs

### Infrastructure Integration
- **Blockchain interoperability** — optional anchoring of Merkle roots to public ledgers
- **AI explainability standards** — alignment with emerging XAI standards
- **Streaming platforms** — Kafka, Pulsar, and similar streaming integrations

---

## Phase 4: Maturity (v2.x — Beyond)

**Status:** Vision

The Maturity phase is what ODS looks like when it has fully entered the infrastructure category.

Indicators of maturity:

- Multiple independent implementations across major sectors
- Third-party certification ecosystem
- Regulatory recognition in at least one major jurisdiction
- Integration into enterprise governance products
- Cross-sector decision benchmarking platforms
- Established academic and research communities

The Foundation does not attempt to predict timing for this phase. It will arrive when the ecosystem is ready.

---

## Out of Scope

ODS deliberately does not include:

- **Decision-making algorithms** — ODS records decisions; it does not prescribe how to make them
- **Specific storage technologies** — ODS is storage-agnostic
- **User interfaces** — ODS is a data and verification standard, not a UI standard
- **Authentication systems** — ODS records actor identifiers but does not standardize identity
- **Sector-specific regulations** — ODS supports compliance but does not replace regulatory frameworks

The standard's value comes from being **focused** and **interoperable**.

---

## How to Contribute to the Roadmap

The roadmap is shaped by community input through:

- **RFCs** — propose new capabilities through the [RFC process](./rfcs/README.md)
- **Issues** — flag gaps and missing capabilities
- **Discussions** — explore ideas before formalizing them as RFCs
- **Implementation feedback** — real-world experience shapes priorities

The Technical Committee reviews roadmap items at least quarterly.

---

## Phase Transitions

Each phase ends when:
1. Core deliverables are released
2. Adoption indicators show readiness for the next phase
3. The Technical Committee approves the transition

There is no schedule pressure to advance phases. The Foundation moves when the ecosystem is ready.

---

## See Also

- [VERSIONING.md](./VERSIONING.md) — how versions are numbered and decided
- [COMPATIBILITY.md](./COMPATIBILITY.md) — what stays stable across versions
- [GOVERNANCE.md](./GOVERNANCE.md) — how decisions are made
- [rfcs/](./rfcs/) — proposed and accepted changes
