---

### File: `xinfer-forge/docs/tutorials/adding-custom-golden-attacks.md`

```markdown
# Embedding Proprietary Zero-Day Signatures into the Safety Gate

Every industrial plant features unique equipment, non-standard Modbus register mappings, or proprietary PLC logic blocks. 

This tutorial walks through capturing a site-specific zero-day attack vector, converting it into a normalized 32-dimensional array, and cryptographically sealing it into `configs/safety/golden_attacks.yaml`.

---

## 1. Capturing and Vectorizing the Attack Flow

When a red-team exercise or localized incident occurs:
1. Extract the malicious flow from the `22_dfir` forensic PCAP vault.
2. Vectorize the flow record into a 32-dimensional floating-point array using Subsystem `ModelConfig`:

```python
import numpy as np

# Extracted 32-dimensional vector for a proprietary chemical dosing pump override
custom_attack_vector = [
    0.085, 240.0, 238.0, 96000.0, 95200.0,
    1420.0, 1420.0, 1420.0, 0.0, 65535.0,
    65535.0, 40.0, 40.0, 1420.0, 1420.0,
    0.0024, 0.0008, 0.0003, 0.0, 0.0,
    2823.0, 1129411.0, 0.0, 0.0, 0.0,
    240.0, 0.0, 0.0, 1.01, 1420.0,
    6.0, 502.0
]
```

---

## 2. Appending to `golden_attacks.yaml`

Edit `configs/safety/golden_attacks.yaml` to register the new attack vector:

```yaml
  # ----------------------------------------------------------------------------
  # Vector 53: Site-Specific Chemical Dosing Over-Pressure Command
  # ----------------------------------------------------------------------------
  - id: "PLANT-MUNICH-DOSE-01"
    name: "Proprietary Dosing Pump High-Pressure Override"
    mitre_attack_id: "T0855"
    protocol: "MODBUS_TCP"
    expected_severity: "CRITICAL"
    vector: [
      0.085, 240.0, 238.0, 96000.0, 95200.0,
      1420.0, 1420.0, 1420.0, 0.0, 65535.0,
      65535.0, 40.0, 40.0, 1420.0, 1420.0,
      0.0024, 0.0008, 0.0003, 0.0, 0.0,
      2823.0, 1129411.0, 0.0, 0.0, 0.0,
      240.0, 0.0, 0.0, 1.01, 1420.0,
      6.0, 502.0
    ]
```

Update the `total_attack_vectors` counter from `52` to `53`.

---

## 3. Re-Sealing to Physical TPM 2.0 Silicon

Re-seal the updated corpus measurement into TPM 2.0 PCR 14 to prevent unauthorized tampering:

```bash
forge-cli validate-safety --update-tpm-seal
```

### Expected Output
```text
[*] Re-calculating SHA-256 Digest of configs/safety/golden_attacks.yaml...
[+] New Corpus Digest: 8a2f3c1e42c994b13a7b41e2d901000000000000000000000000000000000000
[*] Sealing measurement into /dev/tpmrm0 (PCR 14)...
[+] TPM 2.0 Sealing Complete. All future adaptation cycles now enforce Vector 53!
```
```

---

### File: `xinfer-forge/docs/tutorials/tuning-mae-masking-ratio.md`

```markdown
# Tuning the Tabular MAE Masking Ratio for SCADA vs. IT Traffic

In self-supervised learning, the masking ratio controls the difficulty of the reconstruction task. Industrial SCADA traffic (deterministic polling) requires different masking dynamics than enterprise IT traffic (dynamic web/burst traffic).

---

## 1. Comparing Traffic Manifolds

```text
 INDUSTRIAL SCADA TRAFFIC:
  • Low feature variance: 95% of packets are cyclic polls (e.g. Modbus FC 03 every 100ms)
  • High inter-feature correlation: Packet length and byte counts are near-static
  • Optimal Masking Ratio: p_mask = 0.20 to 0.25

 ENTERPRISE IT & CLOUD TRAFFIC:
  • High feature variance: Dynamic payload sizes, random jitter, bursty transfers
  • Moderate inter-feature correlation
  • Optimal Masking Ratio: p_mask = 0.30 to 0.35
```

---

## 2. Experimental Tuning Procedure

Train candidate models with varying masking ratios over the same dataset to observe validation reconstruction loss:

```bash
# Experiment A: Masking Ratio 0.20 (Optimal for Static SCADA)
forge-cli train --data /tmp/scada_flows.csv --masking-ratio 0.20 --epochs 5

# Experiment B: Masking Ratio 0.35 (Optimal for Mixed IT/OT Networks)
forge-cli train --data /tmp/scada_flows.csv --masking-ratio 0.35 --epochs 5
```

### Empirical Results Comparison

| Masking Ratio ($p_{\text{mask}}$) | Baseline Convergence Loss | Outlier Anomaly Separation | False Positive Rate |
| :--- | :--- | :--- | :--- |
| **0.10 (Under-Masked)** | $0.0021$ | Poor ($\Delta_{\text{outlier}} < 0.04$) | $4.2\%$ |
| **0.25 (SCADA Optimal)**| **$0.0078$** | **Exceptional ($\Delta_{\text{outlier}} > 0.22$)** | **$< 0.01\%$** |
| **0.35 (Mixed IT Optimal)**| **$0.0112$** | **Strong ($\Delta_{\text{outlier}} > 0.18$)** | **$0.05\%$** |
| **0.60 (Over-Masked)** | $0.0450$ (High noise) | Degraded (Information collapse) | $8.4\%$ |
```

