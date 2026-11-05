# Architecture & Low-Level Design

`xinfer-forge` operates as a background continual learning daemon (`forge-cli auto-cycle`) fine-tuning deep neural representations in-place without cloud connectivity.

## Section Navigation

- [Continual Learning Architecture](./continual-learning-architecture.md): The 5-stage adaptation loop, cgroup v2 resource isolation, and process priority.
- [Concept Drift Problem](./the-concept-drift-problem.md): Mathematical formulation of covariate shift, concept shift, and 12-month model decay.
- [Adversarial Poisoning Problem](./the-adversarial-poisoning-problem.md): Mathematical model of "boiling-the-frog" data poisoning attacks.
- [Closed-Loop Flywheel Design](./closed-loop-flywheel-design.md): Data flow connecting edge appliances, Nexus hubs, and Forge training loops.
- [Air-Gapped Execution Model](./air-gapped-execution-model.md): On-premises operational invariants, pre-seeded dependencies, and $0.00 cloud egress.
