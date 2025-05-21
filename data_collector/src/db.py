from pymongo import MongoClient

client = MongoClient("mongodb://username:password@mongodb/")

db = client["training_data"]