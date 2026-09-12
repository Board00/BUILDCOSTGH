from fastapi import APIRouter
import subprocess

router = APIRouter()

@router.get("/run-migrations")
def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"])
    return {"status": "migrations applied"}
