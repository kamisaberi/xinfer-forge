# Neural Layer Specifications

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Linear projections, LayerNorm, and LeakyReLU activations.

## Blocks

Projection → norm → LeakyReLU, repeated; no exotic operators.

## Rationale

Boring layers export cleanly to every ONNX backend.

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
