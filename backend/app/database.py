from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()