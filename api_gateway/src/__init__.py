from flask import Flask
from src.db import db
from src.controllers.token_controller import read_public_sert

CONFIG = {
    'data_collector': read_public_sert('data_collector.pem'),
    'preparing_module': read_public_sert('preparing_module.pem'),
}



def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@database:5432/tokens'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    return app
