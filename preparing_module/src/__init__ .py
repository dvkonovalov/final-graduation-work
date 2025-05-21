from flask import Flask
from src.main import process_data, upload_historical_data

def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule('/process_data', view_func=process_data)
    app.add_url_rule('/upload_historical_data', view_func=upload_historical_data)
    return app
