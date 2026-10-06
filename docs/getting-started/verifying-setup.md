# Verifying Your Environment & Diagnostic Self-Test

Confirm that the PyTorch execution backend, ONNX compiler, and mathematical dependencies are configured properly.

---

## 1. Running the Automated Diagnostic Harness

Execute the built-in diagnostic routine:

```bash
forge-cli diag
```

### Sample Output

```text
================================================================================
                     XINFER-FORGE DIAGNOSTIC SUITE
================================================================================
Forge Version          : 2.4.0 (Aryorithm Technologies B.V.)
Python Interpreter     : 3.12.3 (/opt/sentinel-stack/venv/bin/python3)
PyTorch Version        : 2.2.2+cu121
Compute Device Ready   : CUDA GPU (NVIDIA RTX A4000) [Fallback: CPU AVX2 Available]
CUDA Memory Total      : 16.0 GB (Device 0)
ONNX Exporter Version  : 1.16.0 (Opset 17 Supported)
ONNX Runtime Engine    : 1.17.3
Virtualenv Isolation   : PEP 668 Compliant (/opt/sentinel-stack/venv)
Golden Attacks Corpus  : configs/safety/golden_attacks.yaml (52 Vectors Found)
Nexus Staging Bridge   : Functional (curl / requests HTTP client active)

================================================================================
Status: ALL CHECKS PASSED. Ready for autonomous active learning.
================================================================================
```

---

## 2. Testing PyTorch to ONNX Opset 17 Compilation

Verify that the local Python environment can export Torch models to ONNX Opset 17 without warnings:

```bash
python3 -c "
import torch
import torchvision
model = torch.nn.Sequential(torch.nn.Linear(32, 16), torch.nn.Linear(16, 32))
dummy_input = torch.randn(1, 32)
torch.onnx.export(
    model, dummy_input, '/tmp/test_export.onnx',
    opset_version=17,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch'}, 'output': {0: 'batch'}}
)
import onnx
onnx_model = onnx.load('/tmp/test_export.onnx')
onnx.checker.check_model(onnx_model)
print('[+] ONNX Opset 17 Export & Checker Succeeded!')
"
```

