import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from core.config import MONGO_URI

client = MongoClient(MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())

def get_company_data():
    return client["company_data"]

def get_general_market_data():
    return client["general_market_data"]

def ping():
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
 