from pymongo import MongoClient

client = MongoClient("mongodb://username:password@mongodb:27017/")

db = client["training_data"]