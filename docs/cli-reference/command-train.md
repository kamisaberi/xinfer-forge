# Command: train

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


forge-cli train: manual dataset training execution.

## Use

Point at a CSV batch and go; hyperparameters from config or flags.

## Output

Checkpoints plus a loss-curve report per run.

```bash
$ forge-cli train --dataset batch.csv --epochs 50 --lr 0.001
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
