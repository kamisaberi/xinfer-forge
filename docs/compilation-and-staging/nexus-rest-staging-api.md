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

