# predict.py

import torch
import numpy as np
import joblib
import xgboost as xgb
import lightgbm as lgb
from train import LSTMModel, DEVICE


def predict_price(features):
    # Преобразуем словарь признаков в список значений
    feature_values = list(features.values())  # Получаем все значения из словаря как список

    # Входные данные для предсказания
    input_dim = len(feature_values)  # Число признаков (features)

    # Загружаем модель с правильным количеством признаков
    lstm_model = LSTMModel(input_dim=input_dim)

    # Загружаем веса модели
    try:
        lstm_model.load_state_dict(torch.load("models/lstm_model.pt", map_location=DEVICE))
    except RuntimeError as e:
        print(f"Error loading model: {e}")
        return None

    # Прогноз
    lstm_model.eval()
    with torch.no_grad():
        # Преобразуем список в тензор и добавляем фиктивную размерность для временного шага
        feature_tensor = torch.tensor([feature_values], dtype=torch.float32).unsqueeze(1)  # Добавляем 1 как seq_len

        # Прогнозируем
        prediction = lstm_model(feature_tensor)
    return prediction.item()
