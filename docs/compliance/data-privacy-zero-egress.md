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

