---

### File: `xinfer-forge/docs/troubleshooting/nexus-staging-failures.md`

```markdown
# Nexus Staging Failures & REST API Troubleshooting

This guide resolves errors encountered when `forge-cli stage` dispatches compiled ONNX models to `sentinel-nexus` on port **9443**.

---

## 1. `Connection Refused` on Port 9443

### Symptom
```text
[-] Staging failed: requests.exceptions.ConnectionError: Failed to establish a new connection: [Errno 111] Connection refused
```

### Remediation
1. Verify that `sentinel-nexus` is running:
   ```bash
   sudo systemctl status sentinel-nexus
   ```
2. Verify that the management port is listening on the host:
   ```bash
   ss -tulpn | grep 9443
   ```
3. Check firewall rules:
   ```bash
   sudo ufw status | grep 9443
   ```

---

## 2. HTTP `401 Unauthorized` / JWT Expiration

### Symptom
```text
[-] Staging failed [401]: {"detail": "Signature has expired or token is invalid"}
```

### Remediation
The Bearer token stored in `/etc/sentinel/certs/nexus_token.jwt` has expired. Regenerate the local administrative token:

```bash
nexus-ctl auth refresh-token --output /etc/sentinel/certs/nexus_token.jwt
```

---

## 3. HTTP `422 Unprocessable Entity` (Schema / Hash Mismatch)

### Cause
The streaming SHA-256 digest calculated by `sentinel-nexus` does not match the checksum recorded in `network_threat_v2.manifest.json`.

### Remediation
Ensure the model was exported cleanly without intermediate disk truncation:

```bash
forge-cli export-onnx --checkpoint /tmp/candidate.pt --output-onnx /tmp/verified.onnx
forge-cli stage --onnx-model /tmp/verified.onnx --manifest /tmp/verified.manifest.json
```
```

---

### File: `xinfer-forge/docs/troubleshooting/python-pep668-venv-issues.md`

```markdown
# Resolving Python PEP 668 Virtual Environment Issues

On modern Linux distributions (such as **Ubuntu 24.04 LTS and Ubuntu 26.04**), running `pip install` globally results in a system block:

```text
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
```

---

## 1. Architectural Solution: Isolated Virtualenv

`xinfer-forge` complies strictly with PEP 668 by isolating all Python runtimes, Torch dependencies, and ONNX binaries within **`/opt/sentinel-stack/venv`**.

Do **not** pass `--break-system-packages`, as this risks destabilizing system APT packages.

---

## 2. Rebuilding the Isolated Environment

If the virtual environment becomes corrupted:

```bash
# 1. Purge corrupted environment
sudo rm -rf /opt/sentinel-stack/venv

# 2. Re-create clean virtual environment
sudo python3 -m venv /opt/sentinel-stack/venv

# 3. Upgrade pip wheel tools
sudo /opt/sentinel-stack/venv/bin/pip install --upgrade pip setuptools wheel

# 4. Reinstall forge package
cd /opt/sentinel-stack/xinfer-forge
sudo /opt/sentinel-stack/venv/bin/pip install -r requirements.txt
sudo /opt/sentinel-stack/venv/bin/pip install -e .

# 5. Restore global symlink
sudo ln -sf /opt/sentinel-stack/venv/bin/forge-cli /usr/local/bin/forge-cli
```

---

## 3. Verifying Symlink Resolution

```bash
which forge-cli
# Expected: /usr/local/bin/forge-cli

head -n 1 /usr/local/bin/forge-cli
# Expected: #!/opt/sentinel-stack/venv/bin/python3
```
```

---

### File: `xinfer-forge/docs/troubleshooting/faq.md`

```markdown
# Technical Frequently Asked Questions (FAQ)

---

### Q1: Does `xinfer-forge` require labeled training data?
**No.** `xinfer-forge` uses **self-supervised learning**. It trains on unlabeled ambient network telemetry using **Masked Autoencoders (MAE)** and **InfoNCE contrastive learning**, learning the underlying physical and protocol relationships directly from normal traffic.

---

### Q2: Can `xinfer-forge` train models on multi-core CPUs without a GPU?
**Yes.** Because the `TabularMAE` topology is lightweight ($1{,}632\text{ parameters}$), training on a 5,000-flow batch across 5 epochs completes in **$< 20\text{ seconds}$ on a standard 4-core Intel or ARM64 CPU**. A discrete GPU is optional.

---

### Q3: How does Forge protect against adversarial data poisoning?
Every candidate model must pass the **immutable Golden Attacks Safety Gate** (`configs/safety/golden_attacks.yaml`). If an adversary injects perturbations into the training data to desensitize the model to a historical exploit (e.g., Stuxnet or Industroyer), the candidate model will fail detection during safety evaluation and be purged immediately.

---

### Q4: Does retraining cause downtime on edge defense appliances?
**No.** When candidate weights are approved, compiled, and deployed, edge appliances (`blackbox-sentinel`) perform an in-memory atomic pointer swap via `POST /api/v1/control/reload-model`. The active eBPF packet mitigation filter continues dropping packets with **zero downtime**.

---

### Q5: What happens if an edge appliance is completely air-gapped?
`xinfer-forge` executes 100% on-premises within the local security perimeter. It generates zero external network requests and incurs **$0.00 cloud egress fees**.
```

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

