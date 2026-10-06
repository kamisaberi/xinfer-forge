# Command: `forge-cli stage`

Submits an exported ONNX model and its cryptographic manifest to `sentinel-nexus` via its authenticated REST API (`POST /api/v1/ota/stage`), initiating a canary fleet rollout.

---

## 1. Syntax

```bash
forge-cli stage [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--onnx-model PATH` | File Path | **Required** | Compiled ONNX model binary. |
| `--manifest PATH` | File Path | **Required** | Accompanying `.manifest.json` file. |
| `--nexus-url URL` | URL | `https://127.0.0.1:9443`| Sentinel-Nexus management REST API URL. |
| `--token STRING` | String | `ENV[NEXUS_TOKEN]` | Administrator Bearer JWT authentication token. |

---

## 3. Execution Example

```bash
forge-cli stage \
    --onnx-model /opt/sentinel/models/network_threat_v2.onnx \
    --manifest /opt/sentinel/models/network_threat_v2.manifest.json \
    --nexus-url https://10.240.0.10:9443 \
    --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Expected Output
```text
[*] Dispatching multipart upload to https://10.240.0.10:9443/api/v1/ota/stage...
[+] HTTP 201 Created: Model staged successfully!
[+] Fleet Staging Initialized:
    Model Version : 2.4.0
    Deployment ID : stage-8f1c2a04
    Current State : STAGE_SHADOW_MODE (48-Hour Baseline Evaluation)
```

