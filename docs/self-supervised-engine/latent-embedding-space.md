---

### File: `xinfer-forge/docs/self-supervised-engine/latent-embedding-space.md`

```markdown
# Latent Bottleneck Geometry ($z \in \mathbb{R}^8$) & Anomaly Separation

The core bottleneck of `TabularMAE` compresses the 32-dimensional input vector down to an **8-dimensional latent space** ($z \in \mathbb{R}^8$). This bottleneck forces the network to retain only the essential physical and protocol invariants of normal operations.

---

## 1. Latent Bottleneck Dimensionality ($32 \to 8$)

```text
 Ingress Features (ℝ³²) ──► [ Encoder ] ──► Bottleneck Space (ℝ⁸) ──► [ Decoder ] ──► Reconstruction (ℝ³²)
```

* **High-Dimensional Redundancy ($D=32$):** Raw flows contain collinear protocol artifacts (e.g., byte count correlated with packet count; header size correlated with protocol).
* **Manifold Regularization ($d=8$):** An 8-dimensional space provides sufficient capacity to encode operational states (e.g., normal industrial cycles, idle states, scheduled polling) while preventing the network from memorizing anomalous noise.

---

## 2. Outlier Separation Mechanics

When anomalous traffic (e.g., a port scan, Stuxnet register injection, or C2 beacon) is passed through the encoder:

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Latent Space Geometry (t-SNE Projection):                   │
 │                                                             │
 │            Normal Baseline Manifold                         │
 │              (Tightly Clustered)                            │
 │                 ┌─────────┐                                 │
 │                 │  * * *  │                                 │
 │                 │ * * * * │                                 │
 │                 └─────────┘                                 │
 │                                                             │
 │                                           ★ Attacker Anomaly│
 │                                         (Pushed far outside │
 │                                          the dense manifold)│
 └─────────────────────────────────────────────────────────────┘
```

Because the decoder was trained exclusively to reconstruct vectors lying on the dense baseline manifold, passing an outlier $z_{\text{anomaly}}$ results in severe reconstruction error across physical dimensions, triggering an in-kernel drop ($< 0.84\,\mu\text{s}$) on the edge appliance.
```

