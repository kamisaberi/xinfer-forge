# Architecture at a Glance

The diagram below maps the interaction between real-time network traffic ingestion, uncertainty-based active learning selection, self-supervised continual learning in `xinfer-forge`, and Canary deployment to the edge fleet.

---

```text
                                [ PHYSICAL NETWORK WIRE ]
                                            │
                                            ▼ Packets (< 0.84 µs Mitigation)
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │ Tier 3: Blackbox-Sentinel Edge Appliance (sentinel daemon)                               │
 │  - Protocol Dissectors decode Modbus / S7 / DNP3                                         │
 │  - Inference Engine (network_threat_v1.onnx) scores incoming 32-dim flow vectors         │
 └──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                            │
                                            ▼ Uncertainty Selection: Score in [0.40 - 0.60]
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │ Tier 6: Sentinel-Nexus Hub (DatasetCurator.cpp)                                          │
 │  - Batches 5,000 high-uncertainty flows into:                                            │
 │    /var/lib/sentinel-nexus/forge_datasets/forge_dataset_<uuid>.csv                       │
 └──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                            │
                                            ▼ File Watcher / forge-cli auto-cycle
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │ Tier 4: xinfer-forge Continual Learning Engine                                           │
 │                                                                                          │
 │  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ 1. Self-Supervised Training Loop                                                   │  │
 │  │    • 30% Random Tabular Masking (MAE)                                              │  │
 │  │    • InfoNCE Contrastive Regularization (Spatial-Temporal Flow Alignment)          │  │
 │  └───────────────────────────────────────┬────────────────────────────────────────────┘  │
 │                                          │ Candidate Weights (θ*)                         │
 │                                          ▼                                               │
 │  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ 2. Golden Attacks Safety Gate (configs/safety/golden_attacks.yaml)                  │  │
 │  │    • Benchmarks θ* against Stuxnet, Triton, Industroyer, and C2 Exploits           │  │
 │  │    • Zero-Tolerance: Requires S(θ*) == 1.000 (100% Detection Rate)                 │  │
 │  │    • If Miss >= 1 Attack ──► AUTOMATIC PURGE & ALERT CISO                          │  │
 │  └───────────────────────────────────────┬────────────────────────────────────────────┘  │
 │                                          │ Passed Verification                           │
 │                                          ▼                                               │
 │  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ 3. Automated ONNX Opset 17 Stager                                                  │  │
 │  │    • Compiles PyTorch -> network_threat_v2.onnx                                    │  │
 │  │    • Computes SHA-256 Checksum                                                     │  │
 │  │    • Dispatches REST API: POST /api/v1/ota/stage                                   │  │
 │  └────────────────────────────────────────────────────────────────────────────────────┘  │
 └──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                            │
                                            ▼ Canary 5% -> Fleet-Wide Rollout (< 50ms Bus)
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │ Production Fleet Appliances (Hot Reload via POST /api/v1/control/reload-model)           │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
```

