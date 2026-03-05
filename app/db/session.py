import os
import time
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def wait_for_db():
    print("⏳ Connecting to database...")
    for i in range(10):
        try:
            connection = engine.connect()
            connection.close()
            print("✅ Database is up!")
            return True
        except exc.OperationalError:
            print(f"Retrying database connection {i+1}/10...")
            time.sleep(2)
    return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()