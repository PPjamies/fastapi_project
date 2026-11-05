import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Uses SQLite in memory by default; set TEST_DATABASE_URL to test against Postgres
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite://")

if TEST_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
else:
    engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture
def new_profile():
    return {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "date_of_birth": "1990-12-10",
        "email": "Ada@Example.com",
        "phone": "+442071234567",
        "city": "London",
        "country": "GB",
    }
