---

### File: `xinfer-forge/docs/getting-started/quickstart-first-adaptation.md`

```markdown
# 5-Minute Quickstart: Your First Model Adaptation Run

This walkthrough guides you through executing a 5-minute training and validation cycle on a mock 32-dimensional NetFlow batch using `forge-cli`.

---

## 1. Generate Synthetic Training Telemetry

Generate a mock batch of 1,000 baseline network flows representing ambient industrial traffic:

```bash
mkdir -p /tmp/forge_quickstart
python3 -c "
import numpy as np
# 1,000 flows x 32 normalized continuous dimensions
data = np.random.uniform(0.1, 0.4, size=(1000, 32)).astype(np.float32)
np.savetxt('/tmp/forge_quickstart/ambient_flows.csv', data, delimiter=',', fmt='%.6f')
print('[+] Created mock batch: /tmp/forge_quickstart/ambient_flows.csv')
"
```

---

## 2. Run the Continual Training Engine

Invoke `forge-cli train` pointing to the mock batch:

```bash
forge-cli train \
    --data /tmp/forge_quickstart/ambient_flows.csv \
    --epochs 5 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --masking-ratio 0.30 \
    --output-checkpoint /tmp/forge_quickstart/candidate_weights.pt
```

### Terminal Output
```text
[*] Initializing Masked Autoencoder (MAE) Topology: 32 -> 16 -> 8 -> 16 -> 32
[*] Running on Device: cpu
[*] Dataset Loaded: 1,000 samples (32 dimensions)
Epoch 1/5 [========================================] Loss: 0.0412 (MAE: 0.0381, InfoNCE: 0.0031)
Epoch 2/5 [========================================] Loss: 0.0289 (MAE: 0.0264, InfoNCE: 0.0025)
Epoch 3/5 [========================================] Loss: 0.0194 (MAE: 0.0175, InfoNCE: 0.0019)
Epoch 4/5 [========================================] Loss: 0.0142 (MAE: 0.0129, InfoNCE: 0.0013)
Epoch 5/5 [========================================] Loss: 0.0118 (MAE: 0.0108, InfoNCE: 0.0010)
[+] Candidate checkpoint saved: /tmp/forge_quickstart/candidate_weights.pt
```

---

## 3. Audit Candidate Weights Through the Safety Gate

Verify that the adapted weights detect all entries in the golden attack suite:

```bash
forge-cli validate-safety \
    --checkpoint /tmp/forge_quickstart/candidate_weights.pt \
    --safety-corpus configs/safety/golden_attacks.yaml
```

### Expected Output
```text
================================================================================
                    IMMUTABLE GOLDEN ATTACKS REGRESSION GATE
================================================================================
Evaluating Corpus: configs/safety/golden_attacks.yaml (52 Historic Exploits)

 [PASS] CVE-2017-0144 (EternalBlue SMB Injection)       : Residual MSE 0.284 > 0.082
 [PASS] ICS-T0855 (Industroyer2 Switchgear Override)    : Residual MSE 0.341 > 0.082
 [PASS] ICS-T0843 (Triton Safety Instrumented Shutdown) : Residual MSE 0.412 > 0.082
 [PASS] ICS-T0831 (Stuxnet S7 Centrifuge Frequency)     : Residual MSE 0.298 > 0.082
 ... (48 additional attack vectors evaluated)

--------------------------------------------------------------------------------
Regression Audit Result: 52/52 Attacks Detected (Score: 1.000 / Required: 1.000)
Status: CANDIDATE MODEL IS CRYPTOGRAPHICALLY SECURE & APPROVED FOR ONNX EXPORT.
================================================================================
```
```

