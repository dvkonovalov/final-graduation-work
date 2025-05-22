from flask import Flask
import os

from src.db import db
from src.controllers.service_controller import init_session, proxy_request



def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@database:5432/{os.environ.get('POSTGRES_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.add_url_rule('/init_session', view_func=init_session, methods = ['POST'])
    app.add_url_rule('/proxy', view_func=proxy_request, methods = ['POST'])
    db.init_app(app)

    return app
