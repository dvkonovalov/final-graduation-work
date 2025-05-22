from pymongo import MongoClient
import os
client = MongoClient(f"mongodb://{os.environ.get('MONGO_INITDB_ROOT_USERNAME')}:{os.environ.get('MONGO_INITDB_ROOT_PASSWORD')}@mongodb/")

db = client["training_data"]