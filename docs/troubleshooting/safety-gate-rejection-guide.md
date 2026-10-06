# Safety Gate Rejection Diagnostics & Remediation

When candidate weights fail the Golden Attacks Safety Gate, `forge-cli` exits with code `2` (`EXIT_SAFETY_VIOLATION`), logs the failure to `/var/log/sentinel/forge_adaptation.log`, and purges the checkpoint file.

---

## 1. Diagnosing Failed Attack Vectors

Inspect the adaptation log to identify the specific attack vector that dropped below threshold $\tau = 0.082$:

```bash
tail -n 30 /var/log/sentinel/forge_adaptation.log | grep -A 2 -B 2 "FAIL"
```

### Sample Log Trace:
```text
[INFO] Evaluating Vector 14/52: ICS-T0843-TRITON
[FAIL] ICS-T0843-TRITON: Observed Residual MSE 0.0412 <= Required Threshold 0.0820
[!] CRITICAL: Regression detected on Triton TriStation emergency shutdown override!
[*] Purge circuit executed: Unlinking candidate checkpoint /tmp/candidate_weights.pt
```

---

## 2. Common Causes & Fixes

| Root Cause | Diagnostic Indicator | Remediation Step |
| :--- | :--- | :--- |
| **Overfitting on Small Batch** | Sample count $< 1{,}000$ rows in dataset. | Increase minimum batch threshold in `DatasetCurator.cpp` to $\ge 5{,}000$ flows. |
| **Learning Rate Too High** | Early layer features destroyed after Epoch 1. | Reduce `--learning-rate` to `0.0005` with Cosine Annealing. |
| **Adversarial Poisoning** | Quarantined CSV contains clusters closely matching the missed exploit. | Purge the contaminated batch from `/var/lib/sentinel-nexus/forge_datasets/`. |
| **Corrupted Normalization** | Feature values exceed $[0.0, 1.0]$ bounds. | Re-validate min-max clamping rules in `model_config.yaml`. |

