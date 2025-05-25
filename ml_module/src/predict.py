import torch
from train import LSTMModel, DEVICE
from io import BytesIO

from src.minio_connection import get_object
from src.logger import logger


def predict_price(features):
    # Преобразуем словарь признаков в список значений
    feature_values = list(features.values())  # Получаем все значения из словаря как список

    # Входные данные для предсказания
    input_dim = len(feature_values)  # Число признаков (features)

    # Загружаем модель с правильным количеством признаков
    lstm_model = LSTMModel(input_dim=input_dim)

    # Загружаем веса модели
    try:
        model_data = BytesIO(get_object("lstm_model.pt"))
        lstm_model.load_state_dict(torch.load(model_data, map_location=DEVICE))
    except RuntimeError as e:
        logger.debug(f"Error loading model: {e}")
        return None

    # Прогноз
    lstm_model.eval()
    with torch.no_grad():
        # Преобразуем список в тензор и добавляем фиктивную размерность для временного шага
        feature_tensor = torch.tensor([feature_values], dtype=torch.float32).unsqueeze(1)  # Добавляем 1 как seq_len

        # Прогнозируем
        prediction = lstm_model(feature_tensor)
    return prediction.item()