---

### File: `xinfer-forge/docs/tutorials/recovering-from-poisoning-alerts.md`

```markdown
# Investigating & Recovering from Adversarial Poisoning Rejections

When candidate weights fail the Golden Attacks Safety Gate, `xinfer-forge` triggers the automated purge circuit, deletes the weights, and logs a critical alert. 

This tutorial explains how to investigate why a batch was rejected and how to sanitize training data safely.

---

## 1. Triage Workflow

```text
 [ Purge Circuit Fired: Safety Gate S(θ*) < 1.000 ]
                         │
                         ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Step 1: Inspect Forge Log: /var/log/sentinel/forge_*.log    │
 │  - Identify which specific Golden Attack vector failed      │
 └───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Step 2: Inspect Quarantined Dataset                         │
 │  - Path: /var/lib/sentinel-nexus/quarantine/forge_*.csv     │
 └───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Step 3: Run Anomaly Isolation Script (isolate_poison.py)    │
 │  - Finds cluster pulling decision boundary toward exploit   │
 └───────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Step 4: Sanitize & Resume Autonomous Loop                   │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Step 1: Identifying the Failed Vector

Check the logs to see which attack was missed:

```bash
tail -n 25 /var/log/sentinel/forge_adaptation.log | grep -E 'FAIL|REJECTED'
```

### Sample Output:
```text
[FAIL] ICS-T0855-INDUSTROYER2 (Residual MSE: 0.0412 <= 0.0820)
[!] AUDIT REJECTED: Candidate model failed detection on Industroyer2!
[*] Candidate checkpoint /tmp/candidate_weights.pt securely purged.
```

---

## 3. Step 2: Isolating the Contaminant Data

Run the isolation script against the quarantined CSV:

```python
import numpy as np

# Load quarantined dataset
data = np.loadtxt("/var/lib/sentinel-nexus/quarantine/forge_dataset_8f1c.csv", delimiter=",")

# Check for vectors closely matching the Industroyer2 profile (Port 2404, Type 45/46)
industroyer_matches = []
for idx, row in enumerate(data):
    # Feature 31 is Destination Port (2404 / 65535 = 0.036685)
    if abs(row[31] - (2404.0 / 65535.0)) < 0.001:
        industroyer_matches.append(idx)

print(f"[!] Found {len(industroyer_matches)} flows mimicking IEC 104 switchgear commands!")
```

If these flows were captured during an active attack on the network, an adversary attempted to flood the uncertainty window with attack samples to force the autoencoder to learn them as "normal" baseline traffic.

---

## 4. Step 3: Re-Arming the Daemon

Once the malicious cluster is purged from the quarantine directory, re-enable the autonomous loop:

```bash
sudo systemctl restart sentinel-forge
```
```

---

### File: `xinfer-forge/docs/tutorials/deploying-forge-in-vmware.md`

```markdown
# Deploying Forge Inside the `sentinel-matrix` VMware Mesh

This tutorial demonstrates how to configure and run `xinfer-forge` inside the encapsulated digital twin testbed (`sentinel-matrix`), assigning it static IP **`10.240.0.20`** on the isolated `10.240.0.0/24` subnet.

---

## 1. Container Topology (`10.240.0.0/24`)

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ VMware Hypervisor / Docker-in-VMware Virtual Bridge         │
 ├─────────────────────────────────────────────────────────────┤
 │ Nexus Hub Container       : 10.240.0.10 (gRPC 50051 / 9443) │
 │ Forge AI Trainer Container: 10.240.0.20 (Continual Daemon)  │
 │ Traffic Generator         : 10.240.0.50 (OmniFlow Engine)   │
 │ Red-Team Adversary        : 10.240.0.99 (Malware Replay)    │
 │ Edge Node Appliances      : 10.240.0.101 - 10.240.0.103     │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Docker Compose Configuration (`docker-compose.matrix.yml`)

Ensure the `forge` service is defined with the correct static IP and shared dataset volume:

```yaml
  forge:
    build:
      context: ../xinfer-forge
      dockerfile: Dockerfile
    container_name: sentinel-forge
    hostname: sentinel-forge
    networks:
      matrix_net:
        ipv4_address: 10.240.0.20
    volumes:
      - /opt/sentinel-matrix/shared/datasets:/var/lib/sentinel-nexus/forge_datasets
      - /opt/sentinel-matrix/shared/models:/var/lib/sentinel-nexus/models
      - /opt/sentinel-matrix/shared/certs:/etc/sentinel/certs:ro
    environment:
      - NEXUS_API_URL=https://10.240.0.10:9443
      - FORGE_DEVICE=cpu # Or cuda if NVIDIA container toolkit is mapped
      - LOG_LEVEL=INFO
    restart: always
```

---

## 3. Launching and Validating the Mesh

```bash
# 1. Bring up the simulation grid
cd /opt/sentinel-matrix
make up

# 2. Verify network connectivity from Forge to Nexus Hub
docker exec -it sentinel-forge nc -zv 10.240.0.10 9443
# Output: Connection to 10.240.0.10 9443 port [tcp/*] succeeded!

# 3. Follow Forge continual adaptation logs
docker logs -f sentinel-forge
```
```
