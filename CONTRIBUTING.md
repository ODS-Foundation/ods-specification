# Contributing to ODS

Thank you for your interest in contributing to the **Operational Decision Standard (ODS)**. We welcome contributions from organizations, researchers, developers, and standards experts.

---

## 🎯 How to Contribute

ODS is governed through an open RFC (Request for Comments) process. Contributions can take several forms:

### Types of Contributions Welcome

1. **Schema Improvements** — Propose changes or additions to the seven-layer schema
2. **Implementation Examples** — Reference implementations in different languages
3. **Use Case Documentation** — Real-world applications of ODS
4. **Compliance Tooling** — Validators, auditors, certification tools
5. **Bug Reports** — Identify ambiguities, errors, or gaps in the specification
6. **Documentation** — Improve clarity, examples, or translations

---

## 📋 RFC Process for Schema Changes

For substantive changes to the ODS specification, follow the RFC process:

### Step 1: Open an RFC Issue

1. Use the [RFC Template](.github/ISSUE_TEMPLATE/rfc.md)
2. Title format: `[RFC-XXX] Brief description of proposal`
3. Include:
   - **Motivation** — Why is this change needed?
   - **Proposed Change** — Detailed specification of the change
   - **Backward Compatibility** — How existing implementations are affected
   - **Reference Implementation** — Code examples or proof-of-concept
   - **Alternatives Considered** — Other approaches and why they were rejected

### Step 2: Community Review (30 days minimum)

- Open discussion in the RFC issue
- Solicit feedback from implementers
- Respond to questions and concerns
- Iterate on the proposal

### Step 3: Technical Committee Review

- ODS Foundation Technical Committee reviews
- Decision: Accept / Reject / Request Changes
- If accepted, merged into next minor or major version

### Step 4: Implementation and Publication

- Implementation in next ODS version
- Documentation updated
- CHANGELOG entry
- Public announcement

---

## 🐛 Reporting Bugs

For specification bugs (ambiguities, errors, missing fields):

1. Open an issue using [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
2. Include:
   - **Section reference** (e.g., Section 3.2.4)
   - **Description of the issue**
   - **Expected behavior**
   - **Suggested fix** (if applicable)

---

## 💡 Feature Requests

For non-breaking enhancements:

1. Open an issue using [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)
2. Describe:
   - **Use case**
   - **Proposed solution**
   - **Why it benefits the broader ODS community**

---

## 🔄 Pull Request Process

### For Documentation Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b improve-docs/section-name`)
3. Make your changes
4. Submit a pull request
5. Reference any related issues

### For Specification Changes

1. **First**, open an RFC issue (see above)
2. Wait for RFC acceptance
3. Then submit a PR implementing the accepted RFC
4. Reference the RFC issue in the PR description

### PR Requirements

- ✅ Clear, descriptive title
- ✅ Detailed description of changes
- ✅ Reference to related issues/RFCs
- ✅ Updated CHANGELOG.md (for accepted changes)
- ✅ No merge conflicts
- ✅ Passes all automated checks

---

## 📐 Style Guidelines

### Documentation

- Use clear, professional English
- Define technical terms on first use
- Provide examples for complex concepts
- Use consistent terminology (see [Glossary](./SPECIFICATION.md#appendix-c-glossary))

### Code Examples

- Python is the preferred language for examples
- Include type hints
- Add docstrings
- Follow PEP 8

### Markdown

- Use ATX-style headers (`#` not underlines)
- Code blocks with language hints (```python)
- Tables for structured comparisons
- Emoji sparingly for visual clarity

---

## 🌐 Community

### Communication Channels

- **GitHub Issues** — Bug reports, RFCs, feature requests
- **GitHub Discussions** — General questions, community chat
- **Email** — ods@orpi.systems for security or sensitive matters

### Code of Conduct

All contributors are expected to follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

We are committed to:
- ✅ Welcoming environment for all
- ✅ Respectful, professional discourse
- ✅ Focus on technical merit
- ✅ Inclusive language

---

## 🏛️ Governance

ODS is maintained by the **ODS Foundation**, a community-driven standards body.

### Technical Committee

The Technical Committee makes final decisions on:
- RFC acceptance/rejection
- Major version releases
- Compliance certification standards

Membership is appointed based on technical contributions and community engagement.

### Decision Process

1. **Consensus first** — Aim for community agreement
2. **Technical merit** — Decisions based on engineering quality
3. **Transparency** — All decisions documented publicly
4. **Inclusivity** — Diverse perspectives valued

---

## 📜 Licensing

By contributing to ODS, you agree that your contributions will be licensed under the **Apache License 2.0**.

This means:
- ✅ Your contributions can be used commercially
- ✅ Your contributions can be modified and distributed
- ✅ Attribution will be maintained

---

## 🙏 Recognition

All contributors are recognized in:
- Repository contributors list
- Release notes for accepted RFCs
- Annual ODS Foundation reports

---

## 🚀 Getting Started

Ready to contribute? Here's how:

1. **Read the specification** — [SPECIFICATION.md](./SPECIFICATION.md)
2. **Review open issues** — [GitHub Issues](https://github.com/ODS-Foundation/ods-specification/issues)
3. **Join discussions** — [GitHub Discussions](https://github.com/ODS-Foundation/ods-specification/discussions)
4. **Start small** — Documentation improvements are great first contributions

---

## ❓ Questions?

- General questions: [GitHub Discussions](https://github.com/ODS-Foundation/ods-specification/discussions)
- Specific issues: [GitHub Issues](https://github.com/ODS-Foundation/ods-specification/issues)
- Private matters: ods@orpi.systems

---

**Thank you for helping build the future of decision governance.**

🏛️ ODS Foundation
