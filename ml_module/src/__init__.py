from flask import Flask
import os

from src.model_controller import train_endpoint, predict_endpoint
from src.db import db_sql as db

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@database:5432/{os.environ.get('POSTGRES_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.add_url_rule('/train', view_func=train_endpoint, methods=['GET'])
    app.add_url_rule('/predict', view_func=predict_endpoint, methods=['POST'])
    return app
