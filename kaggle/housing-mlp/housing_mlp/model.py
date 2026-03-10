"""Housing price MLP model."""

import torch
import torch.nn as nn


class HousingMLP(nn.Module):
    """Simple 3-layer MLP: Input(8) → 64 → 32 → 1."""

    def __init__(self, input_dim: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)
