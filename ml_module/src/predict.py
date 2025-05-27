import torch
from io import BytesIO

from src.train import LSTMModel, DEVICE
from src.minio_connection import get_object
from src.logger import logger
from src.utils import get_features


def predict_price(features):
    feature_values = list(features.values())

    input_dim = len(feature_values)

    lstm_model = LSTMModel(input_dim=input_dim)

    try:
        model_data = BytesIO(get_object("lstm_model.pt"))
        model_data.seek(0)
        lstm_model.load_state_dict(torch.load(model_data, map_location=DEVICE))
    except RuntimeError as e:
        logger.debug(f"Error loading model: {e}")
        return None

    lstm_model.eval()
    with torch.no_grad():
        feature_tensor = torch.tensor([feature], dtype=torch.float32).unsqueeze(1)
        prediction.append()= lstm_model(feature_tensor)

    return prediction
