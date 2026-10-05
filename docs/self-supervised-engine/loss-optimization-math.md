---

### File: `xinfer-forge/docs/self-supervised-engine/loss-optimization-math.md`

```markdown
# Composite Loss Optimization Formulation

During continual training cycles, `xinfer-forge` optimizes a composite loss objective combining the **Masked Reconstruction Error ($\mathcal{L}_{\text{MAE}}$)** and the **Temporal Contrastive Penalty ($\mathcal{L}_{\text{InfoNCE}}$)**.

---

## 1. Total Loss Formulation

$$\mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_{\text{MAE}}(x, \hat{x}; \theta) + \lambda \cdot \mathcal{L}_{\text{InfoNCE}}(z; \theta)$$

Where:
* $\theta$ denotes the trainable parameter set of `TabularMAE`.
* $\lambda = 0.15$ is the contrastive regularization weight.

---

## 2. Masked Reconstruction Loss ($\mathcal{L}_{\text{MAE}}$)

Reconstruction loss is evaluated using Mean Squared Error (MSE), with double weighting applied to masked dimensions to force predictive inference:

$$\mathcal{L}_{\text{MAE}} = \frac{1}{D} \sum_{i=1}^{D} \left[ w_i \cdot \left(x_i - \hat{x}_i\right)^2 \right]$$

$$w_i = \begin{cases} 2.0, & \text{if } m_i = 1 \text{ (Masked Dimension)} \\ 1.0, & \text{if } m_i = 0 \text{ (Unmasked Context)} \end{cases}$$

---

## 3. PyTorch Composite Loss Function (`trainer.py`)

```python
import torch
import torch.nn as nn
from forge.losses.infonce import InfoNCELoss

class CompositeForgeLoss(nn.Module):
    def __init__(self, lambda_contrastive: float = 0.15, temperature: float = 0.07):
        super().__init__()
        self.lambda_contrastive = lambda_contrastive
        self.infonce = InfoNCELoss(temperature=temperature)

    def forward(self, x: torch.Tensor, x_hat: torch.Tensor, mask: torch.Tensor, 
                z_query: torch.Tensor, z_pos: torch.Tensor, z_negs: torch.Tensor) -> torch.Tensor:
        
        # 1. Mask-Weighted Mean Squared Error
        weights = 1.0 + (mask * 1.0) # 2.0 on masked features, 1.0 on unmasked
        mse_loss = torch.mean(weights * ((x - x_hat) ** 2))

        # 2. InfoNCE Contrastive Loss
        contrastive_loss = self.infonce(z_query, z_pos, z_negs)

        # 3. Composite Objective
        total_loss = mse_loss + (self.lambda_contrastive * contrastive_loss)
        return total_loss
```
```

