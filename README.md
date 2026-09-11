# xInfer Forge: Autonomous On-Device Model Adaptation & Continuous Learning Engine

xInfer Forge is an asynchronous, self-supervised learning (SSL) and continuous adaptation service designed for edge AI appliances and air-gapped security infrastructure. Working in tandem with the `libxinfer.so` inference runtime and the `blackbox-sentinel` defense platform, xInfer Forge ingests ambient, unlabeled site telemetry, fine-tunes deep learning adapters locally without human supervision, verifies the resulting weights against an automated anti-poisoning regression gate, and executes zero-downtime hot-reloads of compiled ONNX models.

---

## Executive Overview

Static deep learning models deployed in production environments suffer from domain shift: benign baseline network traffic, industrial PLC commands, and physical surroundings vary across every physical facility. Models trained in isolated lab environments inevitably generate false alarms or miss novel site-specific threat variants unless adapted locally.

However, standard fine-tuning approaches introduce severe operational risks:
1. **The Air-Gap Constraint:** Regulated facilities (such as nuclear stations, naval vessels, and high-security data centers) are prohibited from uploading operational data to cloud GPU clusters for re-training.
2. **The Labeling Bottleneck:** Real-time edge appliances process millions of unlabelled events per second. Manual human labeling is impossible.
3. **Adversarial Model Poisoning:** A slow, distributed attack can intentionally pollute unsupervised training data, causing models to gradually accept malicious vectors as benign.

xInfer Forge resolves these structural challenges by implementing a decoupled, self-supervised adaptation pipeline protected by a non-negotiable **Golden Attack Regression Gate**.

---

## Architecture and the Continuous Adaptation Loop

xInfer Forge runs asynchronously as a background daemon or scheduled service, decoupled from the microsecond execution path of the primary defense engine:

```text
===================================================================================
 BLACKBOX SENTINEL APPLIANCE (Real-Time C++20 Defense Engine)
 - Captures raw network packets, logs, and video streams at wire speed.
 - Evaluates events via libxinfer.so using compiled network_threat_v1.onnx.
 - Drops malicious traffic at the kernel level via eBPF/XDP in < 1 millisecond.
 - Appends ambient, unlabeled benign flow features into local circular storage.
===================================================================================
                                         |
                                         | 1. Ambient Telemetry (Parquet / SQLite)
                                         v
===================================================================================
 XINFER FORGE (Asynchronous Python/PyTorch Adaptation Service)
 - Step A: Ingests local ambient flow vectors (forge/collector).
 - Step B: Generates self-supervised training samples via Masked Autoencoding (MAE).
 - Step C: Fine-tunes adapter head on base checkpoint (checkpoints/base_model.pt).
 - Step D: Evaluates adapted model against configs/safety/golden_attacks.yaml.
           * PASS: Continues to compilation.
           * FAIL: Discards weights, retains v1 model, logs security alert.
 - Step E: Compiles PyTorch graph to ONNX (models/network_threat_v2.onnx).
===================================================================================
                                         |
                                         | 2. Hot-Reload Signal (REST API / Unix Socket)
                                         v
===================================================================================
 XINFER ENGINE (Atomic Hot-Swap)
 - libxinfer.so compiles network_threat_v2.onnx into memory in the background.
 - Swaps backend execution pointer atomically with zero packet loss or downtime.
===================================================================================
```

---

## Core Technical Subsystems

### 1. Ambient Telemetry Collector (`forge/collector/`)
The collector queries local circular storage buffers populated by `libblackbox.so`. It pulls events that received low baseline anomaly scores during regular operational hours, filtering out anomalous outliers to build an empirical dataset of site-specific benign traffic.

### 2. Self-Supervised Learning Engine (`forge/datasets/` & `forge/trainers/`)
Because incoming production data is 100% unlabeled, xInfer Forge uses Masked Autoencoding (MAE) for parameter-efficient adaptation:
* **Feature Masking:** A random subset (default: 20%) of the 32 input flow features is zero-masked.
* **Reconstruction Objective:** The neural network is trained to reconstruct the original, unmasked values using Mean Squared Error (MSE) loss:
  $$\mathcal{L}_{\text{MAE}} = \frac{1}{|\mathcal{M}|} \sum_{j \in \mathcal{M}} (x_j - \hat{x}_j)^2$$
* **Adaptation Mechanism:** Over several hundred iterations on local traffic, the model learns the exact correlations and normal boundaries of the customer's specific network topology.

