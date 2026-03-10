"""Smoke tests for data loading, model forward pass, and prediction."""

import numpy as np
import torch

from housing_mlp.data import load_data
from housing_mlp.model import HousingMLP


def test_data_loading():
    X_train, X_test, y_train, y_test, scaler = load_data()
    # Correct shapes
    assert X_train.shape[1] == 8
    assert X_test.shape[1] == 8
    assert len(y_train) == X_train.shape[0]
    assert len(y_test) == X_test.shape[0]
    # No NaNs
    assert not np.isnan(X_train).any()
    assert not np.isnan(y_train).any()
    # Scaler is fitted (mean ≈ 0, std ≈ 1 on train set)
    assert np.allclose(X_train.mean(axis=0), 0, atol=0.1)
    assert np.allclose(X_train.std(axis=0), 1, atol=0.1)


def test_model_forward():
    model = HousingMLP()
    x = torch.randn(16, 8)
    out = model(x)
    assert out.shape == (16,)


def test_training_reduces_loss():
    X_train, _, y_train, _, _ = load_data()
    model = HousingMLP()
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Use a small subset
    X = torch.from_numpy(X_train[:256])
    y = torch.from_numpy(y_train[:256])

    model.train()
    loss_first = criterion(model(X), y).item()

    for _ in range(50):
        optimizer.zero_grad()
        loss = criterion(model(X), y)
        loss.backward()
        optimizer.step()

    loss_last = criterion(model(X), y).item()
    assert loss_last < loss_first, f"Loss didn't decrease: {loss_first} → {loss_last}"


def test_predict_output():
    model = HousingMLP()
    x = torch.tensor([[0.0] * 8])
    with torch.no_grad():
        pred = model(x).item()
    assert isinstance(pred, float)
