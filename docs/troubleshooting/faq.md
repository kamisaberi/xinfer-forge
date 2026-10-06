# Technical Frequently Asked Questions (FAQ)

---

### Q1: Does `xinfer-forge` require labeled training data?
**No.** `xinfer-forge` uses **self-supervised learning**. It trains on unlabeled ambient network telemetry using **Masked Autoencoders (MAE)** and **InfoNCE contrastive learning**, learning the underlying physical and protocol relationships directly from normal traffic.

---

### Q2: Can `xinfer-forge` train models on multi-core CPUs without a GPU?
**Yes.** Because the `TabularMAE` topology is lightweight ($1{,}632\text{ parameters}$), training on a 5,000-flow batch across 5 epochs completes in **$< 20\text{ seconds}$ on a standard 4-core Intel or ARM64 CPU**. A discrete GPU is optional.

---

### Q3: How does Forge protect against adversarial data poisoning?
Every candidate model must pass the **immutable Golden Attacks Safety Gate** (`configs/safety/golden_attacks.yaml`). If an adversary injects perturbations into the training data to desensitize the model to a historical exploit (e.g., Stuxnet or Industroyer), the candidate model will fail detection during safety evaluation and be purged immediately.

---

### Q4: Does retraining cause downtime on edge defense appliances?
**No.** When candidate weights are approved, compiled, and deployed, edge appliances (`blackbox-sentinel`) perform an in-memory atomic pointer swap via `POST /api/v1/control/reload-model`. The active eBPF packet mitigation filter continues dropping packets with **zero downtime**.

---

### Q5: What happens if an edge appliance is completely air-gapped?
`xinfer-forge` executes 100% on-premises within the local security perimeter. It generates zero external network requests and incurs **$0.00 cloud egress fees**.

