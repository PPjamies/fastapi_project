import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, MappedAsDataclass, DeclarativeBase

DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql+psycopg://app_user:app_pw@localhost:5432/app_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
