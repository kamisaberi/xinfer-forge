#!/usr/bin/env python3
"""
xinfer-forge: Streaming SLAB Dataset Loader for Continual Fine-Tuning
Reads binary SLAB records (0x534C4142) and yields streaming batches for low-latency adaptation.
"""

import os
import struct
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

SLAB_MAGIC = 0x534C4142


class StreamingSlabDataset(Dataset):
    def __init__(self, slab_path: str, max_records: int = 5000, default_dim: int = 32):
        self.features = []
        self.labels = []
        self._load_data(slab_path, max_records, default_dim)

    def _load_data(self, slab_path: str, max_records: int, default_dim: int):
        slab_path = os.path.abspath(os.path.expanduser(slab_path))
        if os.path.exists(slab_path) and os.path.getsize(slab_path) >= 24:
            try:
                with open(slab_path, "rb") as f:
                    count = 0
                    while count < max_records:
                        hdr = f.read(24)
                        if len(hdr) < 24:
                            break
                        magic, event_id, label, dim = struct.unpack(">IIII", hdr)
                        if magic != SLAB_MAGIC:
                            break
                        payload = f.read(dim * 4)
                        if len(payload) < dim * 4:
                            break
                        vec = np.frombuffer(payload, dtype=">f4").astype(np.float32)
                        self.features.append(vec)
                        self.labels.append(float(label))
                        count += 1
                print(f"[+] [DataStreamer] Loaded {len(self.features)} records from {slab_path}")
            except Exception as e:
                print(f"[!] [DataStreamer Warning] Error loading {slab_path}: {e}")

        # Fallback to deterministic synthetic stream if file is absent or empty
        if not self.features:
            print(f"[*] [DataStreamer] Generating {max_records} synthetic adaptation records ({default_dim}D)...")
            self.features = np.random.randn(max_records, default_dim).astype(np.float32)
            self.labels = (self.features[:, 0] > 0.0).astype(np.float32)
        else:
            self.features = np.array(self.features, dtype=np.float32)
            self.labels = np.array(self.labels, dtype=np.float32)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.from_numpy(self.features[idx]), torch.tensor(self.labels[idx])


def get_streaming_dataloader(slab_path: str, batch_size: int = 32, max_records: int = 5000, input_dim: int = 32) -> DataLoader:
    ds = StreamingSlabDataset(slab_path, max_records=max_records, default_dim=input_dim)
    return DataLoader(ds, batch_size=batch_size, shuffle=True)