from src.job import job

from flask import Flask
import os


CONFIG = {}

CONFIG['collection_interval_hours'] = os.environ.get('collection_interval_hours')
CONFIG['collection_interval_minutes'] = os.environ.get('collection_interval_minutes')
CONFIG['fastapi_base_url'] = os.environ.get('fastapi_base_url')

CONFIG['historical_days'] = os.environ.get('historical_days')

CONFIG['reddit'] = {}
CONFIG['reddit']['client_id'] = os.environ.get('reddit_client_id')
CONFIG['reddit']['client_secret'] = os.environ.get('reddit_client_secret')
CONFIG['reddit']['username'] = os.environ.get('reddit_username')
CONFIG['reddit']['password'] = os.environ.get('reddit_password')
CONFIG['reddit']['user_agent'] = os.environ.get('reddit_user_agent')

def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule('/', 'start', job)
    return app
