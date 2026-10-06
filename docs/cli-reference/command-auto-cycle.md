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

