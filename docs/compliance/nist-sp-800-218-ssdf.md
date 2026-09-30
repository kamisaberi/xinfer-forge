---

### File: `xinfer-forge/docs/compliance/nist-sp-800-218-ssdf.md`

```markdown
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
```

---

### File: `xinfer-forge/docs/compliance/auditing-training-runs.md`

```markdown
# Immutable Logging of Training Runs & Weight Lineage

Regulatory compliance frameworks require detailed audit trails demonstrating when models were trained, what dataset was ingested, which hyperparameters were used, and whether safety verification passed.

`xinfer-forge` maintains an **immutable, machine-readable training audit log**.

---

## 1. Audit Log Record Format (`training_audit.jsonl`)

Every completed adaptation cycle appends a record to `/var/log/sentinel/training_audit.jsonl`:

```json
{
  "audit_version": "1.0",
  "adaptation_id": "adapt-8f1c2a04-d912",
  "timestamp_iso": "2026-10-05T04:12:00.184920Z",
  "host_hardware": {
    "node_id": "edge-substation-alpha",
    "compute_device": "cuda:0",
    "tpm_tier": "TIER1_PHYSICAL_TPM"
  },
  "dataset_metadata": {
    "source_file": "forge_dataset_8f1c2a04.csv",
    "sample_count": 5000,
    "input_dimension": 32,
    "sha256": "e9a2c31e847b2c94b13a7b41e2d9010000000000000000000000000000000000"
  },
  "training_hyperparameters": {
    "epochs": 5,
    "batch_size": 64,
    "learning_rate": 0.001,
    "masking_ratio": 0.30,
    "lambda_contrastive": 0.15,
    "final_loss": 0.0098
  },
  "safety_gate_verification": {
    "golden_attacks_evaluated": 52,
    "passed_attacks": 52,
    "score": 1.000,
    "verdict": "PASSED"
  },
  "output_model": {
    "artifact_name": "network_threat_v2.onnx",
    "format": "ONNX_OPSET_17",
    "sha256": "3a7b41e2d9010000e9a2c31e847b2c94b13a7b41e20000000000000000000000"
  }
}
```

---

## 2. Cryptographic Tamper-Sealing

The training audit log is anchored to **TPM 2.0 PCR 12**:
* When a training cycle finishes, the SHA-256 hash of the audit record is extended into PCR 12 via `tpm2_pcrextend`.
* If an attacker modifies historical audit records on disk, the calculated hash chain diverges from the TPM hardware register, providing mathematical proof of log tampering.
```

---

### File: `xinfer-forge/docs/compliance/data-privacy-zero-egress.md`

```markdown
# Data Privacy, Zero-Egress & GDPR Non-PII Guarantees

Continual active learning often raises data privacy concerns: does training on live network traffic leak sensitive personal data or proprietary credentials into the model's weights?

`xinfer-forge` operates under a **Zero-PII / Zero-Egress Invariant**, complying fully with **EU GDPR (Regulation 2016/679)** and industrial trade secret protection standards.

---

## 1. Feature Representation: Zero PII Ingestion

The 32-dimensional continuous feature vectors consumed by `TabularMAE` contain **only statistical, timing, and protocol metrics**:

```text
 32-DIMENSIONAL FEATURE VECTOR CONTENTS:
  • Flow Duration (Seconds)                • Packet Inter-Arrival Mean & StdDev
  • Total Forward / Backward Packets       • TCP Window Size (Bytes)
  • Total Forward / Backward Bytes         • Flow Packets per Second (Throughput)
  • Min, Max, Mean Packet Length           • TCP Header Flags (SYN, RST, PSH, ACK)
  • Protocol Encoding (TCP=1, UDP=2)       • Destination Port Number
```

### What is Explicitly Excluded?
* **Zero Payload Text:** HTTP request bodies, passwords, usernames, and email addresses are discarded prior to vectorization.
* **Zero Patient Records:** Medical HL7 fields, patient names, and DICOM patient IDs are stripped during protocol dissection.
* **No Raw IP Storage:** Network IP addresses are used for spatial-temporal pairing in InfoNCE but are excluded from the continuous training vector.

---

## 2. Absolute $0.00 Cloud Egress Guarantee

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Protected On-Premises Network Enclave                       │
 │                                                             │
 │  [ Edge Appliance ] ──► [ Local Hub ] ──► [ xinfer-forge ]  │
 │                                                     │       │
 │                                                     ▼       │
 │                            [ On-Premises Training Loop ]    │
 └─────────────────────────────────────────────────────────────┘
                                ║
                                ╫ ZERO CLOUD EGRESS ($0.00)
                                ║
                       [ PUBLIC INTERNET ]
```

* **Zero Cloud Data Egress:** Training, validation, compilation, and canary deployment execute 100% on-premises.
* **GDPR Article 25 (Data Protection by Design):** Because raw personal data is never ingested into model weights, the model is not subject to "right-to-be-forgotten" parameter extraction vulnerabilities.
```

