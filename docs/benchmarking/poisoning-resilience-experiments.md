# Adversarial Poisoning Resilience Experiments

To prove the efficacy of the **Golden Attacks Safety Gate**, we benchmarked `xinfer-forge` against deliberate adversarial data poisoning ("boiling-the-frog") waves, comparing an unprotected continual autoencoder against Forge's zero-tolerance gate.

---

## 1. Adversarial Attack Setup

An adversary introduces synthetic malicious samples into the training stream, gradually shifting feature 31 (Destination Port) and feature 5 (Minimum Packet Length) over 10 consecutive adaptation cycles toward the signature of an **Industroyer2 (IEC 104)** attack vector:

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Poisoning Injection Schedule (10 Consecutive Batches)       │
 ├─────────────────────────────────────────────────────────────┤
 │ Batch 1 - 3  : 1% Perturbed Samples  (ε = 0.05)             │
 │ Batch 4 - 6  : 5% Perturbed Samples  (ε = 0.15)             │
 │ Batch 7 - 9  : 10% Perturbed Samples (ε = 0.35)             │
 │ Batch 10     : Full Exploit Payload Injected                │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Experimental Results: Detection of Attack Vector

```text
 RESIDUAL MSE LOSS ON INDUSTROYER2 EXPLOIT (Detection Threshold τ = 0.082):

 Residual Error (MSE)
  0.40 ──┐  Unprotected Autoencoder:
         │  Cycle 0: 0.341 (Detected)
  0.30 ──┼──────────┐
         │          └─── Cycle 4: 0.185 (Detected)
  0.20 ──┼───────────────┐
         │               └─── Cycle 6: 0.102 (Marginal)
  0.10 ──┼────────────────────┬──────────────────────────────── Threshold τ = 0.082
  0.08 ──┼────────────────────┼─────────────────────────────────────────────────────
         │                    └─── Cycle 8: 0.041 (MISSED!) ──► POISONED!
  0.00 ──┴──────────┴─────────┴─────────┴─────────┴─────────┴────► Retraining Cycles
         C0        C2        C4        C6        C8        C10
```

### Safety Gate Intervention in `xinfer-forge`

| Training Cycle | Poison Fraction | Unprotected Autoencoder Result | `xinfer-forge` Reaction | Candidate Deployment Status |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | $1\%$ | Loss: $0.320 > \tau$ (PASS) | Safety Gate: $52/52$ Detected | **Approved** |
| **Cycle 4** | $5\%$ | Loss: $0.185 > \tau$ (PASS) | Safety Gate: $52/52$ Detected | **Approved** |
| **Cycle 6** | $10\%$ | Loss: $0.102 > \tau$ (PASS) | Safety Gate: $52/52$ Detected | **Approved** |
| **Cycle 8** | $10\%$ | Loss: $0.041 \le \tau$ (**FAIL**) | **Safety Gate: 51/52 Detected (REJECTED)** | **PURGED IMMEDIATELY** |
| **Cycle 10** | Exploit | Exploit Accepted as Benign | **Prior Baseline θ* Retained (Exploit Caught)**| **Secure** |

---

## 3. Conclusion

At Cycle 8, when the unprotected model's residual error on Industroyer2 dipped below $\tau = 0.082$, `xinfer-forge`'s automated purge circuit triggered, immediately deleting the compromised checkpoint, alerting the SOC, and keeping the unpoisoned baseline active.

