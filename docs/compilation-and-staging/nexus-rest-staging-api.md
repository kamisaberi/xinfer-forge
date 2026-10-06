# Nexus Fleet REST Staging API (`POST /api/v1/ota/stage`)

Once compiled and verified, candidate model artifacts are staged to the central fleet hub (`sentinel-nexus`) via its authenticated REST management API on port **9443**.

---

## 1. REST Staging Sequence

```text
 xinfer-forge CLI / Background Stager
                   │
                   ▼ HTTP POST /api/v1/ota/stage (Multipart Form-Data)
 ┌─────────────────────────────────────────────────────────────┐
 │ Sentinel-Nexus Hub (Tier 6 Command Plane - Port 9443)       │
 ├─────────────────────────────────────────────────────────────┤
 │ Headers:                                                    │
 │   Authorization: Bearer <ADMIN_ORCHESTRATOR_JWT>            │
 │   X-Model-Version: 2.4.0                                    │
 │   X-Model-SHA256 : e9a2c31e847b2c94b13a7b41e2...            │
 │ Body:                                                       │
 │   part1: network_threat_v2.onnx (Binary Stream)             │
 │   part2: network_threat_v2.manifest.json                    │
 └─────────────────────────────┬───────────────────────────────┘
                               │
                               ▼ Validation & Staging
 ┌─────────────────────────────────────────────────────────────┐
 │ 1. Recalculates SHA-256; verifies manifest signature        │
 │ 2. Stores model into fleet repository:                      │
 │    /var/lib/sentinel-nexus/models/network_threat_v2.onnx    │
 │ 3. Initializes Canary Rollout Pipeline                      │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Python Staging Client (`forge/nexus_bridge.py`)

```python
import requests
from pathlib import Path

def stage_model_to_nexus(
    nexus_url: str, 
    token: str, 
    onnx_path: str, 
    manifest_path: str
) -> bool:
    endpoint = f"{nexus_url.rstrip('/')}/api/v1/ota/stage"
    headers = {"Authorization": f"Bearer {token}"}

    with open(onnx_path, "rb") as f_model, open(manifest_path, "rb") as f_manifest:
        files = {
            "model_binary": (Path(onnx_path).name, f_model, "application/octet-stream"),
            "manifest_json": (Path(manifest_path).name, f_manifest, "application/json")
        }
        response = requests.post(endpoint, headers=headers, files=files, timeout=30)

    if response.status_code == 201:
        print("[+] Model staged to Sentinel-Nexus fleet orchestrator successfully.")
        return True
    else:
        print(f"[-] Staging failed [{response.status_code}]: {response.text}")
        return False
```

