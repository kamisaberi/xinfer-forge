#!/usr/bin/env python3
"""
xinfer-forge: Tabular Masked Autoencoder (MAE) Model
Self-supervised Transformer Autoencoder for continuous cyber-physical feature streams.
"""

import os
import yaml
from typing import Tuple, Optional
import torch
import torch.nn as nn


class TabularMAE(nn.Module):
    def __init__(
        self,
        input_dim: int = 32,
        embedding_dim: Optional[int] = None,
        num_heads: Optional[int] = None,
        num_layers: Optional[int] = None,
        mask_ratio: Optional[float] = None,
        config_path: str = "configs/model_hyperparams.yaml"
    ):
        super().__init__()
        self.input_dim = input_dim

        # Default hyperparameters
        cfg_emb_dim = 128
        cfg_heads = 4
        cfg_layers = 6
        cfg_mask_ratio = 0.3
        cfg_dropout = 0.1

        # Load from YAML if available
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = yaml.safe_load(f)
                    mae_cfg = cfg.get("model_architecture", {}).get("tabular_mae", {})
                    cfg_emb_dim = mae_cfg.get("embedding_dim", cfg_emb_dim)
                    cfg_heads = mae_cfg.get("num_heads", cfg_heads)
                    cfg_layers = mae_cfg.get("num_layers", cfg_layers)
                    cfg_mask_ratio = mae_cfg.get("mask_ratio", cfg_mask_ratio)
                    cfg_dropout = mae_cfg.get("dropout", cfg_dropout)
            except Exception as e:
                print(f"[!] [TabularMAE Warning] Config read error: {e}. Using defaults.")

        self.embedding_dim = embedding_dim or cfg_emb_dim
        self.num_heads = num_heads or cfg_heads
        self.num_layers = num_layers or cfg_layers
        self.mask_ratio = mask_ratio if mask_ratio is not None else cfg_mask_ratio

        # Linear projection of input features into token embedding space
        self.input_projection = nn.Linear(input_dim, self.embedding_dim)

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.embedding_dim,
            nhead=self.num_heads,
            dim_feedforward=self.embedding_dim * 4,
            dropout=cfg_dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=self.num_layers)

        # Reconstruction Head
        self.reconstruction_head = nn.Sequential(
            nn.Linear(self.embedding_dim, self.embedding_dim),
            nn.GELU(),
            nn.Linear(self.embedding_dim, input_dim)
        )

    def _random_masking(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size, dim = x.size()
        len_keep = int(dim * (1 - self.mask_ratio))

        noise = torch.rand(batch_size, dim, device=x.device)
        ids_shuffle = torch.argsort(noise, dim=1)
        ids_restore = torch.argsort(ids_shuffle, dim=1)

        mask = torch.ones([batch_size, dim], device=x.device)
        mask[:, :len_keep] = 0
        mask = torch.gather(mask, dim=1, index=ids_restore)

        x_masked = x * (1 - mask)
        return x_masked, mask

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        if self.training and self.mask_ratio > 0:
            x_masked, mask = self._random_masking(x)
        else:
            x_masked = x
            mask = torch.zeros_like(x)

        # Token embedding projection
        emb = self.input_projection(x_masked).unsqueeze(1) // [Batch, 1, Emb_Dim]
        latent = self.encoder(emb).squeeze(1)             // [Batch, Emb_Dim]
        reconstructed = self.reconstruction_head(latent)  // [Batch, Input_Dim]

        return reconstructed, mask