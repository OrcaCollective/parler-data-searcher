from pymongo import MongoClient
import os

MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASS = os.environ.get("MONGO_PASS")
MONGO_ENDPOINT = os.environ.get("MONGO_ENDPOINT")
MONGO_PORT = os.environ.get("MONGO_PORT", "")

client = MongoClient(
    f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_ENDPOINT}", port=int(MONGO_PORT)
)

db = client.parler
