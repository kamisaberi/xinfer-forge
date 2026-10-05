---

### File: `xinfer-forge/docs/self-supervised-engine/stochastic-masking-strategy.md`

```markdown
# Stochastic Feature Masking Strategy for Tabular Flow Vectors

In computer vision MAE models (e.g., He et al.), masking is applied to spatial image patches. In tabular cyber-physical telemetry, individual features represent distinct physical and protocol dimensions (e.g., packet counts, TCP window sizes, Modbus register setpoints). 

`xinfer-forge` applies a **$30\%$ Stochastic Bernoulli Masking Strategy**.

---

## 1. Tabular Masking Formulation

Let $x = [x_1, x_2, \dots, x_{32}] \in \mathbb{R}^{32}$ represent a continuous flow vector. A binary mask vector $m \in \{0, 1\}^{32}$ is sampled independently for each training instance:

$$m_i \sim \operatorname{Bernoulli}(p_{\text{mask}}), \quad p_{\text{mask}} = 0.30$$

The corrupted input vector $\tilde{x}$ presented to the encoder is:

$$\tilde{x}_i = \begin{cases} 0.0, & \text{if } m_i = 1 \\ x_i, & \text{if } m_i = 0 \end{cases}$$

```text
 RAW FLOW VECTOR:
 [ Dur: 0.12 | Pkts: 1420 | Bytes: 96000 | TCP Win: 65535 | Reg: 40001 | ... ]
         │
         ▼ 30% Random Bernoulli Masking (m_i = 1)
 CORRUPTED INPUT (Presented to Encoder):
 [ Dur: 0.12 | [MASK: 0.0] | Bytes: 96000 | [MASK: 0.0] | Reg: 40001 | ... ]
         │
         ▼ Autoencoder Target
 Model must reconstruct the masked features [Pkts, TCP Win] using remaining physical context!
```

---

## 2. Why $30\%$ Masking Ratio?

| Masking Ratio ($p_{\text{mask}}$) | Convergence Behavior | Manifold Robustness |
| :--- | :--- | :--- |
| **$10\%$ (Under-Masking)** | Model memorizes identity mapping; fails to learn inter-feature correlations. | Low |
| **$30\%$ (Optimal Tabular)** | Forces network to infer missing protocol fields from correlated telemetry without causing information collapse. | **Optimal** |
| **$75\%$ (Vision-Style)** | Exceeds tabular redundancy; causes non-convergent gradient oscillations. | Divergent |

---

## 3. Vectorized Masking Generator (`masking.py`)

```python
import torch

def generate_tabular_mask(batch_size: int, feature_dim: int = 32, p_mask: float = 0.30, device: str = 'cpu') -> torch.Tensor:
    """Generates an independent Bernoulli mask matrix."""
    prob_matrix = torch.full((batch_size, feature_dim), p_mask, device=device)
    mask = torch.bernoulli(prob_matrix)
    return mask
```
```

