---

### File: `xinfer-forge/docs/cli-reference/command-train.md`

```markdown
# Command: `forge-cli train`

Executes self-supervised training on a 32-dimensional continuous flow dataset using Masked Autoencoder (MAE) reconstruction and InfoNCE temporal contrastive objectives.

---

## 1. Syntax

```bash
forge-cli train [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--data PATH` | File Path | **Required** | Path to the continuous 32-dim CSV dataset. |
| `--output-checkpoint PATH` | File Path | `candidate.pt` | Output destination for trained PyTorch weights. |
| `--epochs INT` | Integer | `5` | Total training epochs over the dataset. |
| `--batch-size INT` | Integer | `64` | Mini-batch sample size per gradient update. |
| `--learning-rate FLOAT` | Float | `0.001` | AdamW initial learning rate. |
| `--weight-decay FLOAT` | Float | `1e-4` | $L_2$ weight decay regularization. |
| `--masking-ratio FLOAT` | Float | `0.30` | Bernoulli feature masking probability ($p_{\text{mask}}$). |
| `--lambda-contrastive FLOAT`| Float | `0.15` | Weight multiplier ($\lambda$) for InfoNCE loss. |
| `--temperature FLOAT` | Float | `0.07` | InfoNCE logit temperature parameter ($\tau$). |

---

## 3. Execution Example

```bash
forge-cli train \
    --data /var/lib/sentinel-nexus/forge_datasets/forge_dataset_8f1c2a04.csv \
    --output-checkpoint /tmp/candidate_weights.pt \
    --epochs 5 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --masking-ratio 0.30 \
    --lambda-contrastive 0.15
```

### Expected Output
```text
[*] Initializing TabularMAE: 32 -> 16 -> 8 -> 16 -> 32
[*] Target Compute Device: cuda:0 (NVIDIA RTX A4000)
[*] Ingesting Dataset: 5,000 samples (32 continuous dimensions)
Epoch 1/5 [========================================] Loss: 0.0381 (MAE: 0.0345, InfoNCE: 0.0036)
Epoch 2/5 [========================================] Loss: 0.0242 (MAE: 0.0218, InfoNCE: 0.0024)
Epoch 3/5 [========================================] Loss: 0.0165 (MAE: 0.0149, InfoNCE: 0.0016)
Epoch 4/5 [========================================] Loss: 0.0121 (MAE: 0.0109, InfoNCE: 0.0012)
Epoch 5/5 [========================================] Loss: 0.0098 (MAE: 0.0089, InfoNCE: 0.0009)
[+] Model training complete. Candidate checkpoint saved: /tmp/candidate_weights.pt
```
```

