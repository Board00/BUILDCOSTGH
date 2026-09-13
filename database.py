import logging
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

load_dotenv()


def _resolve_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    return "sqlite:///./buildcost.db"


def _create_database_if_missing(database_url: str) -> None:
    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgresql", "postgresql+psycopg2", "postgresql+pg8000"}:
        return

    database_name = parsed.path.lstrip("/")
    if not database_name:
        return

    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return
    except Exception as exc:
        message = str(exc).lower()
        if "does not exist" not in message and "invalid catalog name" not in message and "database" not in message:
            logger.warning("Database connection check failed for %s: %s", database_name, exc)
            return

    try:
        import psycopg2
        from psycopg2 import sql

        admin_url = parsed._replace(path="/postgres").geturl()
        admin_parsed = urlparse(admin_url)
        connection = psycopg2.connect(
            dbname=admin_parsed.path.lstrip("/") or "postgres",
            user=admin_parsed.username,
            password=admin_parsed.password,
            host=admin_parsed.hostname,
            port=admin_parsed.port or 5432,
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {}" ).format(sql.Identifier(database_name)))
        logger.info("Created missing PostgreSQL database: %s", database_name)
    except Exception as create_exc:
        logger.warning(
            "Could not auto-create PostgreSQL database '%s'. Ensure the database exists or Postgres is running: %s",
            database_name,
            create_exc,
        )


DATABASE_URL = _resolve_database_url()
_create_database_if_missing(DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()