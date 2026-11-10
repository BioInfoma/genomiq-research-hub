"""
Database engine and session management for GenomIQ Research Hub.
"""
import shutil
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL, DB_FILE, DATA_DIR
from database.models import Base

# Engine configuration
# SQLite requires check_same_thread=False when used across Streamlit worker threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine))


def init_db():
    """Initializes database schema and ensures all tables exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


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
    if not DB_FILE.exists():
        return None
    if backup_dir is None:
        backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"genomiq_backup_{timestamp}.db"
    shutil.copy2(DB_FILE, backup_path)
    return str(backup_path)
