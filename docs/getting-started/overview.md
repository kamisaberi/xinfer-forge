---

### File: `xinfer-forge/docs/getting-started/overview.md`

```markdown
# Edge Continual Active Learning Without Cloud Connectivity

Static machine learning models deployed in cybersecurity environments begin to degrade from the moment they are placed in production. Normal operational changes—such as new PLC firmware updates, network topology expansions, or updated industrial software—trigger false-positive alert storms. 

Conversely, slowly shifting traffic patterns can be exploited by adversaries to poison detection thresholds over time.

`xinfer-forge` provides **on-premises continual learning**, allowing edge appliances to adapt to environmental drift safely without external cloud dependencies.

---

## 1. The Operational Challenges of Edge AI

```text
 1. THE DRIFT PROBLEM:
    Normal traffic profiles shift naturally over 6 to 12 months.
    Result: Static models decay from 98.4% detection accuracy down to < 65%.

 2. THE AIR-GAP CONSTRAINT:
    Regulated infrastructure (substations, water utilities, hospitals) forbids
    uploading network traces to third-party cloud training clusters.
    Result: Models cannot be retrained using traditional SaaS pipelines.

 3. THE DATA POISONING THREAT:
    Adversaries slowly manipulate normal baselines over weeks ("boiling the frog").
    Result: Naive retraining accepts malicious behaviors as benign traffic.
```

---

## 2. How `xinfer-forge` Solves These Challenges

* **Self-Supervised Masked Autoencoders (MAE):** Discards the requirement for manual data labeling. The network learns the underlying physical and protocol relationships of normal operations by reconstructing randomly masked feature dimensions.
* **InfoNCE Contrastive Regularization:** Enforces temporal stability, clustering related sequential flow records together in a compact 8-dimensional latent space ($z \in \mathbb{R}^8$).
* **The Golden Attacks Safety Gate:** Protects the model against adversarial poisoning. Before candidate weights can be staged, they are benchmarked against an immutable suite of historical cyber-physical attacks. If detection drops on a single attack, the model is rejected and deleted.
```

