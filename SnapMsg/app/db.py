import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    db_url = os.getenv("DB_URI")
    client = MongoClient(db_url, server_api=ServerApi('1'), tlsCAFile=certifi.where())
else:
    db_url = "mongodb://mongoadmin:secret@localhost:27017"
    client = MongoClient(db_url, server_api=ServerApi('1'))

db = client['twitsnaps']



def get_db():
    """
    Provides a MongoDB database instance to be used in routes.
    """
    return db
