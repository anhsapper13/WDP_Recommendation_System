from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# Debug environment loading
print(f"🔍 DB_USERNAME from env: '{os.getenv('DB_USERNAME')}'")
print(f"🔍 DB_PASSWORD from env: '{os.getenv('DB_PASSWORD')}...'")
print(f"🔍 DB_HOST from env: '{os.getenv('DB_HOST')}'")
print(f"🔍 DB_DATABASE from env: '{os.getenv('DB_DATABASE')}'")

POSTGRES_USER = os.getenv("DB_USERNAME")  # ✅ Removed wrong default
POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
POSTGRES_SERVER = os.getenv("DB_HOST")
POSTGRES_PORT = os.getenv("DB_PORT", "5432")
POSTGRES_DB = os.getenv("DB_DATABASE")

# SQLAlchemy connection string
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def reflect_table(table_name):
    return Table(table_name, metadata, autoload_with=engine)