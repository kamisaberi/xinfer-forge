---

### File: `xinfer-forge/docs/safety-regression-gate/zero-tolerance-math.md`

```markdown
# Zero-Tolerance Regression Mathematics

In `xinfer-forge`, safety validation is formulated as a **strict logical conjunction**. A candidate model is approved if and only if every golden attack vector produces a reconstruction error exceeding the baseline anomaly threshold.

---

## 1. Formal Mathematical Formulation

Let $\mathcal{A} = \{a_1, a_2, \dots, a_M\}$ represent the corpus of $M$ golden attack vectors ($a_i \in \mathbb{R}^{32}$).

Let $f(a_i; \theta^*)$ represent the reconstruction produced by the candidate parameters $\theta^*$. The reconstruction error $\mathcal{E}(a_i; \theta^*)$ is defined as the Mean Squared Error:

$$\mathcal{E}(a_i; \theta^*) = \frac{1}{D} \sum_{j=1}^{D} \left(a_{i, j} - \hat{a}_{i, j}\right)^2$$

Let $\tau$ denote the non-negotiable anomaly detection threshold ($\tau = 0.082$).

The Safety Gate verification function $S(\theta^*)$ is defined as:

$$S(\theta^*) = \bigwedge_{i=1}^{M} \mathbb{I}\left(\mathcal{E}(a_i; \theta^*) > \tau\right)$$

Where $\mathbb{I}(\cdot)$ is the indicator function:

$$\mathbb{I}(\text{condition}) = \begin{cases} 1, & \text{if condition is TRUE} \\ 0, & \text{if condition is FALSE} \end{cases}$$

---

## 2. Invariant Proof

$$\text{Candidate Approval} \iff S(\theta^*) = 1.000$$

If even a single attack $a_k$ yields $\mathcal{E}(a_k; \theta^*) \le \tau$:

$$S(\theta^*) = 1 \wedge 1 \wedge \dots \wedge 0 \wedge \dots \wedge 1 = 0.000$$

The logical conjunction fails, aborting compilation and deployment.
```

