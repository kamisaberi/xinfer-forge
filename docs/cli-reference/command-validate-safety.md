# Command: `forge-cli validate-safety`

Audits a candidate PyTorch checkpoint against the immutable golden attack corpus (`golden_attacks.yaml`). Enforces the non-negotiable zero-tolerance regression invariant ($S(\theta^*) = 1.000$).

---

## 1. Syntax

```bash
forge-cli validate-safety [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--checkpoint PATH` | File Path | **Required** | Path to candidate PyTorch checkpoint (`.pt`). |
| `--safety-corpus PATH` | File Path | `configs/safety/golden_attacks.yaml` | Path to golden attack manifest. |
| `--threshold FLOAT` | Float | `0.082` | Anomaly reconstruction MSE threshold ($\tau$). |
| `--purge-on-fail` | Boolean | `true` | Securely unlinks checkpoint file if audit fails. |
| `--verify-tpm-seal` | Boolean | `false` | Verifies YAML integrity against TPM 2.0 PCR 14. |

---

## 3. Execution Example (Passing Audit)

```bash
forge-cli validate-safety \
    --checkpoint /tmp/candidate_weights.pt \
    --safety-corpus /opt/sentinel-stack/xinfer-forge/configs/safety/golden_attacks.yaml
```

### Passing Terminal Output
```text
================================================================================
                    IMMUTABLE GOLDEN ATTACKS REGRESSION GATE
================================================================================
Auditing Model Checkpoint: /tmp/candidate_weights.pt
Corpus Path: configs/safety/golden_attacks.yaml (52 Vectors)

 [PASS] ICS-T0831-STUXNET      (Residual MSE: 0.2981 > 0.082)
 [PASS] ICS-T0843-TRITON       (Residual MSE: 0.4120 > 0.082)
 [PASS] ICS-T0855-INDUSTROYER2 (Residual MSE: 0.3412 > 0.082)
 ... (49 additional vectors verified)

--------------------------------------------------------------------------------
Audit Result: 52/52 Historical Attacks Successfully Flagged. Score: 1.000
Status: APPROVED FOR PRODUCTION COMPILATION. Exit Code 0.
================================================================================
```

---

## 4. Execution Example (Poisoning Failure & Purge)

If candidate weights miss a historical exploit:

```text
================================================================================
                    IMMUTABLE GOLDEN ATTACKS REGRESSION GATE
================================================================================
 [PASS] ICS-T0831-STUXNET      (Residual MSE: 0.2981 > 0.082)
 [FAIL] ICS-T0855-INDUSTROYER2 (Residual MSE: 0.0412 <= 0.082) ──► REGRESSION!

--------------------------------------------------------------------------------
[!] AUDIT REJECTED: 1 attack missed! S(θ*) = 0.981 < 1.000
[*] Purge Circuit Triggered: Overwriting and deleting /tmp/candidate_weights.pt
[*] Alert dispatched to Sentinel-Nexus. Exit Code 2.
================================================================================
```

