### Part 11: Troubleshooting & Help Desk Diagnostics (`troubleshooting/*`)

This final section covers numerical stability troubleshooting, safety gate rejection diagnosis, Nexus REST API staging connectivity, Python PEP 668 virtual environment resolution, technical FAQs, and enterprise support SLAs for `xinfer-forge`.

---

### File: `xinfer-forge/docs/troubleshooting/loss-divergence-and-nans.md`

```markdown
# Resolving Loss Divergence, Exploding Gradients & NaNs

During continual retraining on uncurated ambient network telemetry, anomalous outliers (e.g., massive byte bursts or unnormalized port values) can cause numerical instability, leading to gradient explosion and `NaN` (Not-a-Number) loss values.

---

## 1. Primary Causes of Training Divergence

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Common Causes of NaN Loss in Tabular MAE                    │
 ├─────────────────────────────────────────────────────────────┤
 │ 1. Unnormalized Feature Columns (Raw bytes > 10^8)          │
 │ 2. Learning Rate Too High (> 0.01 without Warmup)           │
 │ 3. Division by Zero in InfoNCE Temperature Scaling (τ → 0)  │
 │ 4. Exploding Gradients across Linear Bottleneck Projections │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. In-Engine Safeguards & Remediation

### 1. Enforcing Gradient Value & Norm Clipping
`xinfer-forge` includes automated gradient clipping. If running custom scripts, ensure `clip_grad_norm_` is enforced prior to the optimizer step:

```python
# Scale gradients to prevent explosive weight updates
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

### 2. Validating Input Tensors for NaNs or Infs
Before beginning an epoch, inspect the input batch for corrupted floating-point values:

```python
if torch.isnan(batch_x).any() or torch.isinf(batch_x).any():
    raise ValueError("Input batch contains NaN or Infinite values! Check feature normalizer.")
```

### 3. Lowering the Learning Rate
If loss diverges during the first epoch, reduce the initial step size:

```bash
forge-cli train --data /tmp/ambient_flows.csv --learning-rate 0.0001 --epochs 5
```
```

---

### File: `xinfer-forge/docs/safety-regression-gate/safety-gate-rejection-guide.md`

```markdown
# Safety Gate Rejection Diagnostics & Remediation

When candidate weights fail the Golden Attacks Safety Gate, `forge-cli` exits with code `2` (`EXIT_SAFETY_VIOLATION`), logs the failure to `/var/log/sentinel/forge_adaptation.log`, and purges the checkpoint file.

---

## 1. Diagnosing Failed Attack Vectors

Inspect the adaptation log to identify the specific attack vector that dropped below threshold $\tau = 0.082$:

```bash
tail -n 30 /var/log/sentinel/forge_adaptation.log | grep -A 2 -B 2 "FAIL"
```

### Sample Log Trace:
```text
[INFO] Evaluating Vector 14/52: ICS-T0843-TRITON
[FAIL] ICS-T0843-TRITON: Observed Residual MSE 0.0412 <= Required Threshold 0.0820
[!] CRITICAL: Regression detected on Triton TriStation emergency shutdown override!
[*] Purge circuit executed: Unlinking candidate checkpoint /tmp/candidate_weights.pt
```

---

## 2. Common Causes & Fixes

| Root Cause | Diagnostic Indicator | Remediation Step |
| :--- | :--- | :--- |
| **Overfitting on Small Batch** | Sample count $< 1{,}000$ rows in dataset. | Increase minimum batch threshold in `DatasetCurator.cpp` to $\ge 5{,}000$ flows. |
| **Learning Rate Too High** | Early layer features destroyed after Epoch 1. | Reduce `--learning-rate` to `0.0005` with Cosine Annealing. |
| **Adversarial Poisoning** | Quarantined CSV contains clusters closely matching the missed exploit. | Purge the contaminated batch from `/var/lib/sentinel-nexus/forge_datasets/`. |
| **Corrupted Normalization** | Feature values exceed $[0.0, 1.0]$ bounds. | Re-validate min-max clamping rules in `model_config.yaml`. |
```

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

