"""Data-access layer for scans (Repository pattern).

Keeps all database queries in one class so the API routes stay thin and
the persistence details can change without touching business logic.

Every query is scoped to a session id, so one visitor can never read
another visitor's scan history. That rule lives here and nowhere else —
the routes and the analyzer know nothing about it.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .analyzer import ScanReport
from .models import Scan


class ScanRepository:
    def __init__(self, db: Session, session_id: str) -> None:
        self._db = db
        self._session_id = session_id

    def save(self, report: ScanReport) -> Scan:
        scan = Scan(
            session_id=self._session_id,
            url=report.url,
            score=report.score,
            verdict=report.verdict,
            flags=[
                {"name": o.name, "reason": o.reason, "points": o.points}
                for o in report.triggered
            ],
        )
        self._db.add(scan)
        self._db.commit()
        self._db.refresh(scan)
        return scan

    def list(self, limit: int = 50) -> list[Scan]:
        stmt = (
            select(Scan)
            .where(Scan.session_id == self._session_id)
            .order_by(Scan.created_at.desc())
            .limit(limit)
        )
        return list(self._db.scalars(stmt))

    def get(self, scan_id: int) -> Scan | None:
        """Fetch one scan, but only if it belongs to this session."""
        stmt = select(Scan).where(
            Scan.id == scan_id,
            Scan.session_id == self._session_id,
        )
        return self._db.scalars(stmt).first()
