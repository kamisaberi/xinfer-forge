---

### File: `xinfer-forge/docs/troubleshooting/support.md`

```markdown
# Enterprise Support SLAs & Incident Escalation

---

## 1. Automated Diagnostic Bundle Generation

When reporting a training failure, numerical divergence, or unexpected safety gate rejection, generate an automated diagnostic bundle:

```bash
forge-cli diag --full --output /tmp/forge_diagnostic_bundle.tar.gz
```

This bundle packages:
* Host hardware specifications, CPU topology, and GPU compute capabilities.
* Python virtual environment dependency manifests (`pip freeze`).
* Active training hyperparameter configurations (`forge_config.yaml`).
* Last 500 lines of adaptation logs from `/var/log/sentinel/forge_adaptation.log`.
* Anonymized loss curves and safety gate evaluation summaries.

---

## 2. Enterprise Commercial Support SLAs

Aryorithm Technologies B.V. provides commercial support for defense and critical infrastructure networks:

| Support Tier | Target Response Time | Availability | Scope |
| :--- | :--- | :--- | :--- |
| **Standard Support** | 8 Business Hours | Mon–Fri 08:00–18:00 CET | Configuration review, updates, bug patches. |
| **Mission-Critical Defense**| **1 Hour (24/7/365)** | Round-the-Clock | Dedicated AI systems engineer, model tuning, custom safety corpus development, on-site audits. |

For technical inquiries and enterprise SLA contracts:
* **Customer Portal:** `https://app.aryorithm.com/support`
* **Email:** `support@aryorithm.com`

---

## 3. Coordinated Security Vulnerability Disclosure

If you identify an adversarial evasion vector, safety gate bypass, or potential vulnerability in `xinfer-forge`:
* Send an encrypted PGP message to **`security@aryorithm.com`**.
* We acknowledge disclosures within **48 hours** and provide CVE assignment, risk remediation, and backported security patches according to coordinated disclosure guidelines.
```

