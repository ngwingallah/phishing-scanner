"""FastAPI application entry point.

Exposes three endpoints and auto-generates Swagger docs at /docs and
ReDoc at /redoc. The routes stay thin: they delegate scoring to
RiskAnalyzer and persistence to ScanRepository.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .analyzer import RiskAnalyzer
from .checks.rules import default_checks
from .database import Base, engine, ensure_schema, get_db
from .repository import ScanRepository
from .schemas import CheckOut, ScanOut, ScanRequest

# Create tables on startup (fine for a project of this size).
Base.metadata.create_all(bind=engine)
ensure_schema()

app = FastAPI(
    title="PhishGuard API",
    description="A heuristic phishing-URL risk scanner built for OOAD (SEN2241).",
    version="1.0.0",
)

# Allow the static frontend to call the API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = RiskAnalyzer()

# Requests without a session header fall into one shared bucket, so the API
# stays usable from Swagger or curl without extra setup.
ANONYMOUS_SESSION = "anonymous"


def current_session(
    x_session_id: Annotated[str | None, Header(alias="X-Session-Id")] = None,
) -> str:
    """Identify the caller by an anonymous, browser-generated session id.

    No account, no personal data — just an opaque string that scopes a
    visitor's history to their own browser.
    """
    return (x_session_id or "").strip()[:64] or ANONYMOUS_SESSION

# --- Frontend -----------------------------------------------------------
# Mounted under /static so it never shadows the API routes below.
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve the scanner page."""
    return FileResponse(STATIC_DIR / "index.html")


# --- API ----------------------------------------------------------------


@app.get("/health", summary="Health check", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/checks",
    response_model=list[CheckOut],
    summary="List every heuristic rule and its weight",
    tags=["System"],
)
def list_checks() -> list[CheckOut]:
    """The full rule catalogue, so clients can show how many rules exist."""
    return [CheckOut(name=c.name, weight=c.weight) for c in default_checks()]


@app.post("/scan", response_model=ScanOut, summary="Scan a URL for phishing risk", tags=["Scans"])
def scan_url(
    payload: ScanRequest,
    db: Session = Depends(get_db),
    session_id: str = Depends(current_session),
) -> ScanOut:
    report = analyzer.analyze(payload.url)
    return ScanRepository(db, session_id).save(report)


@app.get(
    "/scans",
    response_model=list[ScanOut],
    summary="List your recent scans",
    tags=["Scans"],
)
def list_scans(
    db: Session = Depends(get_db),
    session_id: str = Depends(current_session),
) -> list[ScanOut]:
    """Only returns scans belonging to the calling session."""
    return ScanRepository(db, session_id).list()


@app.get(
    "/scans/{scan_id}",
    response_model=ScanOut,
    summary="Get one of your scans by id",
    tags=["Scans"],
)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(current_session),
) -> ScanOut:
    scan = ScanRepository(db, session_id).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
