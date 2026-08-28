import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from codegate.database.base import Base

# We use an in-memory SQLite database for fast unit testing.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    # Create the database schema
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)
