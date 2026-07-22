"""Data-access layer for scans (Repository pattern).

Keeps all database queries in one class so the API routes stay thin and
the persistence details can change without touching business logic.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .analyzer import ScanReport
from .models import Scan


class ScanRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, report: ScanReport) -> Scan:
        scan = Scan(
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
        stmt = select(Scan).order_by(Scan.created_at.desc()).limit(limit)
        return list(self._db.scalars(stmt))

    def get(self, scan_id: int) -> Scan | None:
        return self._db.get(Scan, scan_id)
