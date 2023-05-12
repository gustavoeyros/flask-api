from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_pass = os.getenv("DB_PASS")

client = MongoClient(
    'mongodb+srv://' + db_host + ':' + db_pass + '@cluster0.vw8ijjz.mongodb.net/')

db = client['signup']
