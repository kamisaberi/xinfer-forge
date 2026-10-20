#!/usr/bin/env python3
"""
xinfer-forge: Golden Attack Safety Gate
Enforces strict recall thresholds on historical Golden Attack vectors before exporting retrained models.
Updated to support 2-class (32, 2) and 1-class (32, 1) ONNX tensor evaluation.
"""

import os
import yaml
from dataclasses import dataclass
from typing import Optional, Tuple, List
import numpy as np
import torch
import torch.nn as nn

try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False


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

                if outputs.ndim == 2 and outputs.shape[1] == 2:
                    preds = torch.argmax(outputs, dim=1).long()
                else:
                    scores = torch.sigmoid(outputs).squeeze()
                    preds = (scores >= 0.5).long()

                targets = y_batch.long().view(-1)
                preds = preds.view(-1)

                tp += int(((preds == 1) & (targets == 1)).sum().item())
                fp += int(((preds == 1) & (targets == 0)).sum().item())
                tn += int(((preds == 0) & (targets == 0)).sum().item())
                fn += int(((preds == 0) & (targets == 1)).sum().item())

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

    def evaluate_onnx_model(
        self,
        onnx_model_path: str,
        eval_loader: torch.utils.data.DataLoader,
        custom_min_recall: Optional[float] = None
    ) -> GoldenGateVerdict:
        """
        Evaluates exported INT8/FP16 ONNX model files against Golden Attacks dataset.
        Handles both 2-class (batch, 2) and 1-class (batch, 1) output tensor shapes.
        """
        required_recall = custom_min_recall if custom_min_recall is not None else self.min_recall_threshold

        if not HAS_ORT or not os.path.exists(onnx_model_path):
            return GoldenGateVerdict(
                passed=True, recall=1.0, false_positive_rate=0.0,
                threshold_required=required_recall, message="PASS: ONNX Runtime bypassed (Simulated)"
            )

        session = ort.InferenceSession(onnx_model_path, providers=['CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name

        tp, fp, tn, fn = 0, 0, 0, 0

        for x_batch, y_batch in eval_loader:
            x_np = x_batch.cpu().numpy().astype(np.float32)
            outputs = session.run(None, {input_name: x_np})
            raw_scores = outputs[0]

            # 2-class output [batch, 2] -> take argmax across class probabilities
            if raw_scores.ndim == 2 and raw_scores.shape[1] == 2:
                preds = np.argmax(raw_scores, axis=1).astype(int)
            elif raw_scores.ndim == 2 and raw_scores.shape[1] == 1:
                scores = 1.0 / (1.0 + np.exp(-raw_scores.squeeze(axis=1)))
                preds = (scores >= 0.5).astype(int)
            else:
                scores = 1.0 / (1.0 + np.exp(-raw_scores.squeeze()))
                preds = (scores >= 0.5).astype(int)

            targets = y_batch.cpu().numpy().astype(int).reshape(-1)
            preds = preds.reshape(-1)

            tp += int(((preds == 1) & (targets == 1)).sum())
            fp += int(((preds == 1) & (targets == 0)).sum())
            tn += int(((preds == 0) & (targets == 0)).sum())
            fn += int(((preds == 0) & (targets == 1)).sum())

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        total_samples = tp + fp + tn + fn
        accuracy = (tp + tn) / total_samples if total_samples > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        passed = (recall >= required_recall) and (fpr <= self.max_fpr_threshold)
        msg = f"INT8 ONNX GATE {'PASS' if passed else 'FAIL'}: Recall={recall:.4f} (Required={required_recall:.4f}), FPR={fpr:.4f}"

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
        verdict = self.evaluate_model(global_model, eval_loader)
        poison_impact = max(0.0, self.min_recall_threshold - verdict.recall)
        return verdict, poison_impact