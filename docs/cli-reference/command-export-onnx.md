# Command: `forge-cli export-onnx`

Compiles a validated PyTorch checkpoint into an ONNX Opset 17 binary with dynamic batch axes, generating an accompanying cryptographic SHA-256 manifest.

---

## 1. Syntax

```bash
forge-cli export-onnx [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--checkpoint PATH` | File Path | **Required** | Validated PyTorch checkpoint (`.pt`). |
| `--output-onnx PATH` | File Path | `network_threat_v2.onnx` | Destination file for compiled ONNX graph. |
| `--opset-version INT` | Integer | `17` | ONNX Opset specification version. |
| `--model-version STR` | String | `2.0.0` | Semantic version string written to manifest. |

---

## 3. Execution Example

```bash
forge-cli export-onnx \
    --checkpoint /tmp/candidate_weights.pt \
    --output-onnx /opt/sentinel/models/network_threat_v2.onnx \
    --model-version 2.4.0
```

### Expected Output
```text
[*] Exporting PyTorch graph to ONNX Opset 17...
[*] Dynamic batch dimension bound: input [batch_size, 32] -> output [batch_size, 32]
[*] Running onnx.checker.check_model: PASSED
[*] Auditing numerical parity against ONNX Runtime: atol=1e-5 PASSED
[*] Calculating SHA-256: e9a2c31e847b2c94b13a7b41e2d9010000000000000000000000000000000000
[+] Artifacts generated:
    Model    : /opt/sentinel/models/network_threat_v2.onnx (7,412 bytes)
    Manifest : /opt/sentinel/models/network_threat_v2.manifest.json
```

