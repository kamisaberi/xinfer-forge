import torch
import torch.nn as nn
import math

class LoRALinear(nn.Module):
    """Low-Rank Adaptation (LoRA) layer for parameter-efficient fine-tuning."""
    def __init__(self, in_features, out_features, rank=4, alpha=8.0):
        super(LoRALinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.scaling = alpha / rank

        # Frozen base weight matrix
        self.base_weight = nn.Parameter(torch.zeros(out_features, in_features), requires_grad=False)
        
        # Trainable low-rank decomposition matrices
        self.lora_A = nn.Parameter(torch.zeros(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)

    def forward(self, x):
        base_out = nn.functional.linear(x, self.base_weight)
        lora_out = (x @ self.lora_A.T @ self.lora_B.T) * self.scaling
        return base_out + lora_out

    def merge_weights(self):
        """Folds the LoRA parameters into the base weight matrix for clean ONNX export."""
        with torch.no_grad():
            self.base_weight.data += (self.lora_B @ self.lora_A) * self.scaling