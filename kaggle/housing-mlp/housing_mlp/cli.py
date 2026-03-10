"""CLI: train, evaluate, and predict with the Housing MLP."""

import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from housing_mlp.data import FEATURE_NAMES, load_data
from housing_mlp.model import HousingMLP

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def _checkpoint_path() -> Path:
    return MODELS_DIR / "housing_mlp.pt"


def _save_checkpoint(model, scaler):
    MODELS_DIR.mkdir(exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "scaler_mean": scaler.mean_,
            "scaler_scale": scaler.scale_,
        },
        _checkpoint_path(),
    )


def _load_checkpoint():
    from sklearn.preprocessing import StandardScaler

    ckpt = torch.load(_checkpoint_path(), weights_only=False)
    model = HousingMLP()
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    scaler = StandardScaler()
    scaler.mean_ = ckpt["scaler_mean"]
    scaler.scale_ = ckpt["scaler_scale"]
    scaler.n_features_in_ = len(scaler.mean_)

    return model, scaler


def train(args):
    X_train, X_test, y_train, y_test, scaler = load_data()

    dataset = TensorDataset(
        torch.from_numpy(X_train), torch.from_numpy(y_train)
    )
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = HousingMLP()
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in loader:
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = criterion(pred, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(y_batch)
        epoch_loss /= len(dataset)
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:>4d}/{args.epochs}  MSE: {epoch_loss:.4f}")

    _save_checkpoint(model, scaler)
    print(f"\nCheckpoint saved to {_checkpoint_path()}")


def evaluate(args):
    model, scaler = _load_checkpoint()
    _, X_test, _, y_test, _ = load_data()
    # Re-scale test data with loaded scaler
    X_test_raw = _raw_test_data()
    X_test_scaled = scaler.transform(X_test_raw).astype(np.float32)
    y_test = _raw_test_targets()

    with torch.no_grad():
        preds = model(torch.from_numpy(X_test_scaled)).numpy()

    mse = float(np.mean((preds - y_test) ** 2))
    mae = float(np.mean(np.abs(preds - y_test)))
    ss_res = np.sum((y_test - preds) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2 = float(1 - ss_res / ss_tot)

    print(f"Model: {_checkpoint_path()}")
    print(f"Test samples: {len(y_test):,}")
    print(f"MSE:  {mse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R²:   {r2:.4f}")


def _raw_test_data():
    """Get raw (unscaled) test features."""
    from sklearn.datasets import fetch_california_housing
    from sklearn.model_selection import train_test_split

    data = fetch_california_housing()
    _, X_test, _, _ = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    return X_test


def _raw_test_targets():
    """Get test targets."""
    from sklearn.datasets import fetch_california_housing
    from sklearn.model_selection import train_test_split

    data = fetch_california_housing()
    _, _, _, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    return y_test.astype(np.float32)


def predict(args):
    model, scaler = _load_checkpoint()
    features = np.array(
        [[args.medinc, args.houseage, args.averooms, args.avebedrms,
          args.population, args.aveoccup, args.latitude, args.longitude]],
        dtype=np.float32,
    )
    features_scaled = scaler.transform(features).astype(np.float32)
    with torch.no_grad():
        pred = model(torch.from_numpy(features_scaled)).item()
    print(f"Predicted median house value: ${pred * 100_000:,.0f}  (raw: {pred:.4f})")


def main():
    parser = argparse.ArgumentParser(prog="housing-mlp")
    sub = parser.add_subparsers(dest="command")

    # train
    p_train = sub.add_parser("train", help="Train the model")
    p_train.add_argument("--epochs", type=int, default=100)
    p_train.add_argument("--lr", type=float, default=1e-3)
    p_train.add_argument("--batch-size", type=int, default=64)

    # evaluate
    sub.add_parser("evaluate", help="Evaluate on held-out test set")

    # predict
    p_pred = sub.add_parser("predict", help="Predict from feature values")
    for name in FEATURE_NAMES:
        p_pred.add_argument(f"--{name.lower()}", type=float, required=True)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    {"train": train, "evaluate": evaluate, "predict": predict}[args.command](args)


if __name__ == "__main__":
    main()
