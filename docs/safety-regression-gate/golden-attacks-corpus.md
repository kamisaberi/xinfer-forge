# Golden Attacks Corpus Structure (`golden_attacks.yaml`)

The golden attack corpus is declared in `configs/safety/golden_attacks.yaml`. It contains normalized 32-dimensional feature vectors representing authentic historical exploits, protocol injections, and zero-day attacks.

---

## 1. Corpus Manifest Schema

```yaml
version: "2.0.0"
corpus_metadata:
  total_attack_vectors: 52
  feature_dimension: 32
  minimum_detection_threshold_mse: 0.082
  sha256_digest: "e9a2c31e847b2c94b13a7b41e2d9010000000000000000000000000000000000"

attacks:
  # ----------------------------------------------------------------------------
  # Vector 01: Siemens S7 Centrifuge Frequency Injection (Stuxnet)
  # ----------------------------------------------------------------------------
  - id: "ICS-T0831-STUXNET"
    name: "Stuxnet Siemens S7 Centrifuge Tampering"
    mitre_attack_id: "T0831"
    protocol: "S7COMM"
    expected_severity: "CRITICAL"
    vector: [
      0.042, 120.0, 118.0, 48000.0, 46000.0,
      1420.0, 1420.0, 1420.0, 0.0, 65535.0,
      65535.0, 40.0, 40.0, 1420.0, 1420.0,
      0.0012, 0.0005, 0.0001, 0.0, 0.0,
      2400.0, 960000.0, 0.0, 0.0, 0.0,
      120.0, 0.0, 0.0, 1.04, 1420.0,
      6.0, 102.0
    ]

  # ----------------------------------------------------------------------------
  # Vector 02: Schneider Triconex Emergency Shutdown Override (Triton)
  # ----------------------------------------------------------------------------
  - id: "ICS-T0843-TRITON"
    name: "Triton TriStation Safety System Override"
    mitre_attack_id: "T0843"
    protocol: "TRISTATION_TSAP"
    expected_severity: "CRITICAL"
    vector: [
      0.180, 450.0, 420.0, 180000.0, 168000.0,
      64.0, 1420.0, 400.0, 120.0, 32768.0,
      32768.0, 20.0, 20.0, 400.0, 400.0,
      0.0045, 0.0012, 0.0008, 0.0, 0.0,
      2500.0, 1000000.0, 0.0, 0.0, 12.0,
      450.0, 0.0, 0.0, 1.07, 400.0,
      6.0, 19999.0
    ]

  # ----------------------------------------------------------------------------
  # Vector 03: High-Voltage Circuit Breaker Trip (Industroyer2)
  # ----------------------------------------------------------------------------
  - id: "ICS-T0855-INDUSTROYER2"
    name: "Industroyer2 IEC 60870-5-104 Telecontrol Switchgear Trip"
    mitre_attack_id: "T0855"
    protocol: "IEC_60870_5_104"
    expected_severity: "CRITICAL"
    vector: [
      0.015, 12.0, 10.0, 1850.0, 1420.0,
      48.0, 185.0, 154.1, 24.2, 65535.0,
      65535.0, 20.0, 20.0, 154.1, 142.0,
      0.0008, 0.0002, 0.0001, 0.0, 0.0,
      800.0, 123333.0, 0.0, 0.0, 4.0,
      12.0, 0.0, 0.0, 1.30, 154.1,
      6.0, 2404.0
    ]
```

---

## 2. In-Memory Vector Representation

Vectors in `golden_attacks.yaml` are stored normalized according to the transformation rules declared in Subsystem `ModelConfig`. Values are loaded into contiguous PyTorch evaluation tensors during startup.

