import torch
from torch.utils.data import Dataset
import numpy as np

class ContrastiveFlowDataset(Dataset):
    """Generates positive augmented pairs and negative contrastive samples for SSL."""
    def __init__(self, feature_matrix, noise_std=0.03):
        self.data = torch.tensor(feature_matrix, dtype=torch.float32)
        self.noise_std = noise_std

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        x = self.data[idx]
        
        # Positive augmentation 1: Gaussian noise perturbation
        noise_1 = torch.randn_like(x) * self.noise_std
        x_aug1 = torch.clamp(x + noise_1, 0.0, 1.0)

        # Positive augmentation 2: Random element dropout
        noise_2 = torch.randn_like(x) * self.noise_std
        mask = torch.rand_like(x) > 0.10
        x_aug2 = torch.clamp(x + noise_2, 0.0, 1.0) * mask.float()

        return x_aug1, x_aug2