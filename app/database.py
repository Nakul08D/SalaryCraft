from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv()
                
# DATABASE_URL = "sqlite:///C:/Users/dell/Desktop/SalaryCraft/app.database"
DATABASE_URL = "postgresql://postgres:password@localhost:5432/SalaryCraftDatabase"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/SalaryCraftDatabase")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()