# Embedding Proprietary Zero-Day Signatures into the Safety Gate

Every industrial plant features unique equipment, non-standard Modbus register mappings, or proprietary PLC logic blocks. 

This tutorial walks through capturing a site-specific zero-day attack vector, converting it into a normalized 32-dimensional array, and cryptographically sealing it into `configs/safety/golden_attacks.yaml`.

---

## 1. Capturing and Vectorizing the Attack Flow

When a red-team exercise or localized incident occurs:
1. Extract the malicious flow from the `22_dfir` forensic PCAP vault.
2. Vectorize the flow record into a 32-dimensional floating-point array using Subsystem `ModelConfig`:

```python
import numpy as np

# Extracted 32-dimensional vector for a proprietary chemical dosing pump override
custom_attack_vector = [
    0.085, 240.0, 238.0, 96000.0, 95200.0,
    1420.0, 1420.0, 1420.0, 0.0, 65535.0,
    65535.0, 40.0, 40.0, 1420.0, 1420.0,
    0.0024, 0.0008, 0.0003, 0.0, 0.0,
    2823.0, 1129411.0, 0.0, 0.0, 0.0,
    240.0, 0.0, 0.0, 1.01, 1420.0,
    6.0, 502.0
]
```

---

## 2. Appending to `golden_attacks.yaml`

Edit `configs/safety/golden_attacks.yaml` to register the new attack vector:

```yaml
  # ----------------------------------------------------------------------------
  # Vector 53: Site-Specific Chemical Dosing Over-Pressure Command
  # ----------------------------------------------------------------------------
  - id: "PLANT-MUNICH-DOSE-01"
    name: "Proprietary Dosing Pump High-Pressure Override"
    mitre_attack_id: "T0855"
    protocol: "MODBUS_TCP"
    expected_severity: "CRITICAL"
    vector: [
      0.085, 240.0, 238.0, 96000.0, 95200.0,
      1420.0, 1420.0, 1420.0, 0.0, 65535.0,
      65535.0, 40.0, 40.0, 1420.0, 1420.0,
      0.0024, 0.0008, 0.0003, 0.0, 0.0,
      2823.0, 1129411.0, 0.0, 0.0, 0.0,
      240.0, 0.0, 0.0, 1.01, 1420.0,
      6.0, 502.0
    ]
```

Update the `total_attack_vectors` counter from `52` to `53`.

---

## 3. Re-Sealing to Physical TPM 2.0 Silicon

Re-seal the updated corpus measurement into TPM 2.0 PCR 14 to prevent unauthorized tampering:

```bash
forge-cli validate-safety --update-tpm-seal
```

### Expected Output
```text
[*] Re-calculating SHA-256 Digest of configs/safety/golden_attacks.yaml...
[+] New Corpus Digest: 8a2f3c1e42c994b13a7b41e2d901000000000000000000000000000000000000
[*] Sealing measurement into /dev/tpmrm0 (PCR 14)...
[+] TPM 2.0 Sealing Complete. All future adaptation cycles now enforce Vector 53!
```

