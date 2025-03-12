import os
import time
import pymysql

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Load environment variables
load_dotenv()

# Read from .env
HOST = "localhost"
MYSQL_USER = os.getenv("MYSQL_USER", "user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "medium_db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3307))

# Database URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)

# Create a scoped session for thread safety
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

def wait_for_mysql():
    """Wait for MySQL to be available before proceeding."""
    while True:
        try:
            conn = pymysql.connect(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE, port=MYSQL_PORT)
            conn.close()
            print("✅ MySQL is ready!")
            break
        except pymysql.err.OperationalError as e:
            print(f"⏳ Waiting for MySQL to start... Error: {e}")
            time.sleep(2)