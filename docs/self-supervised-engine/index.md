# Self-Supervised Engine

`xinfer-forge` uses an asymmetric Tabular Masked Autoencoder (MAE) combined with InfoNCE contrastive learning to learn flow representations without manual labels.

## Section Navigation

- [MAE Topology](./mae-architecture.md): Asymmetric $32 \to 16 \to 8 \to 16 \to 32$ hourglass autoencoder architecture.
- [Stochastic Masking Strategy](./stochastic-masking-strategy.md): $30\%$ stochastic Bernoulli feature masking for tabular flow vectors.
- [InfoNCE Contrastive Learning](./infonce-contrastive-learning.md): Temporal positive pair construction and cosine similarity loss formulations.
- [Latent Embedding Space](./latent-embedding-space.md): $8$-dimensional bottleneck geometry ($z \in \mathbb{R}^8$) and outlier separation mechanics.
- [Loss Optimization Math](./loss-optimization-math.md): Composite loss formulation ($\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MAE}} + \lambda \mathcal{L}_{\text{InfoNCE}}$).
- [Neural Layer Specifications](./neural-layer-specifications.md): Layer dimensions, $1{,}632$ parameter counts, and `LeakyReLU(0.1)` activations.
- [Hyperparameter Tuning](./hyperparameter-tuning.md): Production baselines, AdamW optimizer settings, and Cosine Annealing schedules.
