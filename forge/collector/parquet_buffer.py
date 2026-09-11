import os
import numpy as np

class ParquetBufferCollector:
    """Reads circular telemetry feature buffers formatted as Parquet/Binary chunks."""
    def __init__(self, buffer_dir="/var/log/sentinel/flows", input_dim=32):
        self.buffer_dir = buffer_dir
        self.input_dim = input_dim

    def collect_features(self, max_records=5000):
        if not os.path.exists(self.buffer_dir):
            return np.empty((0, self.input_dim), dtype=np.float32)

        collected = []
        try:
            for filename in sorted(os.listdir(self.buffer_dir)):
                if filename.endswith(".bin") or filename.endswith(".parquet"):
                    filepath = os.path.join(self.buffer_dir, filename)
                    with open(filepath, "rb") as f:
                        raw = np.fromfile(f, dtype=np.float32)
                        if len(raw) % self.input_dim == 0:
                            matrix = raw.reshape(-1, self.input_dim)
                            collected.append(matrix)

                if sum(len(c) for c in collected) >= max_records:
                    break

            if collected:
                features = np.vstack(collected)[:max_records]
                print(f"[ParquetCollector] Loaded {len(features)} records from {self.buffer_dir}.")
                return features
        except Exception as e:
            print(f"[ParquetCollector Warning] Buffer read encountered: {e}")

        return np.empty((0, self.input_dim), dtype=np.float32)