import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/karvion")

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
