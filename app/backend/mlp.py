"""Shared MLP architecture — must match fsbo_final_model.py exactly."""
from __future__ import annotations
import torch
import torch.nn as nn


class MLP(nn.Module):
    def __init__(self, input_dim: int, n_classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
