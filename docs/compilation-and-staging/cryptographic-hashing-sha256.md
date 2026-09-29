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