### 3. Automated Safety and Anti-Poisoning Gate (`forge/safety/`)
To protect against adversarial drift and catastrophic forgetting, xInfer Forge enforces a strict, automated validation gate before any model is approved for deployment:
* **Golden Attack Evaluation:** The newly adapted weights are evaluated against a immutable test suite (`configs/safety/golden_attacks.yaml`) containing known attack signatures (such as Nmap SYN port scans, Modbus coil overrides, and brute-force patterns).
* **Deterministic Policy:** The adapted model must achieve a **100% detection rate** on the golden benchmark. If the model fails to flag even a single known attack, the adaptation is immediately aborted, the candidate weights are purged, and the appliance continues running the previous verified model.

### 4. Production ONNX Compiler (`forge/exporter/`)
Approved PyTorch models are converted to optimized ONNX binaries via `torch.onnx.export`:
* Employs ONNX Opset 17 with constant folding and operator simplification.
* Enforces explicit, standardized input tensor names (`input`) and output tensor names (`scores`) matching the dynamic engine bindings in `libblackbox.so`.

### 5. Zero-Downtime Hot-Reload Dispatcher (`forge/dispatcher/`)
Once the new ONNX model is verified and written to disk, the dispatcher issues an authenticated HTTP POST payload to Blackbox Sentinel:
```text
POST /api/v1/control/reload-model
Content-Type: application/json

{"model_path": "/var/lib/sentinel/models/network_threat_v2.onnx"}
```
`xinfer::Engine` loads and optimizes the new model in RAM before performing an atomic pointer swap, updating the active detection model without dropping a single packet.

---

## Repository Layout

```text
xinfer-forge/
├── README.md                         # Product Documentation and Architecture Guide
├── LICENSE                           # Commercial License
├── pyproject.toml                    # Package build specifications
├── requirements.txt                  # Python dependencies
├── setup.py                          # Local CLI installer
│
├── configs/                          # Subsystem Configurations
│   ├── forge_config.yaml             # Main operational settings & paths
│   │
│   ├── training/                     # Domain-Specific Hyperparameters
│   │   ├── network_mae.yaml          # Masked Autoencoder settings for network flows
│   │   ├── log_lora.yaml             # LoRA fine-tuning parameters for Syslog NLP
│   │   └── vision_contrastive.yaml   # Contrastive parameters for CCTV feeds
│   │
│   └── safety/                       # Adversarial Protection Suites
│       └── golden_attacks.yaml       # Non-negotiable historical attack vectors
│
├── forge/                            # Core Application Package
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # Main pipeline runner
│   ├── cli.py                        # Command-line interface (forge-cli)
│   │
│   ├── collector/                    # Data Ingestion Subsystem
│   │   ├── __init__.py
│   │   ├── sqlite_collector.py       # Pulls ambient flow data from blackbox_audit.db
│   │   ├── parquet_buffer.py         # Circular flow buffer reader
│   │   └── api_client.py             # Live metrics reader from Sentinel REST API
│   │
│   ├── datasets/                     # Dataset Transformers
│   │   ├── __init__.py
│   │   ├── masked_flow_dataset.py    # Generates masked pairs for MAE training
│   │   ├── contrastive_dataset.py    # Generates temporal positive/negative pairs
│   │   └── log_token_dataset.py      # Tokenizes raw local text logs
│   │
│   ├── models/                       # Model Architectures & Adapters
│   │   ├── __init__.py
│   │   ├── autoencoder.py            # Deep Autoencoder base neural network
│   │   ├── lora_adapter.py           # LoRA low-rank adapter injection
│   │   └── linear_head.py            # Trainable linear adaptation head
│   │
│   ├── trainers/                     # Adaptation Training Loops
│   │   ├── __init__.py
│   │   ├── base_trainer.py           # Abstract lifecycle and early stopping
│   │   ├── mae_trainer.py            # Masked Autoencoder reconstruction trainer
│   │   ├── contrastive_trainer.py    # InfoNCE contrastive representation trainer
│   │   └── lora_finetuner.py         # Supervised & semi-supervised LoRA tuner
│   │
│   ├── safety/                       # Anti-Poisoning & Validation Gate
│   │   ├── __init__.py
│   │   ├── regression_gate.py        # Evaluates candidate weights against golden set
│   │   └── drift_detector.py         # Detects baseline distribution drift
│   │
│   ├── exporter/                     # ONNX Graph Compilation
│   │   ├── __init__.py
│   │   ├── onnx_exporter.py          # PyTorch to ONNX conversion wrapper
│   │   └── graph_optimizer.py        # Graph simplification and layer fusion
│   │
│   └── dispatcher/                   # Deployment Integration
│       ├── __init__.py
│       └── xinfer_client.py          # Hot-reload dispatcher for Sentinel API
│
├── checkpoints/                      # Model Weights Checkpoint Storage
│   ├── base/                         # Factory-shipped base checkpoints (.pt)
│   │   └── network_threat_base.pt
│   └── adapted/                      # Local adapted checkpoints (.pt)
│       └── network_threat_v2.pt
│
├── deploy/                           # System Automation & Deployment
│   ├── forge.service                 # Systemd timer unit for scheduled adaptation
│   └── run_adaptation.sh             # Manual execution wrapper script
│
└── tests/                            # Verification Test Suite
    ├── test_collector.py             # Ingestion buffer test
    ├── test_mae_trainer.py           # Training loop convergence test
    ├── test_regression_gate.py       # Golden attack safety check test
    └── test_onnx_export.py           # ONNX binary export and structure test
```

