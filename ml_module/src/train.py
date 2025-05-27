import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import xgboost as xgb
import lightgbm as lgb
import joblib
from io import BytesIO

from src.utils import prepare_data
from src.minio_connection import put_object
from src.logger import logger

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

SEQUENCE_LENGTH = 12
PREDICTION_HORIZON = 6


class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2):
        logger.debug(input_dim)
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        out = self.fc(out)
        return out


def train_models():
    features, targets = prepare_data(sequence_length=SEQUENCE_LENGTH, prediction_horizon=PREDICTION_HORIZON)

    split_idx = int(len(features) * 0.8)
    X_train, X_test = features[:split_idx], features[split_idx:]
    y_train, y_test = targets[:split_idx], targets[split_idx:]


    class CryptoDataset(Dataset):
        def __init__(self, X, y):
            self.X = torch.tensor(X, dtype=torch.float32)
            self.y = torch.tensor(y, dtype=torch.float32)

        def __len__(self):
            return len(self.X)

        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]

    train_dataset = CryptoDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    input_dim = X_train.shape[2]
    model = LSTMModel(input_dim=input_dim).to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 20
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(X_batch).squeeze()
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        logger.debug(f"LSTM Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(train_loader):.4f}")

    buffer = BytesIO()
    torch.save(model.state_dict(), buffer)
    put_object("lstm_model.pt", buffer)
    logger.debug("LSTM model saved.")


    X_train_flat = X_train.reshape(X_train.shape[0], -1)
    X_test_flat = X_test.reshape(X_test.shape[0], -1)

    xgb_model = xgb.XGBRegressor(n_estimators=100)
    xgb_model.fit(X_train_flat, y_train)
    
    buffer = BytesIO()
    joblib.dump(xgb_model, buffer)
    put_object("xgb_model.pkl", buffer)
    logger.debug("XGBoost model saved.")

    lgb_model = lgb.LGBMRegressor(n_estimators=100)
    lgb_model.fit(X_train_flat, y_train)
    
    buffer = BytesIO()
    joblib.dump(lgb_model, buffer)
    put_object("lgb_model.pkl", buffer)
    logger.debug("LightGBM model saved.")
