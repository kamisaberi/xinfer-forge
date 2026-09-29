---

### File: `xinfer-forge/docs/nexus-integration/active-learning-uncertainty-gate.md`

```markdown
# Active Learning: The Uncertainty Entropy Gate ($0.40 - 0.60$)

In high-throughput cybersecurity environments ($> 1{,}250{,}000\text{ EPS}$), training on every observed network packet is computationally infeasible and counterproductive. Over $99.9\%$ of network flows represent known benign background noise.

`xinfer-forge` operates exclusively on data curated within the **Prediction Uncertainty Window**.

---

## 1. Uncertainty Gating Mechanics

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Edge Appliance AI Prediction Distribution f(x)             │
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 0.00 <= f(x) < 0.40     0.40 <= f(x) <= 0.60    0.60 < f(x) <= 1.00
 ┌───────────────┐       ┌───────────────────┐   ┌───────────────────┐
 │ CONFIDENT     │       │ HIGH UNCERTAINTY  │   │ CONFIDENT         │
 │ BENIGN        │       │ "EDGE CASES"      │   │ THREAT            │
 ├───────────────┤       ├───────────────────┤   ├───────────────────┤
 │ Discard from  │       │ Curated into CSV  │   │ In-Kernel Drop    │
 │ Retraining    │       │ for Forge Loop    │   │ Discard from Train│
 └───────────────┘       └─────────┬─────────┘   └───────────────────┘
                                   │
                                   ▼ Emitted to Forge
           [ Training focused on high-entropy boundary data ]
```

---

## 2. Mathematical Definition of Boundary Entropy

Prediction uncertainty is evaluated using binary Shannon entropy over the model's anomaly probability:

$$\mathcal{H}(p) = -p \log_2(p) - (1 - p) \log_2(1 - p)$$

$$\mathcal{H}(p) \ge \mathcal{H}(0.40) \approx 0.971\,\text{bits}$$

When $p \approx 0.50$, entropy is maximized ($1.00\,\text{bit}$). These flows represent edge cases—such as subtle protocol variations or unmodeled industrial shifts—providing the highest information gain during continual fine-tuning.
```

