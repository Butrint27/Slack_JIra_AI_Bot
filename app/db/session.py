import os
import time
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Added pool_pre_ping to handle dropped connections automatically
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def wait_for_db():
    print("⏳ Connecting to database...")
    for i in range(10):
        try:
            # Try to connect
            connection = engine.connect()
            connection.close()
            print("✅ Database is up and reachable!")
            return True
        except exc.OperationalError as e:
            print(f"Retrying database connection {i+1}/10... (Error: {e})")
            time.sleep(2)
    return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()