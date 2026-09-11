import torch
from torch.utils.data import Dataset
import numpy as np

class MaskedFlowDataset(Dataset):
    def __init__(self, feature_matrix, mask_ratio=0.20):
        self.data = torch.tensor(feature_matrix, dtype=torch.float32)
        self.mask_ratio = mask_ratio

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        original = self.data[idx].clone()
        masked = original.clone()

        # Randomly mask out elements for Self-Supervised Learning (Reconstruction task)
        num_features = original.shape[0]
        num_mask = int(num_features * self.mask_ratio)
        mask_indices = np.random.choice(num_features, num_mask, replace=False)

        masked[mask_indices] = 0.0 # Zero-masking for Autoencoder reconstruction
        return masked, original