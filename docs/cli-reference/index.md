# CLI Reference (`forge-cli`)

`forge-cli` is the primary executable interface for training, validating, compiling, staging, and executing autonomous adaptation cycles.

## Section Navigation

- [CLI Overview](./cli-overview.md): Global options, command tree summary, and POSIX exit code specification.
- [forge-cli train](./command-train.md): Command parameters and execution examples for self-supervised MAE training.
- [forge-cli validate-safety](./command-validate-safety.md): Auditing candidate checkpoints against the golden attacks regression gate.
- [forge-cli export-onnx](./command-export-onnx.md): Exporting PyTorch `.pt` checkpoints to ONNX Opset 17 binaries.
- [forge-cli stage](./command-stage.md): Dispatching ONNX models and manifests to `sentinel-nexus`.
- [forge-cli auto-cycle](./command-auto-cycle.md): Launching the continuous autonomous inotify adaptation loop.
- [Configuration Manifests](./configuration-files.md): Master YAML configuration schema (`forge_config.yaml`).
