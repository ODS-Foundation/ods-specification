# Best Practices for ODS Implementations

- **Status**: Non-normative — guidance, not requirement
- **Audience**: Implementers of ODS-conformant systems; profile authors; auditors
- **Last updated**: 2026-05-26

This document captures implementation patterns and operational stances that distinguish ODS as audit-grade infrastructure from ODS as a logging convention. None of this content is normative: adopters can claim conformance against CONFORMANCE.md levels without following any of this guidance. However, adopters whose implementations exhibit the patterns described here will produce records and audit trails that withstand institutional scrutiny.

This document is a working consolidation of guidance that emerged during ODS-Foundation work through v2.0. It will evolve as new patterns are identified and validated by practice.

## Companion documents

- `SPECIFICATION.md` — normative spec for ODS Core
- `CONFORMANCE.md` — normative conformance levels and verification rules
- `PROFILES.md` — profile authoring bar and registry
- `VERSIONING.md` — version evolution policy
- `BACKLOG.md` — known gaps and v2.1 candidates
- `adr/` — Architectural Decision Records documenting governance decisions

## 1. Decision Communication Quality

ODS Core defines `cognition.rationale` as a free-form text field. The schema enforces that the field exists; it does not enforce what makes a rationale informative. Implementers writing rationales — whether human-authored or machine-generated — produce records of vastly different audit value depending on how the rationale is constructed.

Five principles distinguish informative rationales from ceremonial ones:

### 1.1 Causal, not correlational

A rationale that says "the model predicted high probability" describes a correlation. A rationale that says "we acted because constraint X required Y, given inputs Z" describes a causal mechanism. Auditors and downstream analysts can reason about mechanisms; they cannot reason about black-box probabilities. Where the decision rests on a model output, the rationale should describe what the model output represents in causal terms and what threshold or rule converted the output into the action taken.

### 1.2 Economic, not technical

A rationale that says "RMSE decreased from 0.23 to 0.19" describes a technical metric. A rationale that says "the improvement translates to materially better loss prediction accuracy, supporting tighter capital reserves" describes the economic implication. Records exist to support institutional decisions; technical metrics without economic or operational translation force every downstream reader to do the translation themselves, with varying competence and varying conclusions.

### 1.3 Forward-looking, not backward

A rationale that says "historical accuracy was 87%" describes past performance. A rationale that says "the chosen action has expected outcome X with 87% confidence, with downside scenarios Y at 13%" describes what the decider expects to happen from this decision. ODS records document decisions, which are by nature forward-looking. Rationales should articulate what the decider expected from this decision, not summary statistics about past decisions of the same class.

### 1.4 Decision-focused, not data-focused

A rationale that says "we analyzed 47 variables across 12 models" describes the data pipeline. A rationale that says "the decision is between accepting delay versus activating an alternative supplier; the tradeoff is X" describes the decision itself. Auditors evaluating a decision want to understand the choice that was made; recounting the analytical process is preamble, not substance.

### 1.5 Risk quantified, not hand-waved

A rationale that says "there is some uncertainty in the forecast" describes uncertainty rhetorically. A rationale that says "base case: outcome A; worst case (5th percentile): outcome B; best case (5th percentile): outcome C; variance is driven by factor X" describes uncertainty quantitatively. Where the decider has uncertainty estimates, the rationale should expose them. Where the decider does not have estimates, the rationale should say so explicitly rather than gesturing vaguely.

### When to apply these principles

These principles are not mandatory. A rationale that violates all five is still schema-valid. They become important when:

- The decision class is high-stakes (regulatory exposure, large capital movement, irreversible action, healthcare intervention)
- External audit is anticipated
- The record will be consumed by analysts or downstream systems
- The decision is likely to be revisited or appealed

For low-stakes routine decisions, terse rationales are appropriate.

## 2. The Audit Surface

An ODS-conformant system has an externally observable contract — the set of artifacts that auditors, downstream consumers, and partners interact with. This document calls this the *audit surface*:

