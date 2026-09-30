### Part 10: AI Safety & Regulatory Compliance (`compliance/*`)

This section contains 4 compliance audit guides and technical verification frameworks for `xinfer-forge`: satisfying the EU AI Act Article 15 mandates for high-risk cybersecurity AI, meeting NIST SP 800-218 SSDF model integrity requirements, logging immutable training audit records, and verifying zero PII leakage and zero cloud data egress.

---

### File: `xinfer-forge/docs/compliance/eu-ai-act-article-15.md`

```markdown
# EU AI Act Article 15: Accuracy, Robustness & Anti-Poisoning Mandates

Under the European Union Artificial Intelligence Act (**Regulation (EU) 2024/1689**), AI systems deployed in critical infrastructure (including digital networks, water, electricity, and gas management) are classified as **High-Risk AI Systems** (Annex III, Point 2).

`xinfer-forge` is designed to satisfy the statutory technical mandates defined in **Article 15: Accuracy, Robustness and Cybersecurity**.

---

## 1. Traceability to Article 15 Statutory Requirements

| EU AI Act Provision | Statutory Requirement | `xinfer-forge` Architectural Enforcement |
| :--- | :--- | :--- |
| **Article 15(1)** | **Technical Robustness:** High-risk AI systems must achieve an appropriate level of accuracy, robustness, and cybersecurity. | Continual active learning adapts to operational drift, preventing accuracy decay over multi-month deployments. |
| **Article 15(2)** | **Resilience Against Errors & Anomalies:** Systems must be resilient to operational feedback loops and unexpected inputs. | The 8-dimensional latent bottleneck ($z \in \mathbb{R}^8$) rejects anomalous noise while preserving core physical invariants. |
| **Article 15(3)** | **Feedback Loop Control:** Systems that continue learning after deployment must prevent biased outputs from reinforcing errors. | Uncertainty-based curation ($0.40 \le f(x) \le 0.60$) prevents redundant or biased telemetry from destabilizing weights. |
| **Article 15(4)** | **Anti-Poisoning & Adversarial Defense:** Systems must be resilient to data poisoning and adversarial manipulation. | Enforces the immutable **Golden Attacks Safety Gate** ($S(\theta^*) = 1.000$); purges candidate weights on any regression. |

---

## 2. Article 15(4) Anti-Poisoning Conformance Proof

Article 15(4) specifically targets vulnerabilities where adversaries manipulate training inputs to bypass detection. 

`xinfer-forge` satisfies this requirement through its logical conjunction proof:
* Every candidate model $\theta^*$ must successfully flag $100\%$ of historical exploit vectors in `configs/safety/golden_attacks.yaml`.
* If a model update fails to detect even one attack vector, the update is rejected and deleted automatically, preventing adversarial data poisoning from entering production.

---

## 3. Compliance Documentation Export

Generate an Article 15 verification report via CLI:

```bash
forge-cli validate-safety --export-eu-ai-compliance /var/log/sentinel/eu_ai_act_article15.json
```

### Generated Compliance Declaration:
```json
{
  "regulation": "EU Artificial Intelligence Act (Regulation 2024/1689)",
  "article": "Article 15 (Accuracy, Robustness and Cybersecurity)",
  "classification": "Annex III (High-Risk AI System)",
  "model_tested": "network_threat_v2.onnx",
  "golden_attacks_evaluated": 52,
  "safety_score": 1.000,
  "anti_poisoning_circuit": "ACTIVE_VERIFIED",
  "audit_result": "CONFORMANT"
}
```
```

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

---

### Complete in Part 10
- `xinfer-forge/docs/compliance/eu-ai-act-article-15.md`
- `xinfer-forge/docs/compliance/nist-sp-800-218-ssdf.md`
- `xinfer-forge/docs/compliance/auditing-training-runs.md`
- `xinfer-forge/docs/compliance/data-privacy-zero-egress.md`

All 4 AI Safety & Regulatory Compliance files for `xinfer-forge` are now generated.

---

### Files to be Generated in Part 11 (Final Phase for Project 4)

The final phase covers **Troubleshooting & Help Desk Diagnostics** (`troubleshooting/` - 6 files), completing the entire documentation tree for `xinfer-forge`:

1. `troubleshooting/loss-divergence-and-nans.md` (Resolving exploding gradients and numerical instability in MAE)
2. `troubleshooting/safety-gate-rejection-guide.md` (Debugging false negatives during golden attack regression audits)
3. `troubleshooting/nexus-staging-failures.md` (Resolving REST timeouts, connection refused, and invalid URLs)
4. `troubleshooting/python-pep668-venv-issues.md` (Fixing Ubuntu 24.04/26.04 externally-managed-environment errors)
5. `troubleshooting/faq.md` (Technical Frequently Asked Questions)
6. `troubleshooting/support.md` (Issue reporting, security disclosures, and enterprise support SLAs)

Confirm when you are ready to proceed with Part 11.