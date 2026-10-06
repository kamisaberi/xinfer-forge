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
