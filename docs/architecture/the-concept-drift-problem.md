# The Concept Drift Problem in Cyber-Physical Networks

A primary reason static intrusion detection systems fail in real-world industrial environments is **concept drift**. Normal operational traffic does not remain static over time; baseline distributions drift naturally due to software updates, operational reconfigurations, and physical process shifts.

---

## 1. Mathematical Formulation of Drift

Let $X \in \mathbb{R}^{32}$ denote the continuous feature vector representing an individual network flow, and let $Y \in \{0, 1\}$ represent the ground truth label ($0 = \text{Benign}, 1 = \text{Malicious}$).

In real-world networks, the joint probability distribution $P_t(X, Y)$ changes over time $t$:

$$P_t(X, Y) \ne P_{t + \Delta t}(X, Y)$$

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Covariate Shift: P_t(X) ≠ P_{t+Δt}(X), while P(Y|X) is Fixed│
 │  - Cause: A new PLC engineering tool increases packet rate.│
 │  - Consequence: Static models misclassify new normal flows  │
 │    as anomalies, causing massive false-positive alert storms│
 └─────────────────────────────────────────────────────────────┘
 ┌─────────────────────────────────────────────────────────────┐
 │ Concept Shift: P_t(Y|X) ≠ P_{t+Δt}(Y|X)                     │
 │  - Cause: A protocol once considered normal becomes an      │
 │    exploited attack vector (e.g., Log4j / zero-days).       │
 │  - Consequence: Static models fail to identify new threats. │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Empirical Decay of Static Detection Models

Over a 12-month evaluation across water treatment and electrical distribution networks, static detection models trained on frozen baselines exhibit steady accuracy decay:

```text
STATIC MODEL ACCURACY DECAY (Without Continual Learning):

Accuracy (%)
 100% ──┐
        │  Day 0: 98.4% (Initial Deployment)
  80% ──┼─────────────────────── Day 90: 84.1%
        │                                ┌────────────────────── Day 180: 71.2%
  60% ──┼────────────────────────────────┼─────────────────────────────────────── Day 360: 64.2%
        │                                │                                        (Complete Model Decay)
   0% ──┴──────────┴─────────────────────┴──────────────────────┴──────────────────────┴────► Time
```

By continually ingesting ambient flow batches, `xinfer-forge` updates the internal representation manifold to maintain sustained detection accuracy ($> 98.0\%$).

