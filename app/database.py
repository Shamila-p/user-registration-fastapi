import psycopg2
import pymongo
from decouple import config

# PostgreSQL database configuration
db_name = config('DB_NAME')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST')
db_port = config('DB_PORT')

pg_conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# MongoDB configuration
mongo_client = pymongo.MongoClient(config('MONGO_URL'))
mongo_db = mongo_client[config('MONGO_DB_NAME')]
mongo_collection = mongo_db['Profile']