---

## System Requirements & Prerequisites

### Hardware Requirements
- **Processor:** x86_64 or ARM64 (Compatible with Intel Core, Xeon, AMD Ryzen, or NVIDIA Jetson)
- **RAM:** Minimum 4\,GB available system RAM for adaptation training loops
- **Disk:** 2\,GB free storage for base checkpoints, datasets, and compiled ONNX binaries

### Software Requirements
- **Operating System:** Ubuntu 22.04 / 24.04 LTS, Debian 12, or RHEL 9
- **Python Version:** Python 3.10, 3.11, or 3.12
- **Core Frameworks:** PyTorch 2.0+, ONNX, ONNX Runtime, NumPy, PyYAML, Requests

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/kamisaberi/xinfer-forge.git
cd xinfer-forge
```

### 2. Create a Virtual Environment & Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install xInfer Forge in Editable Mode

```bash
pip install -e .
```

Verify that the CLI is accessible:
```bash
forge-cli --help
```

---

## Configuration Reference

xInfer Forge is controlled through declarative YAML configuration files.

### Global Configuration (`configs/forge_config.yaml`)

```yaml
appliance:
  sentinel_api_url: "http://localhost:8443"
  db_path: "/home/kami/blackbox-sentinel/build/blackbox_audit.db"
  models_dir: "/home/kami/blackbox-sentinel/models"
  checkpoints_dir: "./checkpoints"

training:
  device: "cpu"                  # Options: "cpu", "cuda"
  input_dim: 32                  # Number of input flow features
  epochs: 10                     # Number of training epochs per cycle
  batch_size: 64                 # Training batch size
  learning_rate: 0.002           # Optimizer learning rate
  mask_ratio: 0.20               # Percentage of features masked for MAE learning
  min_samples_to_train: 100      # Minimum collected samples required before triggering training

safety:
  golden_benchmark_path: "configs/safety/golden_attacks.yaml"
  min_golden_detection_rate: 1.00 # Must detect 100% of non-negotiable attacks (1.00 = 100%)
  max_allowed_reconstruction_drift: 0.25

export:
  onnx_output_name: "network_threat_v2.onnx"
  opset_version: 17
```

### Golden Safety Benchmark (`configs/safety/golden_attacks.yaml`)

```yaml
golden_attacks:
  - id: "ATTACK_PORTSCAN_SYN"
    description: "High-Frequency SYN Scan on Ports 1-1000"
    features: [0.95, 0.88, 0.99, 0.12, 0.85, 0.90, 0.77, 0.81, 0.92, 0.84,
               0.90, 0.75, 0.80, 0.85, 0.95, 0.90, 0.88, 0.92, 0.95, 0.89,
               0.91, 0.85, 0.88, 0.94, 0.90, 0.85, 0.82, 0.89, 0.92, 0.87,
               0.99, 0.95]
    expected_threat_score_min: 0.80

  - id: "ATTACK_MODBUS_UNAUTHORIZED_WRITE"
    description: "SCADA PLC Coil Override on Port 502"
    features: [0.05, 0.99, 0.95, 0.88, 0.90, 0.92, 0.85, 0.89, 0.94, 0.90,
               0.88, 0.91, 0.85, 0.82, 0.89, 0.92, 0.87, 0.99, 0.95, 0.90,
               0.88, 0.84, 0.90, 0.75, 0.80, 0.85, 0.95, 0.90, 0.88, 0.92,
               0.95, 0.89]
    expected_threat_score_min: 0.85
