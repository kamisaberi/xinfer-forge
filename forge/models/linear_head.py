import torch
import torch.nn as nn

class AdaptableLinearHead(nn.Module):
    """Replaceable classification and regression head attached to frozen backbones."""
    def __init__(self, embedding_dim=128, num_classes=2):
        super(AdaptableLinearHead, self).__init__()
        self.head = nn.Sequential(
            nn.Linear(embedding_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, num_classes)
        )

    def forward(self, embeddings):
        logits = self.head(embeddings)
        return torch.softmax(logits, dim=-1)