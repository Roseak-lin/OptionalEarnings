from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_URI

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

try:
    print("Connecting to MongoDB...")
    print("MongoDB URI:", MONGO_URI)
    client._connect()
    
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
finally:
    client.close()