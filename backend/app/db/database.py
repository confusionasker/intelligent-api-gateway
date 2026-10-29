"""Database engine and session management supporting both MySQL and SQLite."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Engine configuration depending on dialect
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {"echo": False}

if is_sqlite:
    # SQLite requires check_same_thread=False for FastAPI multithreaded requests
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # MySQL / PostgreSQL connection pooling and auto-reconnect configurations
    engine_kwargs.update({
        "pool_pre_ping": True,     # Tests connection health before issuing queries
        "pool_recycle": 3600,      # Recycle connections every hour to avoid MySQL timeout
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
