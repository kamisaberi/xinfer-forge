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

