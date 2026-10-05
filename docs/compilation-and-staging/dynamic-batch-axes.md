# Dynamic Batch Axes

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Supporting variable inference batch sizes: [batch_size, 32].

## Why

Edge batching varies with ring pressure; fixed batches would pad and lie.

## How

Dynamic axes declared at export; validated across 1–256.

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
