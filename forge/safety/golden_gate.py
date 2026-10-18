#!/usr/bin/env python3
"""
xinfer-forge: Golden Attack Safety Gate
Enforces strict recall thresholds on historical Golden Attack vectors before exporting retrained models.
Updated to support Continual Learning Task Matrix (R_ij) and Federated Weight Evaluation.
"""

import os
import yaml
from dataclasses import dataclass
from typing import Optional, Tuple, List
import torch
import torch.nn as nn


@dataclass
class GoldenGateVerdict:
    passed: bool
    recall: float
    false_positive_rate: float
    threshold_required: float
    message: str
    accuracy: float = 0.0
    precision: float = 0.0
    f1_score: float = 0.0


class GoldenGateEvaluator:
    def __init__(self, config_path: str = "configs/model_hyperparams.yaml"):
        self.config_path = config_path
        self.min_recall_threshold = 0.999
        self.max_fpr_threshold = 0.005
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = yaml.safe_load(f)
                    safety_cfg = data.get("safety_gate", {})
                    self.min_recall_threshold = float(safety_cfg.get("min_recall_threshold", 0.999))
                    self.max_fpr_threshold = float(safety_cfg.get("max_false_positive_rate", 0.005))
                    print(f"[+] [GoldenGate] Loaded config: min_recall={self.min_recall_threshold} | max_fpr={self.max_fpr_threshold}")
            except Exception as e:
                print(f"[!] [GoldenGate Warning] Config read error: {e}. Using default thresholds.")

    def evaluate_model(
        self,
        model: nn.Module,
        eval_loader: torch.utils.data.DataLoader,
        custom_min_recall: Optional[float] = None
    ) -> GoldenGateVerdict:
        model.eval()
        required_recall = custom_min_recall if custom_min_recall is not None else self.min_recall_threshold

        tp, fp, tn, fn = 0, 0, 0, 0

        with torch.no_grad():
            for x_batch, y_batch in eval_loader:
                outputs = model(x_batch)
                if isinstance(outputs, tuple):
                    outputs = outputs[0]

                # Convert reconstruction error or logit scores to binary predictions
                scores = torch.sigmoid(outputs).squeeze()
                preds = (scores >= 0.5).long()
                targets = y_batch.long()

                tp += ((preds == 1) & (targets == 1)).sum().item()
                fp += ((preds == 1) & (targets == 0)).sum().item()
                tn += ((preds == 0) & (targets == 0)).sum().item()
                fn += ((preds == 0) & (targets == 1)).sum().item()

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        total_samples = tp + fp + tn + fn
        accuracy = (tp + tn) / total_samples if total_samples > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        passed = (recall >= required_recall) and (fpr <= self.max_fpr_threshold)

        msg = (
            f"PASS: Recall={recall:.4f} >= {required_recall:.4f} | FPR={fpr:.4f} <= {self.max_fpr_threshold:.4f} | F1={f1:.4f}"
            if passed else
            f"FAIL: Recall={recall:.4f} < {required_recall:.4f} or FPR={fpr:.4f} > {self.max_fpr_threshold:.4f}"
        )

        return GoldenGateVerdict(
            passed=passed,
            recall=recall,
            false_positive_rate=fpr,
            threshold_required=required_recall,
            message=msg,
            accuracy=accuracy,
            precision=precision,
            f1_score=f1
        )

    def evaluate_federated_weights(
        self,
        global_model: nn.Module,
        client_state_dicts: List[dict],
        eval_loader: torch.utils.data.DataLoader
    ) -> Tuple[GoldenGateVerdict, float]:
        """
        Evaluates global model weights aggregated from federated client updates.
        Returns the GoldenGateVerdict and Poisoning Impact Score.
        """
        verdict = self.evaluate_model(global_model, eval_loader)
        poison_impact = max(0.0, self.min_recall_threshold - verdict.recall)
        return verdict, poison_impact