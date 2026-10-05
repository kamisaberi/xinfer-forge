
### File: `xinfer-forge/docs/index.md`

```markdown
# xInfer Forge (`forge-cli`)

**Continual Edge Learning, Self-Supervised Tabular MAE & Anti-Poisoning Gate**  
*Tier 4 Active Adaptation Engine of the Aryorithm / Blackbox Sentinel Ecosystem*

---

## Executive Architectural Overview

`xinfer-forge` is an edge-native, continuous self-supervised active learning daemon and CLI toolsuite (`forge-cli`). It solves the fundamental degradation problem in cybersecurity AI: **concept drift** in operational networks and **adversarial data poisoning** ("boiling-the-frog" attacks).

Operating entirely on-premises without cloud connectivity ($0.00 data egress), `xinfer-forge` fine-tunes 32-dimensional cyber-physical flow representations using **Masked Autoencoders (MAE)** and **InfoNCE contrastive learning**.

Before any fine-tuned candidate model can be compiled or deployed to edge appliances, it must pass through an **immutable, zero-tolerance Golden Attacks Safety Gate** (`configs/safety/golden_attacks.yaml`). If candidate weights miss even a single historical attack, the weights are purged from disk.

```text
====================================================================================================
                        XINFER-FORGE CONTINUAL ADAPTATION PIPELINE
====================================================================================================
 [EDGE SENSORS]                UNLABELED WIRE FLOWS (Ingress Packets & SCADA Telemetry)
                                                │
                                                ▼ Prediction Uncertainty Window [0.40 - 0.60]
 [TIER 6: CURATION]            SENTINEL-NEXUS: DatasetCurator.cpp
                               (Batches 5,000 ambiguous flows -> forge_dataset_*.csv)
                                                │
                                                ▼ File Discovery / Inotify Trigger
 [TIER 4: CONTINUAL ENGINE]    XINFER-FORGE (forge-cli auto-cycle)
                               │
                               ├── 1. Self-Supervised Training
                               │      • 30% Random Masking (Tabular MAE)
                               │      • InfoNCE Temporal Contrastive Regularization
                               │      • Latent Bottleneck Compression (z in R^8)
                               │
                               ├── 2. Anti-Poisoning Safety Gate (configs/safety/golden_attacks.yaml)
                               │      • Stuxnet S7 Injection (T0831)
                               │      • Triton Emergency Shutdown Override (T0843)
                               │      • Industroyer High-Voltage Switchgear Trip (T0855)
                               │      • C2 Beaconing & Exfiltration (T1071)
                               │      │
                               │      ├── [FAIL: Missed >= 1 Attack] ──► HARD PURGE CANDIDATE
                               │      │                                  Emit Critical Security Alert
                               │      └── [PASS: 100% Detection]     ──► PROCEED TO EXPORT
                               │
                               └── 3. Compilation & Fleet Staging
                                      • Compile PyTorch -> ONNX (Opset 17, Dynamic Batch Axes)
                                      • Compute SHA-256 Checksum Manifest
                                      • Dispatch POST /api/v1/ota/stage to Sentinel-Nexus
                                                │
                                                ▼ Canary 5% -> Fleet-Wide Rollout (< 50ms Bus)
 [TIER 3: EDGE INFERENCE]      BLACKBOX-SENTINEL (libxinfer.so Zero-Copy Engine)
====================================================================================================
```

---

## Core Invariants

1. **Continual Autonomy:** Automatically detects, ingests, and adapts to ambient network drift without requiring manual human labeling or data science oversight.
2. **Zero-Tolerance Anti-Poisoning Invariant:** Candidate model weights that fail to detect $100.00\%$ of historical exploits in the immutable golden attack corpus are purged automatically ($S(\theta^*) = 1.000$).
3. **Data Sovereignty ($0.00 Egress):** 100% on-premises edge execution. Raw payload vectors and fine-tuned weights never leave the customer's security boundary.
4. **Standardized Hardware Portability:** Compiles directly to **ONNX Opset 17** with dynamic batch dimensions (`[batch_size, 32]`), ready for immediate zero-copy ingestion across all 15 silicon targets in `libxinfer.so`.
```

