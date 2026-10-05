# Quickstart: First Adaptation

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Five-minute training run on a mock 32-dim NetFlow batch.

## Batch

Bundled mock vectors need no capture hardware or network.

## Expect

Loss curves fall, the gate passes, and a test ONNX lands in models/.

```bash
$ forge-cli train --dataset tests/mock_batch.csv --epochs 5
[*] loss 0.0412 (MAE) | 0.0189 (InfoNCE)
[+] gate: 100% — ONNX written
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
