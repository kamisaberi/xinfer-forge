### Part 7: `forge-cli` Command Reference (`cli-reference/*`)

This section contains 7 technical reference guides covering the `forge-cli` binary: global syntax, environment variable overrides, subcommands (`train`, `validate-safety`, `export-onnx`, `stage`, `auto-cycle`), and declarative configuration manifests.

---

### File: `xinfer-forge/docs/cli-reference/cli-overview.md`

```markdown
# `forge-cli` Command Line Interface Overview

`forge-cli` is the primary executable interface for `xinfer-forge`. It provides modular commands for model training, anti-poisoning validation, ONNX compilation, fleet staging, and autonomous background execution.

---

## 1. Global Syntax

```bash
forge-cli [OPTIONS] COMMAND [ARGS]...
```

### Global Options

| Option | Environment Variable | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `--config PATH` | `FORGE_CONFIG` | `/etc/sentinel/forge_config.yaml` | Path to master configuration YAML. |
| `--device [cpu\|cuda]` | `FORGE_DEVICE` | Auto-detect | Execution backend for PyTorch computations. |
| `--log-level [DEBUG\|INFO\|WARN\|ERROR]` | `LOG_LEVEL` | `INFO` | Console logging verbosity. |
| `--version` | N/A | N/A | Displays version and exits. |
| `--help` | N/A | N/A | Displays CLI usage documentation. |

---

## 2. Command Tree Summary

* **`forge-cli train`**: Trains a Tabular Masked Autoencoder (MAE) on a specified NetFlow CSV dataset.
* **`forge-cli validate-safety`**: Audits a candidate checkpoint against the immutable golden attack corpus.
* **`forge-cli export-onnx`**: Compiles PyTorch `.pt` weights into an ONNX Opset 17 binary.
* **`forge-cli stage`**: Dispatches an ONNX model and manifest to `sentinel-nexus`.
* **`forge-cli auto-cycle`**: Launches the continuous, autonomous inotify adaptation loop.
* **`forge-cli diag`**: Runs environment, PyTorch, CUDA, and ONNX diagnostic self-tests.

---

## 3. Exit Codes

`forge-cli` adheres to deterministic POSIX process exit codes for integration into automated wrappers and systemd daemons:

| Exit Code | Identifier | Description |
| :--- | :--- | :--- |
| `0` | `EXIT_SUCCESS` | Operation completed cleanly without warnings. |
| `1` | `EXIT_GENERAL_ERROR` | Runtime error, missing file, or invalid configuration. |
| `2` | `EXIT_SAFETY_VIOLATION` | Safety Gate rejection: Candidate model failed $\ge 1$ golden attack. |
| `3` | `EXIT_NEXUS_UNREACHABLE`| Staging error: Fleet orchestrator returned HTTP error or timeout. |
```

