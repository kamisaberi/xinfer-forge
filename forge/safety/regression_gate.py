import yaml
import torch
import numpy as np

class RegressionSafetyGate:
    def __init__(self, config):
        self.config = config
        benchmark_file = config["safety"]["golden_benchmark_path"]
        with open(benchmark_file, "r") as f:
            self.benchmark_data = yaml.safe_load(f)["golden_attacks"]

    def validate_adapted_model(self, adapted_model):
        print("[Safety Gate] Evaluating adapted model against non-negotiable Golden Attacks...")
        adapted_model.eval()

        passed_attacks = 0
        total_attacks = len(self.benchmark_data)

        with torch.no_grad():
            for attack in self.benchmark_data:
                feat_tensor = torch.tensor([attack["features"]], dtype=torch.float32)
                score = adapted_model(feat_tensor).item()

                expected_min = attack["expected_threat_score_min"]
                if score >= expected_min:
                    print(f"  PASS: {attack['id']} - Threat Score: {score:.3f} >= {expected_min}")
                    passed_attacks += 1
                else:
                    print(f"  FAIL: {attack['id']} - Threat Score: {score:.3f} < {expected_min} (FAILED TO DETECT)")

        detection_rate = passed_attacks / total_attacks
        min_required = self.config["safety"]["min_golden_detection_rate"]

        if detection_rate >= min_required:
            print(f"[Safety Gate] VALIDATION PASSED. Detection rate: {detection_rate * 100:.1f}%. Safe to deploy.")
            return True
        else:
            print(f"[Safety Gate CRITICAL] VALIDATION REJECTED! Model poisoned or suffering catastrophic forgetting.")
            return False