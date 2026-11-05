# Safety Regression Gate

Before any candidate model can be deployed, it must pass through an immutable, zero-tolerance Golden Attacks Safety Gate (`configs/safety/golden_attacks.yaml`).

## Section Navigation

- [Safety Gate Philosophy](./safety-gate-philosophy.md): The zero-tolerance regression invariant preventing catastrophic forgetting and poisoning.
- [Golden Attacks Corpus](./golden-attacks-corpus.md): YAML manifest schema (`golden_attacks.yaml`) storing 52 normalized historical exploit vectors.
- [Threat Categories Covered](./threat-categories-covered.md): Coverage across industrial OT sabotage (Stuxnet, Triton, Industroyer) and C2 beacons.
- [Zero-Tolerance Math](./zero-tolerance-math.md): Strict logical conjunction formulation ($S(\theta^*) = \bigwedge \mathbb{I}(\mathcal{E} > \tau)$).
- [Automated Purge Circuit](./automated-purge-circuit.md): Automated checkpoint unlinking and anti-recovery file overwrites upon audit failure.
- [Alert Dispatch on Regression](./alert-dispatch-on-regression.md): CISO incident escalation protocols and CSV dataset quarantine.
- [TPM PCR Sealing](./tpm-pcr-sealing.md): Sealing the golden attack corpus hash against physical TPM 2.0 PCR 7 and PCR 14.
