import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from forge.trainers.base_trainer import BaseTrainer

class InfoNCELoss(nn.Module):
    def __init__(self, temperature=0.07):
        super(InfoNCELoss, self).__init__()
        self.temperature = temperature
        self.cosine = nn.CosineSimilarity(dim=-1)

    def forward(self, z_i, z_j):
        batch_size = z_i.size(0)
        representations = torch.cat([z_i, z_j], dim=0)
        similarity_matrix = self.cosine(representations.unsqueeze(1), representations.unsqueeze(0)) / self.temperature

        # Create positive pair index masks
        sim_ij = torch.diag(similarity_matrix, batch_size)
        sim_ji = torch.diag(similarity_matrix, -batch_size)
        positives = torch.cat([sim_ij, sim_ji], dim=0)

        diag_mask = ~torch.eye(2 * batch_size, 2 * batch_size, dtype=torch.bool, device=z_i.device)
        negatives = similarity_matrix[diag_mask].view(2 * batch_size, -1)

        logits = torch.cat([positives.unsqueeze(1), negatives], dim=1)
        labels = torch.zeros(2 * batch_size, dtype=torch.long, device=z_i.device)

        return nn.functional.cross_entropy(logits, labels)

class ContrastiveTrainer(BaseTrainer):
    def train(self, dataset):
        loader = DataLoader(dataset, batch_size=self.config["training"].get("batch_size", 32), shuffle=True)
        criterion = InfoNCELoss(temperature=0.07)
        optimizer = optim.AdamW(self.model.parameters(), lr=self.config["training"].get("learning_rate", 0.001))

        self.model.train()
        print(f"[ContrastiveTrainer] Running InfoNCE self-supervised representation training on {len(dataset)} samples...")

        for epoch in range(self.config["training"].get("epochs", 5)):
            total_loss = 0.0
            for x_i, x_j in loader:
                x_i, x_j = x_i.to(self.device), x_j.to(self.device)
                optimizer.zero_grad()
                z_i = self.model(x_i)
                z_j = self.model(x_j)

                loss = criterion(z_i, z_j)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            print(f"[ContrastiveTrainer] Epoch [{epoch+1}] - InfoNCE Loss: {total_loss / len(loader):.5f}")

        return self.model