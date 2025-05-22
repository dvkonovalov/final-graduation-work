from src.train import train_models
from src.predict import predict_price

from flask import request, jsonify


def train_endpoint():
    train_models()
    return {"status": "success", "message": "Models trained and saved."}


def predict_endpoint():
    values = request.get_json()
    data = values.get('payload')
    
    prediction = predict_price(data.get('features'))
    return jsonify({"status": "success", "prediction": prediction})