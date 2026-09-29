---

### File: `xinfer-forge/docs/compilation-and-staging/dynamic-batch-axes.md`

```markdown
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
```

---

### File: `xinfer-forge/docs/compilation-and-staging/cryptographic-hashing-sha256.md`

```markdown
# Cryptographic SHA-256 Hashing & Integrity Manifests

To prevent in-transit tampering, man-in-the-middle weight injection, and filesystem corruption, every compiled ONNX artifact is packaged with a signed cryptographic manifest.

---

## 1. Checksum Generation Pipeline

```text
 [ Compiled Model: network_threat_v2.onnx ]
                      │
                      ▼ 64 KB Block Streaming
 ┌─────────────────────────────────────────────────────────────┐
 │ Cryptographic Hash Engine: SHA-256                          │
 └────────────────────┬────────────────────────────────────────┘
                      │ Emits: 64-Character Hexadecimal Digest
                      ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Manifest File: network_threat_v2.manifest.json              │
 │  {                                                          │
 │    "model_name": "network_threat",                          │
 │    "version": "2.4.0",                                      │
 │    "sha256": "e9a2c31e847b2c94b13a7b41e2d90100...",        │
 │    "trained_at_epoch": 1791172800,                          │
 │    "safety_gate_score": 1.000                               │
 │  }                                                          │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Checksum Computation (`forge/export/manifest.py`)

```python
import hashlib
import json
from pathlib import Path
from typing import Dict, Any

def generate_manifest(onnx_path: str, model_version: str, gate_score: float) -> str:
    p = Path(onnx_path)
    sha256 = hashlib.sha256()

    with open(p, "rb") as f:
        while chunk := f.read(65536): # 64 KB streaming buffer
            sha256.update(chunk)
            
    digest = sha256.hexdigest()

    manifest_data: Dict[str, Any] = {
        "model_name": p.stem,
        "version": model_version,
        "format": "ONNX_OPSET_17",
        "file_size_bytes": p.stat().st_size,
        "sha256": digest,
        "safety_gate_score": gate_score,
        "target_silicon": "AUTO"
    }

    manifest_path = p.with_suffix(".manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)

    return str(manifest_path)
```
```

---

### File: `xinfer-forge/docs/compilation-and-staging/nexus-rest-staging-api.md`

```markdown
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
```

---

### File: `xinfer-forge/docs/compilation-and-staging/staged-rollout-lifecycle.md`

```markdown
# The Staged Rollout Lifecycle & RollbackGuard

Deploying newly trained weights directly to thousands of edge defense appliances presents operational risk. `sentinel-nexus` manages model deployment through a **three-stage rollout lifecycle** protected by automated rollback circuits.

---

## 1. Rollout Progression Stages

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 1: SHADOW EVALUATION MODE (100% Passive)              │
 │  - Deployed in parallel with production model on edge nodes │
 │  - AI evaluates real traffic; zero active kernel drop power │
 │  - Gate Requirement: Divergence delta <= 2.5% for 48 hours  │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Passes Shadow Verification
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 2: CANARY FLEET ENFORCEMENT (5% of Fleet)             │
 │  - Active mitigation enabled on 5% of non-critical gateways │
 │  - Protected by RollbackGuard telemetry monitor             │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Passes Canary Testing (0 Breaches)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ STAGE 3: FLEET-WIDE PROMOTION (100% of Fleet)               │
 │  - Promoted across all 5,000 edge nodes via Collective Bus  │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Automated Rollback Triggers (`RollbackGuard`)

During Canary deployment, `sentinel-nexus` tracks operational SLAs from the edge appliances. The candidate model is **abruptly rolled back** to the previous baseline if any of the following conditions occur:

| Health Metric | Rollback Trigger Threshold | Mitigation Reaction |
| :--- | :--- | :--- |
| **Mitigation Latency** | $> 1{,}000\,\mu\text{s}$ SLA breach | Instant downgrade to `network_threat_v1.onnx`. |
| **False Positive Surge** | Drop rate spikes $> 500\%$ over moving average | Reverts in-kernel eBPF drop rules immediately. |
| **Edge Hardware Failure** | NPU driver timeout / kernel panic trace | Restores CPU reference backend. |
```

