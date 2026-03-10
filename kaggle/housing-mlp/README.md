# Housing Price MLP

PyTorch MLP that predicts California housing prices using sklearn's California Housing dataset (20,640 samples, 8 features → median house value).

## Architecture

```
Input(8) → Linear(64) → ReLU → Linear(32) → ReLU → Linear(1)
```

- Loss: MSELoss
- Optimizer: Adam (lr=1e-3)
- Preprocessing: StandardScaler on features (saved with checkpoint)

## Usage

```bash
# Install
uv sync

# Train (saves checkpoint to models/)
uv run housing-mlp train --epochs 100 --lr 0.001 --batch-size 64

# Evaluate on held-out test set
uv run housing-mlp evaluate

# Predict a single sample
uv run housing-mlp predict \
  --medinc 8.3 --houseage 41 --averooms 6.9 --avebedrms 1.02 \
  --population 322 --aveoccup 2.55 --latitude 37.88 --longitude -122.23
```

## Features

| Feature | Description |
|---------|-------------|
| MedInc | Median income in block group |
| HouseAge | Median house age |
| AveRooms | Avg rooms per household |
| AveBedrms | Avg bedrooms per household |
| Population | Block group population |
| AveOccup | Avg household members |
| Latitude | Block group latitude |
| Longitude | Block group longitude |

## Tests

```bash
uv run pytest tests/ -v
```
