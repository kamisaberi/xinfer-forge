#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$FORGE_ROOT"

echo "======================================================================"
echo "  XINFER-FORGE: CONTINUOUS ADAPTATION & NEXUS STAGING PIPELINE"
echo "======================================================================"

# 1. Fetch latest curated dataset from Sentinel Nexus
echo "[*] Step 1: Querying Sentinel Nexus for curated edge dataset..."
LATEST_DATASET=$(python3 forge/nexus_bridge.py get-dataset 2>/dev/null || true)

if [ -z "$LATEST_DATASET" ] || [ ! -f "$LATEST_DATASET" ]; then
    echo "[!] No new dataset from Nexus yet. Falling back to ambient site buffer..."
    DATASET_ARG=""
else
    echo "[+] Utilizing Nexus Curated Edge Dataset: $LATEST_DATASET"
    DATASET_ARG="--dataset $LATEST_DATASET"
fi

# 2. Run existing training & safety gate validation
echo "[*] Step 2: Executing Self-Supervised Retraining (MAE / InfoNCE)..."
# Invokes existing adaptation workflow without modifying it
./deploy/run_adaptation.sh $DATASET_ARG

# 3. Locate compiled ONNX model
CANDIDATE_MODEL="models/network_threat_v2.onnx"

if [ ! -f "$CANDIDATE_MODEL" ]; then
    echo "[-] Error: Expected candidate model $CANDIDATE_MODEL was not generated."
    exit 1
fi

# 4. Stage validated model into Sentinel Nexus
echo "[*] Step 3: Staging validated candidate weights to Sentinel Nexus..."
python3 forge/nexus_bridge.py stage "$CANDIDATE_MODEL"

echo "======================================================================"
echo "[+] Continuous Adaptation Cycle Complete!"
echo "    Candidate model is now in SHADOW_MODE on Sentinel Nexus."
echo "======================================================================"