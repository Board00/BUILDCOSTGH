from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from error_handlers import register_error_handlers
from routers import router as backend_router
from frontend_routers import router as frontend_router
from migration_router import router as migration_router
from init_db import init_db   # 👈 import your init_db
from database import SessionLocal
from models import User
from auth import hash_password

app = FastAPI(
    title="FastAPI Backend by Koni",
    description="🚀 FastAPI project with backend + frontend separation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(backend_router)
app.include_router(frontend_router)
app.include_router(migration_router)

register_error_handlers(app)

@app.on_event("startup")
def on_startup():
    init_db()   # 👈 runs table creation at startup

# @app.on_event("startup")
# def seed_admin():
#     db = SessionLocal()
#     admin = db.query(User).filter(User.username == "BUILDCOSTGH").first()
#     if not admin:
#         new_admin = User(
#             username="BUILDCOSTGH",
#             hashed_password=hash_password("BUILDCOSTGH"),  # hashed password
#             is_admin=True,
#             is_active=True
#         )
#         db.add(new_admin)
#         db.commit()
#         print("✅ Admin user created in Render DB")
#     else:
#         print("ℹ️ Admin already exists")
#     db.close()