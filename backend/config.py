import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME")
POLYGON_IO_KEY = os.getenv("POLYGON_IO_KEY")