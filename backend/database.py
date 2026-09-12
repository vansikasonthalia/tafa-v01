"""
Database engine and session factory for TAFA.
Uses SQLite stored at backend/data/tafa.db.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database file lives in backend/data/
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'tafa.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + threads
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from . import models  # noqa: F401 — import so SQLAlchemy sees the models
    Base.metadata.create_all(bind=engine)
