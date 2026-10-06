# Benchmarking Methodology & Continual Drift Protocols

Evaluating continual learning systems requires testing beyond static train/test dataset splits. Traditional static benchmarks fail to capture how models behave when network distributions shift or when adversaries deliberately inject poisoned telemetry.

`xinfer-forge` is evaluated using **Dynamic Drift Simulation Protocols** across multi-month synthetic and captured network timelines.

---

## 1. Testbed Hardware Specifications

Continual learning experiments were executed across two representative hardware baselines:

| Specification | Edge Industrial Appliance (Model S-1000) | Enterprise AI Server (Model S-5000) |
| :--- | :--- | :--- |
| **Processor** | Intel Core Ultra 7 165H (16 Cores, 3.8 GHz Turbo) | Dual Intel Xeon Platinum 8480+ (112 Cores) |
| **GPU Accelerator**| NPU.3720 (Integrated) / CPU Mode | NVIDIA RTX A4000 (16 GB VRAM) / L4 (24 GB) |
| **Memory** | 16 GB LPDDR5-6400 ECC | 128 GB DDR5-4800 Registered ECC |
| **Storage** | 128 GB Industrial NVMe M.2 SSD | 2x 1.92 TB Enterprise U.2 NVMe SSDs (RAID 1) |
| **OS / Runtime** | Ubuntu 24.04 LTS (Kernel 6.8, Python 3.12) | Ubuntu 24.04 LTS (Kernel 6.8, CUDA 12.2) |

---

## 2. Dynamic Drift Simulation Protocol

Experiments simulate realistic network drift across $180\text{ operational days}$ by injecting three distinct statistical shifts:

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ CONTINUAL DRIFT GENERATION TIMELINE (180 Days)              │
 ├─────────────────────────────────────────────────────────────┤
 │ Phase 1: Days 0 - 30   ──► Stable Baseline Operational Norm │
 │ Phase 2: Days 31 - 90  ──► Linear Covariate Shift           │
 │                            (Firmware upgrade shifts packet  │
 │                             lengths and duration by +15%)   │
 │ Phase 3: Days 91 - 180 ──► Concept Shift & Expansion        │
 │                            (20 new field PLCs added;        │
 │                             polling intervals cut to 50ms)  │
 └─────────────────────────────────────────────────────────────┘
```

---

## 3. Evaluation Metrics Recorded

* **Reconstruction Mean Squared Error ($\mathcal{L}_{\text{MSE}}$):** Baseline reconstruction loss on ambient traffic.
* **Area Under the ROC Curve (ROC-AUC):** Metric tracking true positive vs. false positive rate across 52 golden attacks.
* **Catastrophic Forgetting Ratio ($R_{\text{forget}}$):** Degradation in detection accuracy on Day 0 attacks after Day 180 adaptation:

$$R_{\text{forget}} = \frac{\text{Accuracy}_{\text{Day 0}}(\theta_{\text{Day 0}}) - \text{Accuracy}_{\text{Day 0}}(\theta_{\text{Day 180}})}{\text{Accuracy}_{\text{Day 0}}(\theta_{\text{Day 0}})}$$

In `xinfer-forge`, the Golden Attacks Safety Gate mathematically bounds $R_{\text{forget}} = 0.000$.

