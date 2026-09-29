"""
SQLAlchemy database session management.

This module creates:
1. The database engine (connection pool)
2. A session factory (SessionLocal)
3. A FastAPI dependency (get_db) for injecting sessions into route handlers

The session is closed after each request, even if an exception occurs,
thanks to the try/finally in get_db().
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create the SQLAlchemy engine with connection pooling
# pool_size: number of persistent connections
# max_overflow: additional connections allowed under load (beyond pool_size)
# pool_pre_ping: test connections before using them (handles stale connections)
# pool_recycle: recycle connections older than this many seconds
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug,  # Log all SQL in debug mode
)

# Session factory — each call to SessionLocal() creates a new session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage in a route:
        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    The session is always closed after the request, even on exceptions.
    Transactions are NOT committed automatically — the route handler or
    service must call db.commit() explicitly.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Verify the database is reachable.
    Used by the health check endpoint.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False
