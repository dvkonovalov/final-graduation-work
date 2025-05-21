from src.job import job

from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule('/job', view_func=job)
    return app
