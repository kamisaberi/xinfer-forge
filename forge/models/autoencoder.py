import torch
import torch.nn as nn

class NetworkAnomalyAutoencoder(nn.Module):
    def __init__(self, input_dim=32):
        super(NetworkAnomalyAutoencoder, self).__init__()
        # Compression Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 4), # Latent bottleneck
            nn.ReLU()
        )
        # Expansion Decoder
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        # Anomaly score based on reconstruction error
        mse = torch.mean((x - decoded) ** 2, dim=1, keepdim=True)
        score = torch.clamp(mse * 10.0, 0.0, 1.0)
        return score

    def reconstruct(self, x):
        return self.decoder(self.encoder(x))