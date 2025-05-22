from flask import Flask
from src.model_controller import train_endpoint, predict_endpoint

def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule('/train', view_func=train_endpoint, methods=['POST'])
    app.add_url_rule('/predict', view_func=predict_endpoint, methods=['POST'])
    return app
