# NIST SP 800-218 Secure Software Development Framework (SSDF)

The **NIST Special Publication 800-218** establishes the Secure Software Development Framework (SSDF) Version 1.1 for mitigating vulnerabilities across the software supply chain. In AI and machine learning architectures, SSDF applies directly to **Task PW.8: Protect Software from Unauthorized Access and Tampering**.

`xinfer-forge` satisfies the AI integrity controls mandated under NIST SP 800-218.

---

## 1. Traceability to NIST SSDF Practice PW.8

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ NIST SP 800-218 Practice PW.8 (Protect Software & AI Models)│
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
 │ Task PW.8.1   │       │ Task PW.8.2   │       │ Task PW.8.3   │
 │ Model Source  │       │ Cryptographic │       │ Secure Weight │
 │ Integrity     │       │ Manifests     │       │ Deployment    │
 └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
         │                       │                       │
         ▼                       ▼                       ▼
 Safety gate verifies    SHA-256 checksum        Staged rollout  │
 weights against known   manifest generated      (Canary 5%) with│
 golden attack corpus.   for all ONNX models.    RollbackGuard.  │
```

---

## 2. NIST SSDF Implementation Proofs

### Task PW.8.1: Prevent Vulnerabilities in AI Model Checkpoints
* **Enforcement:** `xinfer-forge` validates candidate checkpoints against the golden attacks corpus before export, preventing degraded models from entering the deployment pipeline.

### Task PW.8.2: Verify the Integrity of Software Releases
* **Enforcement:** Every compiled `.onnx` model is packaged with an accompanying `.manifest.json` file containing its streaming SHA-256 digest. Edge appliances verify this checksum before loading models into memory.

### Task PW.8.3: Secure Software Delivery Pipelines
* **Enforcement:** Distribution between `xinfer-forge` and `sentinel-nexus` is conducted over authenticated mTLS channels using scoped JWT credentials.

