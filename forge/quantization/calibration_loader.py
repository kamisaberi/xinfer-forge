#!/usr/bin/env python3
"""
xinfer-forge: Calibration Dataset Loader for PTQ
Ingests representative SLAB binary records or synthetic feature tensors
to compute scale (S) and zero-point (Z) quantization factors.
"""

import os
import struct
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

SLAB_MAGIC = 0x534C4142


class SlabCalibrationDataset(Dataset):
    def __init__(self, slab_path: str, num_samples: int = 500, default_dim: int = 32):
        self.features = []
        self.labels = []
        self._load_slab(slab_path, num_samples, default_dim)

    def _load_slab(self, slab_path: str, num_samples: int, default_dim: int):
        if os.path.exists(slab_path) and os.path.getsize(slab_path) >= 24:
            try:
                with open(slab_path, "rb") as f:
                    count = 0
                    while count < num_samples:
                        hdr_data = f.read(24)
                        if len(hdr_data) < 24:
                            break
                        magic, event_id, label, dim = struct.unpack(">IIII", hdr_data)
                        if magic != SLAB_MAGIC:
                            break
                        payload_data = f.read(dim * 4)
                        if len(payload_data) < dim * 4:
                            break
                        feature_vec = np.frombuffer(payload_data, dtype=">f4").astype(np.float32)
                        self.features.append(feature_vec)
                        self.labels.append(float(label))
                        count += 1
            except Exception as e:
                print(f"[!] [CalibrationLoader] Error parsing SLAB file {slab_path}: {e}")

        if not self.features:
            print(f"[*] [CalibrationLoader] Generating {num_samples} synthetic calibration vectors ({default_dim}D)...")
            self.features = np.random.randn(num_samples, default_dim).astype(np.float32)
            self.labels = np.random.choice([0, 1], size=num_samples).astype(np.float32)
        else:
            self.features = np.array(self.features, dtype=np.float32)
            self.labels = np.array(self.labels, dtype=np.float32)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.from_numpy(self.features[idx]), torch.tensor(self.labels[idx])


def get_calibration_loader(slab_path: str, batch_size: int = 32, num_samples: int = 500, input_dim: int = 32) -> DataLoader:
    ds = SlabCalibrationDataset(slab_path=slab_path, num_samples=num_samples, default_dim=input_dim)
    return DataLoader(ds, batch_size=batch_size, shuffle=False)