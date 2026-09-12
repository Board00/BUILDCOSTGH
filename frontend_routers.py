from pathlib import Path
from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from auth import decode_token
from database import get_db
from models import User

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files (do this in main.py, not here)
# app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

@router.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="forgot_password.html")

@router.get("/reset-password", response_class=HTMLResponse, include_in_schema=False)
async def reset_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="reset_password.html")

@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
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

@router.get("/admin/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard_page(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    user = _get_page_user(access_token, db)
    if user is None or not user.is_admin:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="admin_dashboard.html")

ADMIN_DATA_PAGES = {
    "materials": {"title": "Materials", "singular": "material", "description": "Material prices and units"},
    "permits": {"title": "Permits", "singular": "permit", "description": "Permit fees and sources"},
    "land_prices": {"title": "Land prices", "singular": "land price", "description": "District land pricing"},
    "labor_rates": {"title": "Labour rates", "singular": "labour rate", "description": "Local trade rates"},
}

@router.get("/admin/data/{resource}", response_class=HTMLResponse, include_in_schema=False)
async def admin_data_page(
    resource: str,
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    user = _get_page_user(access_token, db)
    page = ADMIN_DATA_PAGES.get(resource)
    if page is None:
        return RedirectResponse("/admin/dashboard", status_code=303)
    if user is None or not user.is_admin:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin_data.html",
        context={"resource": resource, "page": page},
    )
