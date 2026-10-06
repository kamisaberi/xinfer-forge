# System Requirements & Prerequisites

Review the toolchain, virtual environment requirements, and hardware dependencies before running `xinfer-forge`.

---

## 1. Operating System & Python Runtime

* **Operating System:** Ubuntu 24.04 LTS (Noble Numbat) or Ubuntu 26.04 (Devel) 64-bit Linux.
* **Python Runtime:** Python **>= 3.10** (Recommended: Python 3.12).
* **Package Management Isolation:** Strict compliance with **PEP 668** (Externally Managed Environments). All Python dependencies must reside inside an isolated virtual environment (`/opt/sentinel-stack/venv`).

---

## 2. Hardware Resource Sizing

`xinfer-forge` runs on both multi-core CPUs and hardware GPUs:

| Hardware Component | Minimum (Edge Gateway / Model S-1000) | Recommended (Enterprise Server / Model S-5000) |
| :--- | :--- | :--- |
| **CPU Architecture** | 4-Core x86_64 or ARM64 (e.g., RK3588, Core Ultra) | 16-Core Intel Xeon / AMD EPYC |
| **GPU Acceleration** | Optional (PyTorch CPU fallback supported) | NVIDIA RTX A4000 (16GB) or L4 (24GB) |
| **System Memory (RAM)**| 8 GB DDR4/DDR5 | 32 GB DDR5 ECC Registered |
| **Storage Space** | 10 GB Available NVMe SSD | 50 GB High-Endurance NVMe SSD |

---

## 3. Required Python Packages

The virtual environment requires the following versions:

```text
torch >= 2.2.0
torchvision >= 0.17.0
onnx >= 1.15.0
onnxruntime >= 1.17.0
numpy >= 1.24.0, < 2.0.0
pyyaml >= 6.0.1
requests >= 2.31.0
tqdm >= 4.66.0
```

