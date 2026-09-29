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

---

### File: `xinfer-forge/docs/cli-reference/command-train.md`

```markdown
# Command: `forge-cli train`

Executes self-supervised training on a 32-dimensional continuous flow dataset using Masked Autoencoder (MAE) reconstruction and InfoNCE temporal contrastive objectives.

---

## 1. Syntax

```bash
forge-cli train [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--data PATH` | File Path | **Required** | Path to the continuous 32-dim CSV dataset. |
| `--output-checkpoint PATH` | File Path | `candidate.pt` | Output destination for trained PyTorch weights. |
| `--epochs INT` | Integer | `5` | Total training epochs over the dataset. |
| `--batch-size INT` | Integer | `64` | Mini-batch sample size per gradient update. |
| `--learning-rate FLOAT` | Float | `0.001` | AdamW initial learning rate. |
| `--weight-decay FLOAT` | Float | `1e-4` | $L_2$ weight decay regularization. |
| `--masking-ratio FLOAT` | Float | `0.30` | Bernoulli feature masking probability ($p_{\text{mask}}$). |
| `--lambda-contrastive FLOAT`| Float | `0.15` | Weight multiplier ($\lambda$) for InfoNCE loss. |
| `--temperature FLOAT` | Float | `0.07` | InfoNCE logit temperature parameter ($\tau$). |

---

## 3. Execution Example

```bash
forge-cli train \
    --data /var/lib/sentinel-nexus/forge_datasets/forge_dataset_8f1c2a04.csv \
    --output-checkpoint /tmp/candidate_weights.pt \
    --epochs 5 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --masking-ratio 0.30 \
    --lambda-contrastive 0.15
```

### Expected Output
```text
[*] Initializing TabularMAE: 32 -> 16 -> 8 -> 16 -> 32
[*] Target Compute Device: cuda:0 (NVIDIA RTX A4000)
[*] Ingesting Dataset: 5,000 samples (32 continuous dimensions)
Epoch 1/5 [========================================] Loss: 0.0381 (MAE: 0.0345, InfoNCE: 0.0036)
Epoch 2/5 [========================================] Loss: 0.0242 (MAE: 0.0218, InfoNCE: 0.0024)
Epoch 3/5 [========================================] Loss: 0.0165 (MAE: 0.0149, InfoNCE: 0.0016)
Epoch 4/5 [========================================] Loss: 0.0121 (MAE: 0.0109, InfoNCE: 0.0012)
Epoch 5/5 [========================================] Loss: 0.0098 (MAE: 0.0089, InfoNCE: 0.0009)
[+] Model training complete. Candidate checkpoint saved: /tmp/candidate_weights.pt
```
```

---

### File: `xinfer-forge/docs/cli-reference/command-validate-safety.md`

```markdown
# Command: `forge-cli validate-safety`

Audits a candidate PyTorch checkpoint against the immutable golden attack corpus (`golden_attacks.yaml`). Enforces the non-negotiable zero-tolerance regression invariant ($S(\theta^*) = 1.000$).

---

## 1. Syntax

```bash
forge-cli validate-safety [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--checkpoint PATH` | File Path | **Required** | Path to candidate PyTorch checkpoint (`.pt`). |
| `--safety-corpus PATH` | File Path | `configs/safety/golden_attacks.yaml` | Path to golden attack manifest. |
| `--threshold FLOAT` | Float | `0.082` | Anomaly reconstruction MSE threshold ($\tau$). |
| `--purge-on-fail` | Boolean | `true` | Securely unlinks checkpoint file if audit fails. |
| `--verify-tpm-seal` | Boolean | `false` | Verifies YAML integrity against TPM 2.0 PCR 14. |

---

## 3. Execution Example (Passing Audit)

```bash
forge-cli validate-safety \
    --checkpoint /tmp/candidate_weights.pt \
    --safety-corpus /opt/sentinel-stack/xinfer-forge/configs/safety/golden_attacks.yaml
```

### Passing Terminal Output
```text
================================================================================
                    IMMUTABLE GOLDEN ATTACKS REGRESSION GATE
================================================================================
Auditing Model Checkpoint: /tmp/candidate_weights.pt
Corpus Path: configs/safety/golden_attacks.yaml (52 Vectors)

 [PASS] ICS-T0831-STUXNET      (Residual MSE: 0.2981 > 0.082)
 [PASS] ICS-T0843-TRITON       (Residual MSE: 0.4120 > 0.082)
 [PASS] ICS-T0855-INDUSTROYER2 (Residual MSE: 0.3412 > 0.082)
 ... (49 additional vectors verified)

--------------------------------------------------------------------------------
Audit Result: 52/52 Historical Attacks Successfully Flagged. Score: 1.000
Status: APPROVED FOR PRODUCTION COMPILATION. Exit Code 0.
================================================================================
```

---

## 4. Execution Example (Poisoning Failure & Purge)

If candidate weights miss a historical exploit:

```text
================================================================================
                    IMMUTABLE GOLDEN ATTACKS REGRESSION GATE
================================================================================
 [PASS] ICS-T0831-STUXNET      (Residual MSE: 0.2981 > 0.082)
 [FAIL] ICS-T0855-INDUSTROYER2 (Residual MSE: 0.0412 <= 0.082) ──► REGRESSION!

--------------------------------------------------------------------------------
[!] AUDIT REJECTED: 1 attack missed! S(θ*) = 0.981 < 1.000
[*] Purge Circuit Triggered: Overwriting and deleting /tmp/candidate_weights.pt
[*] Alert dispatched to Sentinel-Nexus. Exit Code 2.
================================================================================
```
```

---

### File: `xinfer-forge/docs/cli-reference/command-export-onnx.md`

```markdown
# Command: `forge-cli export-onnx`

Compiles a validated PyTorch checkpoint into an ONNX Opset 17 binary with dynamic batch axes, generating an accompanying cryptographic SHA-256 manifest.

---

## 1. Syntax

```bash
forge-cli export-onnx [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--checkpoint PATH` | File Path | **Required** | Validated PyTorch checkpoint (`.pt`). |
| `--output-onnx PATH` | File Path | `network_threat_v2.onnx` | Destination file for compiled ONNX graph. |
| `--opset-version INT` | Integer | `17` | ONNX Opset specification version. |
| `--model-version STR` | String | `2.0.0` | Semantic version string written to manifest. |

---

## 3. Execution Example

```bash
forge-cli export-onnx \
    --checkpoint /tmp/candidate_weights.pt \
    --output-onnx /opt/sentinel/models/network_threat_v2.onnx \
    --model-version 2.4.0
```

### Expected Output
```text
[*] Exporting PyTorch graph to ONNX Opset 17...
[*] Dynamic batch dimension bound: input [batch_size, 32] -> output [batch_size, 32]
[*] Running onnx.checker.check_model: PASSED
[*] Auditing numerical parity against ONNX Runtime: atol=1e-5 PASSED
[*] Calculating SHA-256: e9a2c31e847b2c94b13a7b41e2d9010000000000000000000000000000000000
[+] Artifacts generated:
    Model    : /opt/sentinel/models/network_threat_v2.onnx (7,412 bytes)
    Manifest : /opt/sentinel/models/network_threat_v2.manifest.json
```
```

---

### File: `xinfer-forge/docs/cli-reference/command-stage.md`

```markdown
# Command: `forge-cli stage`

Submits an exported ONNX model and its cryptographic manifest to `sentinel-nexus` via its authenticated REST API (`POST /api/v1/ota/stage`), initiating a canary fleet rollout.

---

## 1. Syntax

```bash
forge-cli stage [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--onnx-model PATH` | File Path | **Required** | Compiled ONNX model binary. |
| `--manifest PATH` | File Path | **Required** | Accompanying `.manifest.json` file. |
| `--nexus-url URL` | URL | `https://127.0.0.1:9443`| Sentinel-Nexus management REST API URL. |
| `--token STRING` | String | `ENV[NEXUS_TOKEN]` | Administrator Bearer JWT authentication token. |

---

## 3. Execution Example

```bash
forge-cli stage \
    --onnx-model /opt/sentinel/models/network_threat_v2.onnx \
    --manifest /opt/sentinel/models/network_threat_v2.manifest.json \
    --nexus-url https://10.240.0.10:9443 \
    --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Expected Output
```text
[*] Dispatching multipart upload to https://10.240.0.10:9443/api/v1/ota/stage...
[+] HTTP 201 Created: Model staged successfully!
[+] Fleet Staging Initialized:
    Model Version : 2.4.0
    Deployment ID : stage-8f1c2a04
    Current State : STAGE_SHADOW_MODE (48-Hour Baseline Evaluation)
```
```

---

### File: `xinfer-forge/docs/cli-reference/command-auto-cycle.md`

```markdown
# Command: `forge-cli auto-cycle`

Launches the continuous, autonomous active learning daemon. In this mode, `forge-cli` monitors `/var/lib/sentinel-nexus/forge_datasets/`, training, validating, exporting, and staging models without operator intervention.

---

## 1. Syntax

```bash
forge-cli auto-cycle [OPTIONS]
```

---

## 2. Command Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--watch-dir PATH` | Directory | `/var/lib/sentinel-nexus/forge_datasets` | Inotify target directory for new batches. |
| `--safety-corpus PATH` | File Path | `configs/safety/golden_attacks.yaml` | Golden attacks regression file. |
| `--nexus-url URL` | URL | `https://127.0.0.1:9443` | Sentinel-Nexus management endpoint. |
| `--continuous` | Flag | `false` | Keeps daemon resident in memory indefinitely. |
| `--poll-interval INT` | Integer | `10` | Sleep interval (seconds) between directory scans. |

---

## 3. Systemd Execution

In production, `auto-cycle` is managed by systemd:

```bash
sudo systemctl start sentinel-forge
sudo journalctl -u sentinel-forge -f
```

### Live Service Output
```text
[INFO] forge-cli: Inotify watcher armed on /var/lib/sentinel-nexus/forge_datasets/
[INFO] forge-cli: Discovered new curated batch: forge_dataset_8f1c2a04.csv (5,000 samples)
[INFO] forge-cli: Starting TabularMAE adaptation run (5 epochs)...
[INFO] forge-cli: Training complete (Loss: 0.0098). Auditing Golden Attacks Safety Gate...
[INFO] forge-cli: Safety Gate Passed (52/52 Attacks Detected).
[INFO] forge-cli: Compiling to ONNX Opset 17 -> network_threat_v2.onnx
[INFO] forge-cli: Staged to Nexus Hub. Candidate promoted to STAGE_SHADOW_MODE.
[INFO] forge-cli: Batch archived to processed/. Returning to watcher loop.
```
```

---

### File: `xinfer-forge/docs/cli-reference/configuration-files.md`

```markdown
# Master Configuration Manifest (`forge_config.yaml`)

All default hyperparameters, directories, and fleet endpoints can be declared in `/etc/sentinel/forge_config.yaml`.

---

## 1. Master Configuration Schema

```yaml
version: "2.4.0"

# Compute & Device Controls
compute:
  device: "cuda"                     # "cuda" or "cpu"
  cuda_device_id: 0
  num_workers: 4                     # PyTorch DataLoader worker threads
  pin_memory: true

# Self-Supervised Training Hyperparameters
training:
  epochs: 5
  batch_size: 64
  learning_rate: 0.001
  weight_decay: 0.0001
  masking_ratio: 0.30                # 30% stochastic Bernoulli masking
  lambda_contrastive: 0.15           # Weight multiplier for InfoNCE loss
  infonce_temperature: 0.07          # Scale parameter for positive/negative logits
  checkpoint_dir: "/var/lib/sentinel-nexus/checkpoints"

# Immutable Safety Regression Gate
safety_gate:
  corpus_path: "/opt/sentinel-stack/xinfer-forge/configs/safety/golden_attacks.yaml"
  threshold_mse: 0.082               # Minimum reconstruction error to declare anomaly
  zero_tolerance_score: 1.000        # Must detect 100% of historical attacks
  purge_on_failure: true             # Deletes compromised weights immediately
  enforce_tpm_seal: true             # Verifies YAML hash against physical TPM PCR 14

# Model Compilation (ONNX)
compilation:
  opset_version: 17
  output_dir: "/var/lib/sentinel-nexus/models"
  input_tensor_name: "flow_features"
  output_tensor_name: "reconstruction"
  enable_dynamic_axes: true

# Nexus Fleet Synchronization Bridge
nexus_bridge:
  hub_url: "https://10.240.0.10:9443"
  auth_token_file: "/etc/sentinel/certs/nexus_token.jwt"
  watch_dir: "/var/lib/sentinel-nexus/forge_datasets"
  poll_interval_seconds: 5
```
```

---