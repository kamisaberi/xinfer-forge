# Loss Divergence & NaNs

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Resolving exploding gradients and numerical instability in MAE.

## First aid

Halve the learning rate, clip gradients, re-run the smoke batch.

## Root cause

Unnormalized features are the usual suspect — check scalers.

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
