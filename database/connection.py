"""
Database engine and session management for GenomIQ Research Hub.
Features:
- Resilient multi-platform path resolution (Windows, Linux, Streamlit Cloud)
- Directory auto-creation and fallback to user home directory if needed
- Graceful cloud database connection with automatic fallback to local SQLite
- Thread-safe session management
"""
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL, DB_FILE, DATA_DIR
from database.models import Base

logger = logging.getLogger(__name__)


def ensure_data_directory() -> Path:
    """Ensures data directory exists and is writable, falling back to home dir if needed."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Test write permissions
        test_file = DATA_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
        return DATA_DIR
    except Exception as e:
        logger.warning(f"Default DATA_DIR '{DATA_DIR}' not writable: {e}. Falling back to user home directory.")
        fallback_dir = Path.home() / ".genomiq" / "data"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir


# Ensure directory is ready
active_data_dir = ensure_data_directory()
active_db_file = active_data_dir / "genomiq.db"

# Determine active database URL
active_db_url = DATABASE_URL
if "sqlite" in active_db_url and not os.getenv("DATABASE_URL"):
    active_db_url = f"sqlite:///{active_db_file.as_posix()}"


def build_engine(db_url: str):
    is_sqlite = "sqlite" in db_url
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(
        db_url,
        connect_args=connect_args,
        echo=False,
        pool_pre_ping=True,
    )


engine = build_engine(active_db_url)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine))


def init_db():
    """Initializes database schema and ensures all tables exist with resilient error recovery."""
    global engine, SessionLocal, active_db_url

    try:
        active_data_dir.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=engine)
    except Exception as primary_exc:
        logger.error(f"Primary database initialization failed ({primary_exc}). Attempting fallback to local SQLite...")
        try:
            # Fallback to isolated user home directory SQLite
            fallback_dir = Path.home() / ".genomiq" / "data"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            fallback_file = fallback_dir / "genomiq.db"
            fallback_url = f"sqlite:///{fallback_file.as_posix()}"

            engine = build_engine(fallback_url)
            SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine))
            Base.metadata.create_all(bind=engine)
            active_db_url = fallback_url
            logger.info(f"Fallback to SQLite at '{fallback_file}' succeeded.")
        except Exception as fallback_exc:
            # Re-raise with informative unredacted details
            raise RuntimeError(
                f"Failed to initialize database on primary ({primary_exc}) and fallback ({fallback_exc}). "
                f"Active URL: {active_db_url}"
            ) from primary_exc


@contextmanager
def get_db():
    """Context manager for thread-safe database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def backup_database(backup_dir=None):
    """Creates a timestamped backup copy of SQLite database for disaster recovery."""
    if not active_db_file.exists():
        return None
    if backup_dir is None:
        backup_dir = active_data_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"genomiq_backup_{timestamp}.db"
    shutil.copy2(active_db_file, backup_path)
    return str(backup_path)
