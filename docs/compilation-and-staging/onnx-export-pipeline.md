# ONNX Export Pipeline

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


Compiling PyTorch .pt weights via torch.onnx.export (Opset 17).

## Export

Constant folding plus shape inference; dynamic batch axes enabled.

## Verify

Reference runtime scores the export before it leaves the host.

```bash
$ forge-cli export-onnx --input-weights candidate.pt \
    --output-onnx models/network_threat_v2.onnx --opset 17 --input-dim 32
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
