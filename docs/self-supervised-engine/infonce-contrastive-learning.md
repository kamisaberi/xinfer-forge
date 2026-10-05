---

### File: `xinfer-forge/docs/self-supervised-engine/infonce-contrastive-learning.md`

```markdown
# InfoNCE Contrastive Representation Learning

While the Masked Autoencoder forces the model to reconstruct intra-flow feature dependencies, it does not inherently account for temporal continuity across related network flows. 

`xinfer-forge` incorporates **InfoNCE Contrastive Learning** to cluster temporally adjacent flows in the latent space while repelling unrelated flows.

---

## 1. Temporal Positive Pair Construction

```text
 Network Wire Stream (Time Ordering)
 ───► Flow A (t = 0.00s) ──► Flow B (t = 0.15s) ──────────────► Flow K (t = 120.0s)
      └──────────────┬────────────────────────┘                  └─────────┬────────┘
                     ▼                                                     ▼
         POSITIVE PAIR (z_i, z_j⁺)                               NEGATIVE PAIR (z_i, z_k⁻)
      Same source subnet, adjacent window                        Unrelated background flow
```

Two flows $x_i$ and $x_j$ form a **positive pair** if:
1. They share identical source subnets or industrial Unit IDs.
2. Their inter-arrival delta satisfies $|t_i - t_j| < 2.0\,\text{seconds}$.

---

## 2. InfoNCE Loss Formulation

For a batch containing a positive pair $(z_i, z_j^+)$ and $K$ negative samples $\{z_k^-\}_{k=1}^K$, the InfoNCE contrastive loss is defined as:

$$\mathcal{L}_{\text{InfoNCE}} = -\log \frac{\exp\left(\frac{\operatorname{sim}(z_i, z_j^+)}{\tau}\right)}{\exp\left(\frac{\operatorname{sim}(z_i, z_j^+)}{\tau}\right) + \sum_{k=1}^{K} \exp\left(\frac{\operatorname{sim}(z_i, z_k^-)}{\tau}\right)}$$

Where:
* $\operatorname{sim}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$ represents cosine similarity.
* $\tau = 0.07$ is the temperature hyperparameter controlling distribution sharpness.

---

## 3. PyTorch Implementation (`losses/infonce.py`)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class InfoNCELoss(nn.Module):
    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature

    def forward(self, query: torch.Tensor, positive: torch.Tensor, negatives: torch.Tensor) -> torch.Tensor:
        # L2-normalize latent embeddings
        q_norm = F.normalize(query, dim=-1)
        pos_norm = F.normalize(positive, dim=-1)
        neg_norm = F.normalize(negatives, dim=-1)

        # Compute positive logits: [batch_size, 1]
        pos_sim = torch.sum(q_norm * pos_norm, dim=-1, keepdim=True) / self.temperature

        # Compute negative logits: [batch_size, K]
        neg_sim = torch.matmul(q_norm, neg_norm.transpose(0, 1)) / self.temperature

        logits = torch.cat([pos_sim, neg_sim], dim=1)
        labels = torch.zeros(query.size(0), dtype=torch.long, device=query.device)

        return F.cross_entropy(logits, labels)
```
```

