"""ORM model for a stored scan."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Scan(Base):
    """A single URL scan and its result, persisted to the database."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Anonymous per-browser identifier. Nullable so rows created before
    # sessions existed remain readable.
    session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    verdict: Mapped[str] = mapped_column(String(20), nullable=False)
    # List of {"name": ..., "reason": ...} for each triggered check.
    flags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
