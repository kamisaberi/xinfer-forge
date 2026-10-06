# Dynamic Batch Axes: Single-Frame to Saturation Ingestion

Edge intrusion prevention requires models to handle two distinct operational extremes:
1. **Single-Packet Fast Path ($N=1$):** Inline packet-by-packet evaluation inside the NIC driver ring ($< 0.84\,\mu\text{s}$ SLA).
2. **Forensic Batch Evaluation ($N=64, 128, 1024$):** Offline PCAP re-evaluation and historical batch auditing.

`xinfer-forge` compiles ONNX models with **Dynamic Batch Axes** to support variable tensor shapes without recompilation.

---

## 1. Dynamic Shape Declaration

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Tensor Dimensionality Specification                         │
 ├─────────────────────────────────────────────────────────────┤
 │ Input Tensor : "flow_features"  ──► [ batch_size, 32 ]      │
 │ Output Tensor: "reconstruction" ──► [ batch_size, 32 ]      │
 │ Latent Tensor: "latent_z"       ──► [ batch_size, 8 ]       │
 └─────────────────────────────────────────────────────────────┘
```

In the ONNX protobuf definition, dimension index `0` is assigned a symbolic identifier string (`"batch_size"`), while dimension index `1` is locked to a fixed constant scalar (`32`).

---

## 2. Verification Across Varying Batch Sizes

```python
import onnxruntime as ort
import numpy as np

def verify_dynamic_shapes(onnx_path: str):
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    
    # Test batch sizes: 1 (Wire fast-path), 16 (Industrial burst), 512 (Forensic batch)
    for batch_size in [1, 16, 512]:
        test_tensor = np.random.uniform(0.0, 1.0, size=(batch_size, 32)).astype(np.float32)
        outputs = session.run(None, {"flow_features": test_tensor})
        
        assert outputs[0].shape == (batch_size, 32), f"Shape mismatch for batch size {batch_size}"
        print(f"[PASS] Dynamic Batch Size Verified: Shape [{batch_size}, 32]")

verify_dynamic_shapes("/tmp/network_threat_v2.onnx")
```

