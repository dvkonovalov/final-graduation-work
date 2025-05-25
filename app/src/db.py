from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter

db = SQLAlchemy()

update_clicks = Counter('update_clicks', 'Number of Update button clicks')
site_entered = Counter('site_entered', 'Number of site enters')