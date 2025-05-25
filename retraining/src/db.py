from prometheus_client import Gauge
from pymongo import MongoClient
import os
from flask_sqlalchemy import SQLAlchemy

Bitcoin_MSE = Gauge("bitcoin_MSE_metric", "Bitcoin MSE metric value")
Etherium_MSE = Gauge("etherium_MSE_metric", "Etherium MSE metric value")
Litecoin_MSE = Gauge("litecoin_MSE_metric", "Litecoin MSE metric value")

db_sql = SQLAlchemy()

client = MongoClient(f"mongodb://{os.environ.get('MONGO_INITDB_ROOT_USERNAME')}:{os.environ.get('MONGO_INITDB_ROOT_PASSWORD')}@mongodb/")

db = client["training_data"]