```

---

## Operating Instructions

### Manual Single-Run Execution

To trigger a complete adaptation cycle manually:

```bash
./deploy/run_adaptation.sh
```

Or execute via the CLI tool:

```bash
forge-cli run --config configs/forge_config.yaml
```

#### Typical Execution Output:
```text
==========================================================
  xInfer Forge: Continuous Adaptation & SSL Engine        
==========================================================
[Collector] Collected 1000 ambient flow records from local storage.
[Trainer] Starting Self-Supervised Masked Autoencoding on 1000 local samples...
[Trainer] Epoch [1/10] - Reconstruction Loss: 0.045120
[Trainer] Epoch [5/10] - Reconstruction Loss: 0.008412
[Trainer] Epoch [10/10] - Reconstruction Loss: 0.001840
[Trainer] Local self-supervised adaptation completed successfully.
[Safety Gate] Evaluating adapted model against non-negotiable Golden Attacks...
  PASS: ATTACK_PORTSCAN_SYN - Threat Score: 0.941 >= 0.80
  PASS: ATTACK_MODBUS_UNAUTHORIZED_WRITE - Threat Score: 0.962 >= 0.85
[Safety Gate] VALIDATION PASSED. Detection rate: 100.0%. Safe to deploy.
[Exporter] Compiling adapted PyTorch model to ONNX: models/network_threat_v2.onnx ...
[Exporter] Export complete. Binary size: 8420 bytes.
[Dispatcher] Triggering zero-downtime hot-reload at http://localhost:8443/api/v1/control/reload-model ...
[Dispatcher] Sentinel successfully hot-reloaded model: models/network_threat_v2.onnx!
==========================================================
  Adaptation Cycle Complete: Model Deployed with Zero Lag 
==========================================================
```

---

### Scheduled Automated Background Adaptation (Systemd)

To schedule xInfer Forge to adapt models automatically every 24 hours (e.g., at 2:00 AM during off-peak hours):

1. Copy the systemd unit files to your system directory:
   ```bash
   sudo cp deploy/forge.service /etc/systemd/system/
   ```

2. Enable and start the background service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now forge.service
   ```

3. View execution logs:
   ```bash
   sudo journalctl -u forge.service -f
   ```

---

## Security Model & Anti-Poisoning Guarantees

| Attack Vector | Vulnerability in Standard Continual Learning | xInfer Forge Defense Mechanism |
| :--- | :--- | :--- |
| **Gradual Adversarial Drift** | Attackers slowly modify traffic over 14 days to make intrusions appear normal. | **The Safety Regression Gate:** Every checkpoint is validated against read-only historical attacks. If an attack is missed, adaptation is aborted. |
| **Catastrophic Forgetting** | Adapting to a new subnet causes the model to forget generic malware patterns. | **Parameter-Efficient Tuning:** The core feature representation backbone remains frozen; only adaptation adapter parameters are tuned. |
| **Telemetry Injection** | Injected false events into the audit database pollute training datasets. | **Anomaly Filtering:** Events flagged with an anomaly score $>0.50$ by `libblackbox.so` are excluded from the ambient benign training pool. |
| **Supply Chain Tampering** | An unauthorized user attempts to replace the model file with malicious weights. | **Cryptographic Model Verification:** The exported ONNX model is verified for structural integrity before `libxinfer.so` executes the hot-reload. |

---

## Commercial Value Proposition

1. **Autonomous Site-Specific Baselines:** Eliminates the need for professional services teams to manually calibrate SIEM rules during customer onboarding. The appliance adapts itself to the customer's network topology within 48 hours.
2. **False Positive Suppression:** Adapting to legitimate, unusual internal protocols (such as proprietary industrial SCADA communications) prevents alert fatigue without weakening perimeter threat defenses.
3. **True Sovereign Operation:** No telemetry, feature vectors, or internal system configurations ever exit the physical appliance enclosure.

---

## License

xInfer Forge is proprietary commercial software. Copyright (c) 2026 Kamran Saberifard. All rights reserved. See `LICENSE` for commercial terms and distribution licensing.