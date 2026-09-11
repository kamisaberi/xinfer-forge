#!/usr/bin/env python3
import os
import yaml
import sys

from forge.collector.sqlite_collector import SQLiteCollector
from forge.datasets.masked_flow_dataset import MaskedFlowDataset
from forge.models.autoencoder import NetworkAnomalyAutoencoder
from forge.trainers.mae_trainer import MAETrainer
from forge.safety.regression_gate import RegressionSafetyGate
from forge.exporter.onnx_exporter import ONNXExporter
from forge.dispatcher.xinfer_client import xInferDispatcher

def run_adaptation_cycle(config_path="configs/forge_config.yaml"):
    print("==========================================================")
    print("  xInfer Forge: Continuous Adaptation & SSL Engine        ")
    print("==========================================================")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # 1. Collect ambient flow features
    collector = SQLiteCollector(config["appliance"]["db_path"], input_dim=config["training"]["input_dim"])
    features = collector.collect_unlabeled_features(min_samples=config["training"]["min_samples_to_train"])

    # 2. Prepare Self-Supervised Masked Dataset
    dataset = MaskedFlowDataset(features, mask_ratio=config["training"]["mask_ratio"])

    # 3. Initialize & Adapt Model
    model = NetworkAnomalyAutoencoder(input_dim=config["training"]["input_dim"])
    trainer = MAETrainer(model, config)
    adapted_model = trainer.train(dataset)

    # 4. Safety & Anti-Poisoning Regression Gate
    safety_gate = RegressionSafetyGate(config)
    is_safe = safety_gate.validate_adapted_model(adapted_model)

    if not is_safe:
        print("[Forge CRITICAL] Model adaptation rejected by safety gate. Retaining previous model.")
        sys.exit(1)

    # 5. Export to ONNX
    exporter = ONNXExporter(config)
    onnx_path = exporter.export(adapted_model)

    # 6. Dispatch Hot-Reload to Blackbox Sentinel (xinfer)
    dispatcher = xInferDispatcher(config["appliance"]["sentinel_api_url"])
    dispatcher.trigger_hot_reload(onnx_path)

    print("==========================================================")
    print("  Adaptation Cycle Complete: Model Deployed with Zero Lag ")
    print("==========================================================")

if __name__ == "__main__":
    run_adaptation_cycle()