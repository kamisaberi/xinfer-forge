import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

class MAETrainer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.device = torch.device(config["training"].get("device", "cpu"))
        self.model.to(self.device)

    def train(self, dataset):
        loader = DataLoader(
            dataset,
            batch_size=self.config["training"]["batch_size"],
            shuffle=True
        )

        criterion = nn.MSELoss()
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config["training"]["learning_rate"],
            weight_decay=1e-4
        )

        self.model.train()
        print(f"[Trainer] Starting Self-Supervised Masked Autoencoding on {len(dataset)} local samples...")

        for epoch in range(self.config["training"]["epochs"]):
            total_loss = 0.0
            for masked_x, original_x in loader:
                masked_x = masked_x.to(self.device)
                original_x = original_x.to(self.device)

                optimizer.zero_grad()
                reconstructed = self.model.reconstruct(masked_x)
                loss = criterion(reconstructed, original_x)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(loader)
            if (epoch + 1) % 2 == 0 or epoch == 0:
                print(f"[Trainer] Epoch [{epoch+1}/{self.config['training']['epochs']}] - Reconstruction Loss: {avg_loss:.6f}")

        print("[Trainer] Local self-supervised adaptation completed successfully.")
        return self.model