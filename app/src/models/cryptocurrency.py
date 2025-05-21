from src.db import db
from datetime import datetime

class Cryptocurrency(db.Model):
    __tablename__ = "cryptocurrency"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, nullable=False)
    created_date = db.Column(db.DateTime(), nullable=False, default = datetime.now)