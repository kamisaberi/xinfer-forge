### Part 2: Deep Systems Design (`architecture/*`)

This section contains 5 architectural specifications detailing the systems design of `xinfer-forge`: the continual learning event loop, mathematical formulations of concept drift and adversarial poisoning, the closed-loop fleet flywheel, and the air-gapped execution model.

---

### File: `xinfer-forge/docs/architecture/continual-learning-architecture.md`

```markdown
# Continual Learning Engine Architecture & Event Loop

`xinfer-forge` operates as a decoupled, background continual learning daemon (`forge-cli auto-cycle`). It monitors curated data streams emitted by edge appliances, fine-tunes deep neural representations in-place, and enforces safety boundaries before deploying candidate weights.

---

## 1. The Autonomous Adaptation Loop

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 1: DATASET DISCOVERY & VALIDATION                     │
 │  - Watches: /var/lib/sentinel-nexus/forge_datasets/         │
 │  - Validates CSV integrity and metadata schema against SHA256│
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 2: SELF-SUPERVISED TRAINING RUN (MAE + InfoNCE)       │
 │  - Ingests 32-dim continuous flow vectors                   │
 │  - Applies 30% stochastic feature masking                   │
 │  - Optimizes reconstruction loss and temporal contrastive   │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Produces Candidate Weights: θ*
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 3: IMMUTABLE GOLDEN ATTACKS REGRESSION GATE           │
 │  - Evaluates θ* against configs/safety/golden_attacks.yaml  │
 │  - Enforces zero-tolerance invariant: S(θ*) == 1.000        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼ S(θ*) < 1.000 (Regression Detected)           ▼ S(θ*) == 1.000 (100% Detection)
 ┌─────────────────────────────┐         ┌─────────────────────────────┐
 │ PURGE CIRCUIT TRIGGERED     │         │ STAGE 4: ONNX COMPILATION   │
 │ • Delete candidate θ*       │         │ • PyTorch -> ONNX Opset 17  │
 │ • Raise critical alert      │         │ • Set dynamic batch axes    │
 └─────────────────────────────┘         └──────────────┬──────────────┘
                                                        │
                                                        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 5: NEXUS REST STAGING & FLEET CANARY PROMOTION        │
 │  - Dispatches POST /api/v1/ota/stage to sentinel-nexus      │
 │  - Deploys: Shadow Mode -> 5% Canary -> Fleet-Wide (<50ms)  │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Resource Isolation & Execution Boundaries

Training neural models on multi-purpose edge appliances can compete with real-time packet filtering if not constrained:

1. **Linux cgroup v2 Constraints:** `forge-cli` execution runs inside a dedicated slice (`sentinel-forge.slice`) capped at $50\%$ CPU quota and pinned to lower NUMA nodes.
2. **Scheduling Priority:** Runs under `SCHED_IDLE` or `nice +19`, ensuring in-kernel eBPF packet mitigation ($< 0.84\,\mu\text{s}$) and live inference routines take precedence over retraining loops.
3. **Dedicated Scratchpad RAM:** Training allocations are constrained to a fixed memory budget ($< 4.0\text{ GB}$), avoiding host swapping.
```

