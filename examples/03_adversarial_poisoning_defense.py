#!/usr/bin/env python3
"""
Example 2: Adversarial Poisoning Attack Defense
Demonstrates:
  1. An attacker injecting corrupted traffic to cause catastrophic forgetting.
  2. The model training on the poisoned dataset.
  3. The Regression Safety Gate intercepting the candidate weights.
  4. Automatically aborting deployment before the corrupted model can compromise Sentinel.
"""

import os
import sys
import torch
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forge.models.autoencoder import NetworkAnomalyAutoencoder
from forge.datasets.masked_flow_dataset import MaskedFlowDataset
from forge.trainers.mae_trainer import MAETrainer
from forge.safety.regression_gate import RegressionSafetyGate

def main():
    print("==================================================================")
    print("  xInfer Forge: Adversarial Poisoning Defense Test                ")
    print("==================================================================")

    input_dim = 32
    num_samples = 1500

    # 1. Attacker intentionally crafts poisoned training data
    # The attacker floods the facility with packets resembling their exploit (0.95 features)
    # attempting to force the Autoencoder to learn that exploit patterns are "normal".
    print("\n[Step 1] Simulating Adversarial Baseline Poisoning Attack...")
    poisoned_traffic = np.random.normal(loc=0.92, scale=0.03, size=(num_samples, input_dim)).astype(np.float32)
    poisoned_traffic = np.clip(poisoned_traffic, 0.0, 1.0)
    print("Attacker generated 1,500 poisoned flow vectors targeting port 502/SYN scans.")

    # 2. Train candidate model on poisoned traffic
    print("\n[Step 2] Candidate model trains on the poisoned dataset...")
    dataset = MaskedFlowDataset(poisoned_traffic, mask_ratio=0.20)
    model = NetworkAnomalyAutoencoder(input_dim=input_dim)
    
    config = {
        "training": {
            "device": "cpu",
            "epochs": 5,
            "batch_size": 64,
            "learning_rate": 0.005,
            "input_dim": input_dim
        },
        "safety": {
            "golden_benchmark_path": "configs/safety/golden_attacks.yaml",
            "min_golden_detection_rate": 1.00 # 100% required
        }
    }

    trainer = MAETrainer(model, config)
    poisoned_candidate_model = trainer.train(dataset)

    # 3. Safety Regression Gate intercepts the candidate model
    print("\n[Step 3] Running candidate weights through the Regression Safety Gate...")
    safety_gate = RegressionSafetyGate(config)
    is_safe = safety_gate.validate_adapted_model(poisoned_candidate_model)

    print("\n[Step 4] Enforcement Decision:")
    if not is_safe:
        print("------------------------------------------------------------------")
        print("  RESULT: DEPLOYMENT REJECTED BY SAFETY GATE                      ")
        print("  Reason: The candidate model adapted to exploit patterns,       ")
        print("          failing to detect known Golden Attacks.                 ")
        print("  Action: Weights purged. Active Sentinel appliance is UNHARMED.  ")
        print("------------------------------------------------------------------")
    else:
        print("FAIL: Model was incorrectly approved.")

    print("==================================================================")

if __name__ == "__main__":
    main()