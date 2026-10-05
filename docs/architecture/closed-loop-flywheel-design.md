---

### File: `xinfer-forge/docs/architecture/closed-loop-flywheel-design.md`

```markdown
# The Closed-Loop Active Learning Flywheel

`xinfer-forge` operates as the central adaptation engine in an autonomous active learning flywheel. It connects edge inference appliances (`blackbox-sentinel`) and fleet orchestration hubs (`sentinel-nexus`) in a continuous improvement loop.

---

## 1. Flywheel Data Flow

```text
                     [ INDUSTRIAL NETWORK TRAFFIC ]
                                   │
                                   ▼ Ingress Slices (< 0.84 µs Mitigation)
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ Step 1: Edge Inference Execution (Tier 3: blackbox-sentinel)                │
 │  - Model network_threat_v1.onnx scores 32-dim flow vectors                  │
 │  - Unambiguous threats (Score > 0.85) dropped in driver space               │
 │  - Unambiguous benign (Score < 0.10) passed to host stack                   │
 └─────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼ Uncertainty Selection: Score ∈ [0.40, 0.60]
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ Step 2: Telemetry Batch Curation (Tier 6: sentinel-nexus)                   │
 │  - DatasetCurator.cpp isolates ambiguous flows (Edge Cases)                 │
 │  - Emits: /var/lib/sentinel-nexus/forge_datasets/forge_dataset_<uuid>.csv   │
 └─────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼ Inotify Watcher Trigger
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ Step 3: Continual Self-Supervised Adaptation (Tier 4: xinfer-forge)         │
 │  - 30% Stochastic Feature Masking (Tabular MAE)                             │
 │  - InfoNCE Contrastive Regularization                                       │
 │  - Produces candidate checkpoint: candidate_weights.pt                      │
 └─────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼ Golden Attacks Safety Gate Pass (100% Score)
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ Step 4: ONNX Opset 17 Compilation & Cryptographic Staging                   │
 │  - Compiles candidate weights to network_threat_v2.onnx                     │
 │  - Dispatches POST /api/v1/ota/stage payload to sentinel-nexus              │
 └─────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼ Staged Canary Deployment (< 50ms Sync)
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ Step 5: Zero-Downtime Hot Reload across Edge Fleet                          │
 │  - Edge nodes reload weights via POST /api/v1/control/reload-model          │
 │  - Newly adapted model resolves previously ambiguous edge cases             │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Active Learning Uncertainty Boundary

Instead of retraining on millions of redundant, obvious flows, the flywheel isolates ambiguous traffic:

$$\text{Uncertainty Filter}(x) = \{ x \mid 0.40 \le f(x; \theta) \le 0.60 \}$$

This focuses training computations on edge cases and emerging environmental variations, reducing compute requirements by up to **$94\%$**.
```

---
