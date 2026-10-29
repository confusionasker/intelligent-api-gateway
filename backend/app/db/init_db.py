"""Database initialization script to automatically create database, tables, and seed default user.

Supports both MySQL and SQLite:
- For MySQL: Automatically executes `CREATE DATABASE IF NOT EXISTS` so no manual SQL setup is needed.
- For SQLite: Automatically creates the local `.db` file if not present.
- Creates all tables (users, api_keys, request_logs, anomalies) and seeds the default admin.
"""

from sqlalchemy import text, create_engine
from sqlalchemy.engine.url import make_url
from app.db.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.api_key import ApiKey
from app.core.security import hash_password
from app.core.config import settings
from app.utils.logger import logger


def ensure_database_exists():
    """If using MySQL/PostgreSQL, ensure the target database exists on the server before connecting."""
    try:
        url = make_url(settings.DATABASE_URL)
        backend = url.get_backend_name()

        if backend in ("mysql", "mariadb"):
            db_name = url.database
            if db_name:
                # Connect to MySQL server root without selecting a specific database
                server_url = url.set(database="")
                temp_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
                with temp_engine.connect() as conn:
                    logger.info(f"Checking if MySQL database '{db_name}' exists...")
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
                temp_engine.dispose()
                logger.info(f"MySQL database '{db_name}' is verified and ready.")
    except Exception as exc:
        logger.warning(f"Notice during automatic database creation check: {exc}")


def init_db():
    """Create all tables and seed default admin user if not existing."""
    # 1. Ensure MySQL database exists if using MySQL
    ensure_database_exists()

    # 2. Create tables
    logger.info("Initializing database schema and tables...")
    Base.metadata.create_all(bind=engine)

    # 3. Seed default admin user and default API key
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            logger.info("Creating default admin account (username: admin)...")
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            # Create a default API key for the admin
            default_key = ApiKey(
                key="pg_live_demo1234567890abcdef",
                name="Demo Default Key",
                user_id=admin.id,
                rate_limit=20,
                is_active=True,
            )
            db.add(default_key)
            db.commit()
            logger.info("Created default admin user and default API key: pg_live_demo1234567890abcdef")
        else:
            logger.info("Default admin user and schema already verified.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
