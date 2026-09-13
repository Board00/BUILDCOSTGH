import logging
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from auth import hash_password
from database import SessionLocal
from error_handlers import register_error_handlers
from frontend_routers import router as frontend_router
from init_db import init_db
from models import User
from routers import router as backend_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FastAPI Backend by Koni",
    description="🚀 FastAPI project with backend + frontend separation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(backend_router)
app.include_router(frontend_router)
# app.include_router(migration_router)

register_error_handlers(app)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
        from database import DATABASE_URL

        parsed_database_url = urlparse(DATABASE_URL)
        database_target = parsed_database_url.hostname or parsed_database_url.scheme
        logger.info("Database initialized successfully using host: %s", database_target)
    except Exception:
        logger.exception(
            "Database initialization failed during startup. "
            "Check that PostgreSQL is running and DATABASE_URL points to an existing database."
        )

