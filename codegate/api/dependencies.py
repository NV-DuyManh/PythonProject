from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from codegate.database.session import SessionLocal
from codegate.database.models import User

def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user() -> User:
    """
    AUTH STATUS: FOUNDATION ONLY
    This is a stub for the future authentication system (e.g. GitHub OAuth).
    Returns a dummy user for now.
    """
    return User(
        id=1,
        provider="GITHUB",
        provider_user_id="dummy",
        username="admin_stub"
    )
