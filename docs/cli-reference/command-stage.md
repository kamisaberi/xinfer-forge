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