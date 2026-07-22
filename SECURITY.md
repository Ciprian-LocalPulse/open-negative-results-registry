# Security Policy

> *"Robust security architecture and responsible vulnerability disclosure are fundamental to preserving the integrity of open-source medical infrastructures."*
> **— Ciprian Stefan Plesca, Independent Researcher**

---

The **Open Negative Results Registry (ONRR)** is committed to maintaining the highest standards of data security, operational resilience, and infrastructural integrity. Given the sensitive nature of biomedical research metadata and open-source scientific repositories, we take security vulnerabilities extremely seriously. 

Authored and overseen by **Ciprian Stefan Plesca, Independent Researcher**, this security policy outlines our protocol for reporting vulnerabilities and maintaining a secure ecosystem for global research collaboration.

---

## 🚨 Supported Versions

Security updates and patches are exclusively deployed to the current active release branch of the repository. Users are strongly advised to maintain deployment instances synchronized with the latest version hosted in the official GitHub repository or GitHub Container Registry (GHCR).

| Version | Supported |
| :--- | :--- |
| `latest` (Active Development) | ✅ Yes |
| Older / Legacy Releases | ❌ No |

---

## 🔒 Reporting a Vulnerability

If you discover a security vulnerability, architectural flaw, or potential data exposure vector within the ONRR repository or its containerized distribution packages, **do not open a public GitHub Issue**. Public disclosures can expose infrastructure before a mitigating patch can be deployed.

Instead, please report vulnerabilities privately through our designated reporting channels:

* **Private Vulnerability Reporting:** Utilize the **Private vulnerability reporting** feature enabled on our [GitHub Security Tab](https://github.com/Ciprian-LocalPulse/open-negative-results-registry/security/advisories) to submit findings confidentially.
* **Direct Communication:** For critical security matters requiring direct coordination, contact the lead researcher and project maintainer, **Ciprian Stefan Plesca**, through official repository communication channels.

### Information to Include in Your Report:
To expedite verification and remediation, please provide a comprehensive technical description containing:
1. Type of vulnerability (e.g., Remote Code Execution, Authentication Bypass, Injection Flaw).
2. Step-by-step instructions or proof-of-concept (PoC) code to reproduce the issue safely.
3. Potential impact assessment on system integrity or participant data privacy.

---

## ⏱️ Response and Disclosure Timeline

Upon receiving a private disclosure report, our security oversight protocol adheres to the following timeline:
* **Acknowledgment:** Initial triage and response within **48 to 72 hours**.
* **Assessment & Remediation:** Collaborative patch development and verification proportional to the severity level.
* **Public Disclosure:** Public advisory publication following successful patch deployment, crediting the reporting security researcher (unless anonymity is requested).

---

## ⚖️ Responsible Disclosure Commitment

We deeply appreciate security researchers and community contributors who act in good faith to identify and report vulnerabilities. We pledge not to pursue legal action against researchers who report security flaws following responsible disclosure guidelines, provided they refrain from exploiting the vulnerability, accessing unauthorized data, or disrupting live services.