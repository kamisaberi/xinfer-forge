# Resolving Loss Divergence, Exploding Gradients & NaNs

During continual retraining on uncurated ambient network telemetry, anomalous outliers (e.g., massive byte bursts or unnormalized port values) can cause numerical instability, leading to gradient explosion and `NaN` (Not-a-Number) loss values.

---

## 1. Primary Causes of Training Divergence

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Common Causes of NaN Loss in Tabular MAE                    │
 ├─────────────────────────────────────────────────────────────┤
 │ 1. Unnormalized Feature Columns (Raw bytes > 10^8)          │
 │ 2. Learning Rate Too High (> 0.01 without Warmup)           │
 │ 3. Division by Zero in InfoNCE Temperature Scaling (τ → 0)  │
 │ 4. Exploding Gradients across Linear Bottleneck Projections │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. In-Engine Safeguards & Remediation

### 1. Enforcing Gradient Value & Norm Clipping
`xinfer-forge` includes automated gradient clipping. If running custom scripts, ensure `clip_grad_norm_` is enforced prior to the optimizer step:

```python
# Scale gradients to prevent explosive weight updates
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

### 2. Validating Input Tensors for NaNs or Infs
Before beginning an epoch, inspect the input batch for corrupted floating-point values:

```python
if torch.isnan(batch_x).any() or torch.isinf(batch_x).any():
    raise ValueError("Input batch contains NaN or Infinite values! Check feature normalizer.")
```

### 3. Lowering the Learning Rate
If loss diverges during the first epoch, reduce the initial step size:

```bash
forge-cli train --data /tmp/ambient_flows.csv --learning-rate 0.0001 --epochs 5
```

