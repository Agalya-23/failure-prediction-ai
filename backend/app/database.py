
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

database_url = os.environ["DATABASE_URL"]

database_url = database_url.replace(
    "postgresql+psycopg://",
    "postgresql+psycopg2://"
)

database_url = database_url.replace(
    "postgresql://",
    "postgresql+psycopg2://"
)

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
