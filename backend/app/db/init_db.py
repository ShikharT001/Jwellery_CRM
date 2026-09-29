"""
Database initialization helpers.

These functions are used for:
- Verifying database connectivity
- Running initial setup (used in tests or first-time setup scripts)

NOTE: Actual schema creation is handled by Alembic migrations (alembic upgrade head).
Do NOT use SQLAlchemy's create_all() in production.
"""

from app.core.logging import get_logger
from app.db.session import SessionLocal, check_database_connection

logger = get_logger(__name__)


def verify_db_on_startup() -> None:
    """
    Verify the database connection on application startup.

    Called in the lifespan event handler in main.py.
    Logs a warning if the database is unreachable but does not crash
    the application (the health endpoint will reflect the degraded state).
    """
    if check_database_connection():
        logger.info("Database connection verified on startup")
    else:
        logger.error(
            "Database connection failed on startup. "
            "Check DATABASE_URL environment variable and Supabase connection settings."
        )
