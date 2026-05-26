"""BiLSTM_CNN architecture — exact match to Section 7 of fsbo_final_model.py."""
from __future__ import annotations
import torch
import torch.nn as nn


class BiLSTM_CNN(nn.Module):
    """Convolutional BiLSTM used in the Section 7 'ultimate' ensemble.

    Forward pass:
        Linear expand → Conv1d → ReLU → MaxPool → BiLSTM (2 layers) → MaxPool over time → FC
    """
    def __init__(self, input_dim: int, n_classes: int) -> None:
        super().__init__()
        self.feature_expand = nn.Linear(input_dim, 32)
        self.conv  = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
        self.relu  = nn.ReLU()
        self.pool  = nn.MaxPool1d(kernel_size=2)
        self.lstm  = nn.LSTM(
            input_size=16, hidden_size=64, num_layers=2,
            batch_first=True, bidirectional=True, dropout=0.3,
        )
        self.fc = nn.Sequential(
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.feature_expand(x)       # (B, 32)
        x = x.unsqueeze(1)               # (B, 1, 32)
        x = self.pool(self.relu(self.conv(x)))  # (B, 16, 16)
        x = x.transpose(1, 2)            # (B, 16, 16)
        lstm_out, _ = self.lstm(x)       # (B, 16, 128)
        x = torch.max(lstm_out, dim=1)[0]  # (B, 128)
        return self.fc(x)                # (B, n_classes)
