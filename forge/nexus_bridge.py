#!/usr/bin/env python3
"""
xInfer Forge - Sentinel Nexus Bridge
1. Locates the latest curated edge dataset exported by Nexus.
2. Computes the SHA-256 hash of the newly trained ONNX model.
3. Automatically stages candidate weights into Nexus via REST API.
"""

import os
import sys
import glob
import json
import hashlib
import urllib.request
import urllib.error
import shutil

NEXUS_REST_URL = os.environ.get("NEXUS_REST_URL", "http://localhost:9443")
NEXUS_DATASET_DIR = os.environ.get("NEXUS_DATASET_DIR", "/var/lib/sentinel-nexus/forge_datasets")
NEXUS_MODELS_DIR = os.environ.get("NEXUS_MODELS_DIR", "/home/kami/sentinel-nexus/models")

def get_latest_nexus_dataset(dataset_dir=NEXUS_DATASET_DIR):
    """
    Finds the most recent dataset curated by Sentinel Nexus.
    Returns path to CSV and path to manifest, or None.
    """
    if not os.path.exists(dataset_dir):
        print(f"[-] Nexus dataset directory does not exist: {dataset_dir}")
        return None

    csv_files = glob.glob(os.path.join(dataset_dir, "forge_dataset_*.csv"))
    if not csv_files:
        print(f"[*] No curated datasets found in {dataset_dir}")
        return None

    # Sort by modification time (most recent first)
    csv_files.sort(key=os.path.getmtime, reverse=True)
    latest_csv = csv_files[0]
    manifest = latest_csv.replace(".csv", ".manifest.json")

    print(f"[+] Found latest Nexus dataset: {latest_csv}")
    if os.path.exists(manifest):
        with open(manifest, "r") as mf:
            meta = json.load(mf)
            print(f"    Total Samples: {meta.get('total_samples')}, "
                  f"High Uncertainty: {meta.get('high_uncertainty_samples')}, "
                  f"Kernel Drops: {meta.get('kernel_drop_samples')}")

    return latest_csv

def calculate_sha256(file_path):
    """Computes cryptographic SHA-256 checksum of file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def stage_model_to_nexus(onnx_model_path, nexus_url=NEXUS_REST_URL, models_dir=NEXUS_MODELS_DIR):
    """
    Copies trained ONNX model to Nexus repository and stages it in SHADOW_MODE.
    """
    if not os.path.exists(onnx_model_path):
        print(f"[-] Error: Model file not found: {onnx_model_path}")
        return False

    model_filename = os.path.basename(onnx_model_path)
    model_sha256 = calculate_sha256(onnx_model_path)
    print(f"[*] Model: {model_filename}")
    print(f"    SHA-256: {model_sha256}")

    # 1. Copy model into Nexus models repository if accessible
    os.makedirs(models_dir, exist_ok=True)
    target_dest = os.path.join(models_dir, model_filename)
    try:
        shutil.copyfile(onnx_model_path, target_dest)
        print(f"[+] Model copied to Nexus repository: {target_dest}")
    except Exception as e:
        print(f"[!] Warning: Could not copy directly to {target_dest}: {e}")

    # 2. Call Nexus REST API to stage candidate model
    stage_endpoint = f"{nexus_url}/api/v1/ota/stage"
    payload = {
        "version": model_filename,
        "sha256": model_sha256,
        "url": f"/models/{model_filename}"
    }

    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            stage_endpoint,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            print(f"[+] Model staged successfully in Nexus!")
            print(f"    Status: {res_body.get('status')}")
            print(f"    Current Stage: {res_body.get('stage')} (Passive shadow evaluation)")
            return True

    except urllib.error.URLError as e:
        print(f"[-] Could not communicate with Nexus API at {stage_endpoint}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 nexus_bridge.py get-dataset")
        print("  python3 nexus_bridge.py stage <path_to_model.onnx>")
        sys.exit(1)

    action = sys.argv[1]
    if action == "get-dataset":
        dataset = get_latest_nexus_dataset()
        if dataset:
            print(dataset)
        else:
            sys.exit(1)
    elif action == "stage":
        if len(sys.argv) < 3:
            print("Error: Missing path to .onnx file")
            sys.exit(1)
        model_path = sys.argv[2]
        success = stage_model_to_nexus(model_path)
        sys.exit(0 if success else 1)