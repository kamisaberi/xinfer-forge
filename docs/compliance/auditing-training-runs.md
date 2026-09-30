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

