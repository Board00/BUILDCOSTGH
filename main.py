from pathlib import Path

from fastapi import Cookie, Depends, FastAPI, Request
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth import decode_token
from database import get_db
from error_handlers import register_error_handlers
from models import User
from routers import router

app = FastAPI(
    title="FastAPI Backend by Koni",
    description="""
    🚀 This backend was developed by Koni using FastAPI.
    It includes custom error handling and modular routing.
    """,
    version="0.1.0",
    contact={
        "name": "Koni",
        "email": "konikakraba0@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url=None  # disable default ReDoc so we can override it
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def user_dashboard_page(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    user = _get_page_user(access_token, db)
    if user is None or user.is_admin:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="dashboard.html")


def _get_page_user(access_token: str | None, db: Session):
    if not access_token:
        return None
    payload = decode_token(access_token)
    username = payload.get("sub") if payload else None
    return db.query(User).filter(User.username == username).first() if username else None


@app.get("/admin/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard_page(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    user = _get_page_user(access_token, db)
    if user is None or not user.is_admin:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="admin_dashboard.html")

# Custom ReDoc page


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="FastAPI Backend by Koni",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js",
        with_google_fonts=True
    )


register_error_handlers(app)
app.include_router(router)
