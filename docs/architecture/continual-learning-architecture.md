# Continual Learning Architecture

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Decoupled continuous training pipeline and event loop.

## Decoupling

Training never blocks inference; the hot path never waits on a gradient.

## Events

Dataset arrivals drive cycles; idle hosts cost nothing.

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
