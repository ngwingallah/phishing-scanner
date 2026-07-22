"""Database engine and session wiring.

Defaults to a local SQLite file for development; reads DATABASE_URL from
the environment in production (e.g. the Postgres URL Render injects).
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scanner.db")

# Render (and Heroku) hand out 'postgres://', but SQLAlchemy wants 'postgresql://'.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base every ORM model inherits from."""


def ensure_schema() -> None:
    """Add columns introduced after a database was first created.

    Keeps an existing scanner.db working instead of forcing users to delete
    it. A real project would use Alembic; this is the minimal equivalent.
    """
    inspector = inspect(engine)
    if not inspector.has_table("scans"):
        return
    columns = {col["name"] for col in inspector.get_columns("scans")}
    if "session_id" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE scans ADD COLUMN session_id VARCHAR(64)"))
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_scans_session_id ON scans (session_id)")
            )


def get_db():
    """FastAPI dependency that yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
