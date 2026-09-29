---

### File: `xinfer-forge/docs/nexus-integration/automated-wrapper-script.md`

```markdown
# Automated Wrapper Script (`deploy/run_nexus_adaptation.sh`)

`run_nexus_adaptation.sh` orchestrates the complete continual adaptation loop. It handles virtual environment activation, checks lockfiles, executes `forge-cli auto-cycle`, and manages logging output.

---

## 1. Script Architecture (`deploy/run_nexus_adaptation.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# XINFER-FORGE CONTINUAL ADAPTATION WRAPPER
# ==============================================================================
FORGE_VENV="/opt/sentinel-stack/venv"
DATASET_DIR="/var/lib/sentinel-nexus/forge_datasets"
SAFETY_CORPUS="/opt/sentinel-stack/xinfer-forge/configs/safety/golden_attacks.yaml"
NEXUS_API_URL="https://127.0.0.1:9443"
LOG_FILE="/var/log/sentinel/forge_adaptation.log"

export PYTHONPATH="/opt/sentinel-stack/xinfer-forge:${PYTHONPATH:-}"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Starting automated adaptation cycle..." >> "${LOG_FILE}"

# 1. Activate isolated Python environment
# shellcheck source=/dev/null
source "${FORGE_VENV}/bin/activate"

# 2. Invoke Forge CLI in auto-cycle mode
python3 -m forge.cli auto-cycle \
    --watch-dir "${DATASET_DIR}" \
    --safety-corpus "${SAFETY_CORPUS}" \
    --nexus-url "${NEXUS_API_URL}" \
    --epochs 5 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --masking-ratio 0.30 \
    >> "${LOG_FILE}" 2>&1

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Adaptation cycle completed cleanly." >> "${LOG_FILE}"
```

---

## 2. Integration with Systemd Timer

The script is executed automatically via a systemd timer unit (`sentinel-forge.timer`) every hour:

```ini
[Unit]
Description=Hourly Automated Continual AI Adaptation Cycle
After=sentinel-nexus.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```
```

