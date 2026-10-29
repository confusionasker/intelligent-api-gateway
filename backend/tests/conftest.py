"""Pytest fixtures for PulseGate backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import hash_password
from app.models.user import User
from app.models.api_key import ApiKey
from app.ml.predict import get_model

# In-memory SQLite engine for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def preload_ml():
    """Ensure Isolation Forest model is available for tests."""
    get_model()


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    # Seed test user and API key
    test_user = User(
        username="tester",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    test_key = ApiKey(
        key="pg_live_test_api_key_12345",
        name="Test API Key",
        user_id=test_user.id,
        rate_limit=5,  # small limit for testing rate limiter trigger
        is_active=True,
    )
    session.add(test_key)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Override get_db with test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
