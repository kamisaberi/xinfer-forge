# Command: export-onnx

> **Status:** Draft — placeholder content. Final technical prose is forthcoming.


forge-cli export-onnx: standalone ONNX compilation.

## Use

Compile approved weights without running a full cycle.

## Output

Opset 17 graph with dynamic batch axes.

```bash
$ forge-cli export-onnx --input-weights candidate.pt \
    --output-onnx models/v2.onnx --opset 17
```

---

*Part of the xinfer-forge documentation set. See mkdocs.yml for navigation.*
