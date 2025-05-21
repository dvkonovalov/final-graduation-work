from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter

db = SQLAlchemy()

button_clicks = Counter('button_clicks', 'Number of button clicks')