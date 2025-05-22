from flask import Flask
import os

from src.db import db
from src.controllers.prediction_controller import index, update, get_all_data
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware



def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@database:5432/{os.environ.get('POSTGRES_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/update', 'update', update)
    app.add_url_rule('/get_all_data', view_func=get_all_data)
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    return app
