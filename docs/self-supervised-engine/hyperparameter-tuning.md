# Hyperparameter Tuning

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Learning rates, batch sizing, masking ratios, and temperature (τ).

## Defaults

LR 0.001, batch 64, mask 30%, τ 0.07 — tuned for 2,500-vector batches.

## Search

One knob at a time against gate pass-rate, never raw loss.

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
