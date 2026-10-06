# End-to-End Retraining on Raw Industrial Network Captures

This tutorial demonstrates how to extract continuous 32-dimensional telemetry vectors from raw industrial network traffic (PCAP or NetFlow feeds), train a `TabularMAE` candidate model, verify safety compliance, and export an updated ONNX model.

---

## 1. Pipeline Overview

```text
 [ Industrial Subnet (Modbus / S7 / DNP3) ]
                     │
                     ▼ Raw PCAP Capture (tcpdump / mirror port)
 [ traffic.pcap (10,000 Flows) ]
                     │
                     ▼ Feature Extraction via Subsystem ModelConfig
 [ ambient_flows.csv (10,000 Rows x 32 Float Columns) ]
                     │
                     ▼ forge-cli train
 [ candidate_weights.pt (PyTorch Checkpoint) ]
                     │
                     ▼ forge-cli validate-safety
 [ Verified against configs/safety/golden_attacks.yaml ]
                     │
                     ▼ forge-cli export-onnx
 [ network_threat_v2.onnx (Opset 17) Ready for Staging ]
```

---

## 2. Step 1: Ingest and Normalize Raw Flows

Use the extraction utility in `xinfer-forge` to convert packet captures into normalized 32-dimensional continuous flow vectors:

```bash
python3 -m forge.data.pcap_extractor \
    --input-pcap /var/log/sentinel/traffic_capture.pcap \
    --output-csv /tmp/ambient_flows.csv \
    --sliding-window-sec 2.0
```

Verify that the output contains 32 normalized floating-point columns:

```bash
head -n 2 /tmp/ambient_flows.csv | awk -F',' '{print NF " columns detected"}'
# Output: 32 columns detected
```

---

## 3. Step 2: Train the Masked Autoencoder

Execute self-supervised training using `forge-cli train`:

```bash
forge-cli train \
    --data /tmp/ambient_flows.csv \
    --epochs 5 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --masking-ratio 0.30 \
    --output-checkpoint /tmp/candidate_weights.pt
```

### Expected Output
```text
[*] Initializing TabularMAE Topology: 32 -> 16 -> 8 -> 16 -> 32
[*] Training Device: cuda:0 (NVIDIA RTX A4000)
[*] Ingested: 10,000 samples
Epoch 1/5 [========================================] Loss: 0.0341 (MAE: 0.0305, InfoNCE: 0.0036)
Epoch 2/5 [========================================] Loss: 0.0210 (MAE: 0.0189, InfoNCE: 0.0021)
Epoch 3/5 [========================================] Loss: 0.0145 (MAE: 0.0131, InfoNCE: 0.0014)
Epoch 4/5 [========================================] Loss: 0.0108 (MAE: 0.0098, InfoNCE: 0.0010)
Epoch 5/5 [========================================] Loss: 0.0089 (MAE: 0.0081, InfoNCE: 0.0008)
[+] Candidate checkpoint saved: /tmp/candidate_weights.pt
```

---

## 4. Step 3: Enforce the Golden Attacks Safety Gate

Verify that the adapted model has not suffered catastrophic forgetting or incorporated malicious baseline drift:

```bash
forge-cli validate-safety \
    --checkpoint /tmp/candidate_weights.pt \
    --safety-corpus /opt/sentinel-stack/xinfer-forge/configs/safety/golden_attacks.yaml
```

If the score returns `1.000`, proceed to export:

```bash
forge-cli export-onnx \
    --checkpoint /tmp/candidate_weights.pt \
    --output-onnx /opt/sentinel/models/network_threat_v2.onnx \
    --model-version 2.4.0
```

