### Part 5: Model Compilation & Fleet Staging (`compilation-and-staging/*`)

This section contains 5 technical implementation guides detailing the model compilation and fleet distribution pipeline of `xinfer-forge`: compiling PyTorch weights to ONNX Opset 17, configuring dynamic batch axes, generating SHA-256 cryptographic manifests, dispatching models via the Nexus REST API, and managing the multi-stage canary rollout lifecycle.

---

### File: `xinfer-forge/docs/compilation-and-staging/onnx-export-pipeline.md`

```markdown
# ONNX Opset 17 Export Pipeline (`forge/export/onnx_exporter.py`)

Once candidate model weights pass the zero-tolerance Golden Attacks Safety Gate, `xinfer-forge` compiles the native PyTorch checkpoint (`.pt`) into a production-grade **ONNX (Open Neural Network Exchange)** artifact targeting **Opset 17**.

---

## 1. Why ONNX Opset 17?

1. **Native `LayerNorm` Operator Support:** Prior ONNX opsets decomposed Layer Normalization into multiple discrete mathematical operations (`ReduceMean`, `Sub`, `Pow`, `Sqrt`, `Div`), introducing compiler overhead on edge NPUs. Opset 17 provides native, fused `LayerNormalization`.
2. **Direct Silicon Runtime Mapping:** Opset 17 is directly consumable by all 15 hardware target backends in `libxinfer.so` (Intel OpenVINO, NVIDIA TensorRT, Rockchip RKNN, Qualcomm QNN, and HailoRT).
3. **Deterministic Type Inference:** Guarantees strict IEEE 754 floating-point precision mappings without dynamic type coercion ambiguities.

---

## 2. Export Pipeline Sequence

```text
 Validated PyTorch Candidate Weights (θ*)
                     │
                     ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ torch.onnx.export() Execution                               │
 │  - Opset: 17                        - Constant Folding: ON  │
 │  - Input Name: "flow_features"      - Shape: [batch, 32]    │
 │  - Output Name: "reconstruction"    - Shape: [batch, 32]    │
 └───────────────────┬─────────────────────────────────────────┘
                     │ Emits: network_threat_v2.onnx
                     ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ ONNX Graph Structural Verification                          │
 │  - onnx.checker.check_model()                               │
 │  - Verifies DAG acyclicity and operator type consistency     │
 └───────────────────┬─────────────────────────────────────────┘
                     │
                     ▼ Numerical Parity Verification
 ┌─────────────────────────────────────────────────────────────┐
 │ PyTorch vs. ONNX Runtime Output Comparison                  │
 │  - Max Absolute Tolerance (atol): 1e-5                      │
 │  - Verifies exact numerical parity before fleet staging     │
 └─────────────────────────────────────────────────────────────┘
```

---

## 3. Python Implementation (`forge/export/onnx_exporter.py`)

```python
import torch
import onnx
import onnxruntime as ort
import numpy as np
from pathlib import Path
from forge.models.mae import TabularMAE

def export_to_onnx(
    model: TabularMAE, 
    output_path: str, 
    opset_version: int = 17
) -> str:
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    model.eval()
    dummy_input = torch.randn(1, 32, dtype=torch.float32)

    # 1. Export PyTorch graph to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        str(out_file),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["flow_features"],
        output_names=["reconstruction"],
        dynamic_axes={
            "flow_features": {0: "batch_size"},
            "reconstruction": {0: "batch_size"}
        }
    )

    # 2. Structural Schema Check
    onnx_model = onnx.load(str(out_file))
    onnx.checker.check_model(onnx_model)

    # 3. Numerical Parity Audit
    with torch.no_grad():
        torch_out, _ = model(dummy_input)

    ort_session = ort.InferenceSession(str(out_file), providers=["CPUExecutionProvider"])
    ort_inputs = {"flow_features": dummy_input.numpy()}
    ort_out = ort_session.run(None, ort_inputs)[0]

    np.testing.assert_allclose(
        torch_out.numpy(), 
        ort_out, 
        rtol=1e-4, 
        atol=1e-5, 
        err_msg="ONNX numerical parity audit failed!"
    )

    print(f"[+] ONNX export verified and written to: {out_file}")
    return str(out_file)
```
```

