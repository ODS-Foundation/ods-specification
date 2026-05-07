# Security Policy

## Reporting Vulnerabilities

The ODS Foundation takes security seriously. We appreciate your efforts to responsibly disclose vulnerabilities in the ODS specification or reference implementations.

---

## How to Report

**For security vulnerabilities, please DO NOT open a public GitHub issue.**

Instead, report security issues through one of these channels:

### Preferred: GitHub Security Advisories

1. Go to the [Security tab](https://github.com/ODS-Foundation/ods-specification/security)
2. Click "Report a vulnerability"
3. Fill in the details

### Alternative: Private Email

Send a detailed report to: **security@ods-foundation.org** *(coming soon)*

For now, use GitHub Security Advisories.

---

## What to Include

To help us understand and address the issue quickly, please include:

- **Description** of the vulnerability
- **Type** of issue (e.g., schema flaw, cryptographic weakness, implementation gap)
- **Step-by-step reproduction**
- **Affected versions** of ODS
- **Potential impact** assessment
- **Suggested fix** (if applicable)
- **Your contact information** for follow-up questions

---

## Response Timeline

We commit to:

| Timeline | Action |
|----------|--------|
| **24 hours** | Initial acknowledgment of report |
| **72 hours** | Severity assessment completed |
| **7 days** | Mitigation strategy proposed |
| **30 days** | Fix released (for critical issues) |
| **90 days** | Public disclosure (coordinated) |

---

## Severity Classification

We classify vulnerabilities using CVSS 3.1:

- **Critical (9.0-10.0):** Immediate action required; affects core trust model
- **High (7.0-8.9):** Significant security impact; mitigation prioritized
- **Medium (4.0-6.9):** Moderate security impact; addressed in next release
- **Low (0.1-3.9):** Minor security improvement; addressed in regular cycle

---

## Disclosure Policy

We follow **coordinated disclosure**:

1. Report received privately
2. Validation and severity assessment
3. Fix developed and tested
4. Patch released to all known implementers
5. Public advisory published (typically 30-90 days after report)
6. CVE assigned (for significant vulnerabilities)

---

## Scope

This security policy covers:

✅ The ODS specification itself  
✅ The reference implementation (if hosted in this organization)  
✅ Schema validation tools  
✅ Cryptographic verification mechanisms  

This policy does NOT cover:

❌ Third-party implementations (report to those vendors)  
❌ Issues in dependencies (report upstream)  
❌ User errors or misconfigurations  

---

## Recognition

We recognize security researchers who responsibly disclose vulnerabilities:

- **Hall of Fame** — Listed in our security acknowledgments
- **Public credit** in security advisories (with permission)
- **CVE attribution** for significant findings

---

## Bug Bounty

Currently, the ODS Foundation does not offer a paid bug bounty program. However:

- Responsible disclosures are highly valued
- Recognition is provided
- Future bug bounty programs will be announced if established

---

## Security Best Practices for Implementers

When implementing ODS, follow these security guidelines:

### Cryptographic Requirements

- ✅ Use SHA-256 minimum for hashing (per specification)
- ✅ Implement Merkle trees correctly for batch verification
- ✅ Store cryptographic keys securely (HSM recommended)
- ✅ Rotate keys according to your security policy

### Storage Security

- ✅ Use append-only storage with WORM guarantees
- ✅ Encrypt data at rest
- ✅ Encrypt data in transit (TLS 1.3+)
- ✅ Implement proper access controls
- ✅ Audit all access to decision data

### API Security

- ✅ Use strong authentication (OAuth 2.0, JWT)
- ✅ Implement rate limiting
- ✅ Validate all inputs
- ✅ Log all API access
- ✅ Use HTTPS only

### Implementation Security

- ✅ Keep dependencies updated
- ✅ Run security scans regularly
- ✅ Conduct penetration testing
- ✅ Follow OWASP guidelines
- ✅ Use static analysis tools

---

## Contact

For security-related questions or concerns:

- **GitHub Security:** [Security Advisories](https://github.com/ODS-Foundation/ods-specification/security)
- **Public Discussions:** [GitHub Discussions](https://github.com/ODS-Foundation/ods-specification/discussions) (non-sensitive only)

---

**Security is a shared responsibility.**

🏛️ ODS Foundation
