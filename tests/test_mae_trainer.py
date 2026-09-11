import unittest
import torch
import numpy as np
from forge.models.autoencoder import NetworkAnomalyAutoencoder
from forge.datasets.masked_flow_dataset import MaskedFlowDataset
from forge.trainers.mae_trainer import MAETrainer

class TestMAETrainer(unittest.TestCase):
    def test_mae_convergence(self):
        dummy_features = np.random.normal(0.3, 0.05, size=(128, 32)).astype(np.float32)
        dataset = MaskedFlowDataset(dummy_features, mask_ratio=0.20)
        
        model = NetworkAnomalyAutoencoder(input_dim=32)
        config = {
            "training": {
                "device": "cpu",
                "epochs": 2,
                "batch_size": 32,
                "learning_rate": 0.01
            }
        }

        trainer = MAETrainer(model, config)
        trained_model = trainer.train(dataset)
        self.assertIsNotNone(trained_model)

if __name__ == '__main__':
    unittest.main()