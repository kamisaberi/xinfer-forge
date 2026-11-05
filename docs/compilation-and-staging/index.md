# Compilation & Fleet Staging

`xinfer-forge` compiles PyTorch checkpoints into production-grade ONNX Opset 17 binaries and stages them to `sentinel-nexus`.

## Section Navigation

- [ONNX Export Pipeline](./onnx-export-pipeline.md): Compiling PyTorch graphs to ONNX Opset 17 and verifying numerical parity.
- [INT8 PTQ Quantization](./int8-ptq-quantization.md): Automated INT8 Post-Training Quantization (PTQ) targeting sub-20µs execution on edge NPUs.
- [Dynamic Batch Axes](./dynamic-batch-axes.md): Supporting dynamic batch dimensions ($[batch\_size, 32]$) for wire-speed fast paths and forensic batches.
- [SHA-256 Checksums](./cryptographic-hashing-sha256.md): Streaming 64 KB block checksum generation and integrity manifest creation.
- [Nexus REST Staging API](./nexus-rest-staging-api.md): Dispatched multipart upload client (`POST /api/v1/ota/stage`).
- [Staged Rollout Lifecycle](./staged-rollout-lifecycle.md): Progression stages (`Shadow Mode` $\to$ `5% Canary` $\to$ `Fleet-Wide`) and `RollbackGuard`.
