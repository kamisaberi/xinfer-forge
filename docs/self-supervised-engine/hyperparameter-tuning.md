---

### File: `xinfer-forge/docs/self-supervised-engine/hyperparameter-tuning.md`

```markdown
# Hyperparameter Tuning & Training Baselines

Continual learning at the edge requires bounded training budgets to avoid CPU starvation. `xinfer-forge` defaults to validated hyperparameters optimized for stability across continuous training runs.

---

## 1. Production Hyperparameter Baselines

| Hyperparameter | Flag in `forge-cli` | Default Value | Tuning Range | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Learning Rate** | `--learning-rate` | `0.001` | `0.0001` to `0.005` | AdamW optimizer initial step size. |
| **Weight Decay** | `--weight-decay` | `1e-4` | `1e-5` to `1e-3` | $L_2$ regularization preventing weight explosion. |
| **Batch Size** | `--batch-size` | `64` | `32` to `256` | Number of flows per gradient update. |
| **Epochs** | `--epochs` | `5` | `3` to `10` | Continual adaptation epochs per batch. |
| **Masking Ratio** | `--masking-ratio` | `0.30` | `0.20` to `0.40` | Bernoulli masking fraction ($p_{\text{mask}}$). |
| **Contrastive Weight**| `--lambda` | `0.15` | `0.05` to `0.30` | Weight of $\mathcal{L}_{\text{InfoNCE}}$ in total loss. |
| **InfoNCE Temperature**| `--temperature` | `0.07` | `0.05` to `0.15` | Logit scale factor for contrastive pairs. |

---

## 2. Learning Rate Scheduling: Cosine Annealing

To prevent abrupt weight updates from disrupting previous knowledge (catastrophic forgetting), `forge-cli` uses **Cosine Annealing with Warmup**:

```python
from torch.optim.lr_scheduler import CosineAnnealingLR

optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
```
```

