from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from error_handlers import register_error_handlers
from routers import router as backend_router
from frontend_routers import router as frontend_router
from migration_router import router as migration_router

app = FastAPI(
    title="FastAPI Backend by Koni",
    description="🚀 FastAPI project with backend + frontend separation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None
)

# Mount static files here
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(backend_router)
app.include_router(frontend_router)

register_error_handlers(app)

app.include_router(migration_router)