- The record schema (what fields exist, what values are valid)
- The validator behavior (what it accepts, what it rejects)
- The enum vocabularies (what controlled values are defined)
- The hash semantics (how `policy_hash` is computed, how records chain via `parent_id`)
- The conformance level claims (what Basic, Standard, Full mean for this adopter)

Everything else is *internal*: how records are generated, what tooling produces them, what business logic precedes them, what storage backs them.

The audit surface is the public contract. It changes through governance — RFCs, design memos, ADRs. It is versioned. It is documented.

Internal implementation is the adopter's affair. It can change without external announcement, evolve continuously, vary across deployments.

### Why this distinction matters

It lets adopters move fast internally while preserving external trust. Auditors and partners only need to track changes to the audit surface, not the implementation details. Standards bodies that maintain a clear audit surface (HL7 FHIR's published Resources, IETF's stable RFCs, W3C's recommendations) achieve credibility precisely because of this separation.

### Guidance for implementers

Identify, document, and treat as a public commitment your audit surface — even if your only auditor today is your future self. Internal change without surface change is free. Surface change requires governance discipline. Conflating the two produces churn that auditors discount and that adopters resent.

## 3. Operational Stance on Missing Records

`CONFORMANCE.md` §Operational Stance on Missing Records makes the formal conformance interpretation: the absence of an ODS record, within declared scope, is a fault condition equivalent to silent execution failure.

This section provides implementation guidance behind that stance.

### What it means in practice

An ODS implementation operating at Standard conformance or above should architecturally guarantee that any state mutation within declared ODS scope produces a corresponding record. The guarantee is not "we try to log; if logging fails, we proceed." The guarantee is "we cannot mutate state without a record; if record creation fails, the mutation does not occur."

This pattern is the *ledger-before-state* discipline detailed in the next section.

### What it looks like operationally

- Monitoring alerts on missing records at the same severity as alerts on silent execution failures, not at the severity of data quality issues.
- Reconciliation pipelines that compare state mutations to record counts and surface gaps as faults.
- Architectural guarantees (not procedural ones) that record creation cannot be skipped under load, failure, or operator override.

### What it does not mean

- Missing records due to legitimate scope exclusion (decisions explicitly outside declared ODS scope) are not faults. The fault condition applies only to in-scope decisions.
- Missing records discovered in pre-production testing are not institutional faults; they are bugs to fix before claiming conformance.
- Missing records from a third-party system the adopter does not control may be a data quality issue from the adopter's perspective; whether they are faults depends on the third party's own conformance claims.

## 4. Ledger-Before-State Discipline

The ordering of ledger writes and state mutations matters more than most implementers initially realize. Three orderings are possible:

1. **State first, then ledger** — act, then record what was done
2. **Ledger and state in parallel** — act and record simultaneously
3. **Ledger first, then state** — record what is about to be done, then act

The first two orderings tolerate silent failure. If the ledger write fails after a successful state mutation, an external observer sees state in a configuration with no corresponding record — exactly the fault condition the audit trail exists to detect. The third ordering — ledger-before-state — makes silent failure architecturally impossible: if the ledger write fails, the state mutation does not occur.

### Why this matters for audit-grade systems

If records can be missing without state being missing, the audit trail provides no assurance. An auditor seeing 100 state mutations and 99 records cannot determine whether the missing record represents a logging bug or a covert action. In high-stakes domains (capital movements, healthcare interventions, regulatory disclosures), this ambiguity is unacceptable.

Ledger-before-state eliminates the ambiguity by construction.

### Implementation pattern

1. Construct a record (proposed state, decision rationale, counterfactuals)
2. Submit the record to the audit ledger (atomic write)
3. If ledger write fails → abort; do not mutate state
4. If ledger write succeeds → execute the state mutation
5. If the state mutation itself fails → record the failure as a follow-up record (the original record stands; the failure is part of the audit trail)

This pattern is closely related to *write-ahead logging* in database literature, applied at the decision-record level rather than the transaction-log level.

### Cost and tradeoffs

Ledger-before-state introduces latency: state mutations cannot complete faster than ledger writes. In low-latency domains (high-frequency trading, real-time control systems), this is a real constraint. The tradeoff is between audit assurance and execution speed.

For audit-grade systems, the latency cost is the price of the assurance. For systems where audit is decorative, the discipline is overkill.

ODS does not normatively require ledger-before-state at any conformance level as of v2.0. It is documented here as the implementation pattern that distinguishes audit-grade adopters from logging-convention adopters. Future versions may incorporate this as a Strict conformance level — currently a deferred Council decision per the 2026-05-26 consolidation session.

## 5. Counterfactual Quality

ODS Core v2 defines `counterfactuals[]` with two fields per item: `alternative_action` and `expected_outcome`. The schema accepts any values that match the field types. It does not distinguish a counterfactual derived from rigorous causal analysis from one invented in the moment to satisfy the schema.

This section provides guidance on what makes a counterfactual informative.

### The provenance question

For any counterfactual, an auditor will eventually ask: *how was the expected_outcome value derived?* Possible answers vary widely in epistemic quality:

- **Observed similar case**: another decision in similar context chose this alternative and produced this outcome. Strong evidence.
- **Synthetic control / matching**: statistical methods constructed a comparable counterfactual from observational data. Moderate evidence.
- **Causal inference**: a formal causal model produced the expected outcome via do-calculus or similar method. Moderate-to-strong evidence depending on model validity.
- **Simulation**: a domain model produced the expected outcome via simulation. Variable evidence depending on simulation calibration.
- **Expert estimate**: a domain expert estimated the outcome based on judgment. Weak-to-moderate evidence.
- **Assumed**: the value was guessed or invented to populate the field. Essentially no evidence.

ODS Core v2 does not currently expose this provenance distinction in the schema. `BACKLOG-003` tracks the candidate addition of `counterfactuals[].methodology` and `counterfactuals[].evidence_quality` fields for v2.1.

### Guidance for current implementations

Until `BACKLOG-003` is resolved in a v2.1 schema update, implementers writing counterfactuals should:

1. Treat the absence of provenance as a defect, not a feature. A counterfactual with no clear derivation method is providing little audit value.
2. Document provenance in the `alternative_action` text where possible (e.g., "redirect to Supplier Y based on observed similar disruption case #4287" rather than just "redirect to Supplier Y").
3. Distinguish *real* counterfactuals (alternatives genuinely considered at decision time) from *ceremonial* ones (alternatives invented post-hoc to satisfy field requirements). Only real counterfactuals provide audit value.

### Future direction

When v2.1 adds explicit provenance fields per `BACKLOG-003`, implementations should migrate to populate them. The non-normative best practice — until that schema update lands — is to document provenance inline in `alternative_action` or in adjacent annotation fields where available.

## 6. Related Reading

- `SPECIFICATION.md` — normative schema and field semantics
- `CONFORMANCE.md` — normative conformance levels and verification rules
- `PROFILES.md` — profile authoring bar and registry
- `VERSIONING.md` — version evolution policy and migration guidance
- `BACKLOG.md` — known gaps and v2.1 candidates
- `adr/ADR-0001` through `adr/ADR-0005` — architectural and governance decisions

### Standards practice precedent

The patterns in this document draw on practice established by mature standards bodies and adjacent disciplines:

- HL7 FHIR Implementation Guides as a model for non-normative companion documents
- Event Sourcing and write-ahead logging literature as a model for ledger-before-state discipline
- WCAG accessibility guidance as a model for non-normative best practices alongside normative criteria
- ISO conformance documentation as a model for audit surface articulation
- Causal inference methodology (Pearl, Imbens, Rubin) as a model for counterfactual provenance

This document is expected to evolve. Council, working groups, and future contributors are encouraged to refine, expand, and challenge its content as practice accumulates and as the ODS adopter base grows.
