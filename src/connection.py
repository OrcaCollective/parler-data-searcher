from pymongo import MongoClient
import os

MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASS = os.environ.get("MONGO_PASS")

client = MongoClient(
    f"mongodb://{MONGO_USER}:{MONGO_PASS}@parler-data.tech-bloc-sea.dev", port=27017
)

db = client.parler
