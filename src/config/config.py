import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('POSTGRES_DB')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_USER = os.getenv('POSTGRES_USER')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_HOST = os.getenv('POSTGRES_HOST')

TOKEN = os.getenv('TOKEN')
IS_ADMIN_ID = os.getenv('IS_ADMIN_ID')

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'