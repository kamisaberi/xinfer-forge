from abc import ABC, abstractmethod
import torch

class BaseTrainer(ABC):
    """Abstract training lifecycle managing device allocation and early stopping."""
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.device = torch.device(config["training"].get("device", "cpu"))
        self.model.to(self.device)

    @abstractmethod
    def train(self, dataset):
        pass

    def check_early_stopping(self, val_losses, patience=3):
        if len(val_losses) < patience:
            return False
        recent = val_losses[-patience:]
        return all(recent[i] <= recent[i+1] for i in range(len(recent)-1))