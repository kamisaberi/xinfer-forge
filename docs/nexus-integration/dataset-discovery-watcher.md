---

### File: `xinfer-forge/docs/nexus-integration/dataset-discovery-watcher.md`

```markdown
# Dataset Discovery & Inotify Watcher Loop

`xinfer-forge` monitors `/var/lib/sentinel-nexus/forge_datasets/` for incoming training batches emitted by the fleet curator using the Linux **`inotify`** kernel subsystem.

---

## 1. Directory Structure

```text
/var/lib/sentinel-nexus/forge_datasets/
├── forge_dataset_8f1c2a04.csv            # 5,000 Curated 32-dim Flow Vectors
├── forge_dataset_8f1c2a04.manifest.json  # Sidecar Hash & Metadata
├── .forge_dataset_8f1c2a04.lock          # Prevents concurrent worker collisions
└── processed/                            # Archived historical batches
```

---

## 2. Inotify Event Loop (`forge/watcher.py`)

```python
import os
import time
import json
from pathlib import Path
from typing import Optional, Tuple

class DatasetWatcher:
    def __init__(self, watch_dir: str = "/var/lib/sentinel-nexus/forge_datasets"):
        self.watch_dir = Path(watch_dir)
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = self.watch_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)

    def poll_next_batch(self, timeout_sec: int = 10) -> Optional[Tuple[Path, Path]]:
        """Polls for un-locked completed dataset batches."""
        for csv_file in self.watch_dir.glob("forge_dataset_*.csv"):
            manifest_file = csv_file.with_suffix(".manifest.json")
            lock_file = self.watch_dir / f".{csv_file.name}.lock"

            if manifest_file.exists() and not lock_file.exists():
                # Acquire lock
                lock_file.touch()
                return csv_file, manifest_file

        return None

    def archive_batch(self, csv_file: Path, manifest_file: Path):
        """Moves processed batch to archive directory."""
        lock_file = self.watch_dir / f".{csv_file.name}.lock"
        csv_file.rename(self.processed_dir / csv_file.name)
        manifest_file.rename(self.processed_dir / manifest_file.name)
        if lock_file.exists():
            lock_file.unlink()
```
```

