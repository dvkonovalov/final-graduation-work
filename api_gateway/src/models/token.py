from datetime import datetime, timedelta
import uuid

from src.db import db

class Token(db.Model):
    __tablename__ = "token"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub = db.Column(db.String(50), nullable=False)
    jti = db.Column(db.Float, unique=True, nullable=False, default= lambda: str(uuid.uuid4()))
    exp = db.Column(db.Float, nullable=False, default = lambda: datetime.now() + timedelta(hours = 1))
    iat = db.Column(db.DateTime(), nullable=False, default = datetime.now)