# The Automated Purge Circuit (`safety_gate.py`)

If candidate weights fail the safety gate ($S(\theta^*) < 1.000$), `xinfer-forge` triggers the **Automated Purge Circuit**, physically deleting candidate weights from storage and restoring the previous verified baseline.

---

## 1. Purge Circuit Sequence

```text
 Safety Gate Evaluation: S(θ*) < 1.000 (Regression Detected)
                            │
                            ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 1. Trigger Automated Purge Circuit                          │
 └──────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
 ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
 │ Unlink .pt   │    │ Revert Active│    │ Emit SOC     │
 │ Checkpoints  │    │ Model Link   │    │ Critical     │
 │ from Disk    │    │ to θ_base    │    │ Alarm        │
 └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
 [ Quarantine Training Batch for Forensic Inspection ]
```

---

## 2. Python Implementation (`forge/safety/safety_gate.py`)

```python
import os
import sys
import yaml
import torch
from pathlib import Path
from typing import Dict, Any

class SafetyGate:
    def __init__(self, corpus_path: str, threshold: float = 0.082):
        self.corpus_path = Path(corpus_path)
        self.threshold = threshold
        self.attacks = self._load_corpus()

    def _load_corpus(self) -> torch.Tensor:
        with open(self.corpus_path, "r") as f:
            data = yaml.safe_load(f)
        vectors = [item["vector"] for item in data["attacks"]]
        return torch.tensor(vectors, dtype=torch.float32)

    def evaluate_and_enforce(self, model: torch.nn.Module, checkpoint_path: str) -> bool:
        model.eval()
        with torch.no_grad():
            reconstructed, _ = model(self.attacks)
            # Compute element-wise MSE per attack vector
            mse_errors = torch.mean((self.attacks - reconstructed) ** 2, dim=-1)

        failed_indices = (mse_errors <= self.threshold).nonzero(as_tuple=True)[0]

        if len(failed_indices) > 0:
            print(f"[!] CRITICAL SAFETY BREACH: {len(failed_indices)} historic attacks missed!")
            self._execute_purge(checkpoint_path)
            return False

        print(f"[+] Safety Gate Passed: {len(self.attacks)}/{len(self.attacks)} attacks detected.")
        return True

    def _execute_purge(self, checkpoint_path: str) -> None:
        """Securely deletes compromised candidate weights."""
        p = Path(checkpoint_path)
        if p.exists():
            # Overwrite with random bytes prior to unlinking (anti-recovery)
            with open(p, "wb") as f:
                f.write(os.urandom(p.stat().st_size))
            p.unlink()
            print(f"[*] Candidate checkpoint {checkpoint_path} purged from disk.")
```

