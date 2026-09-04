import os
from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import (
    create_token,
    decode_token,
    get_current_admin,
    get_current_user,
    hash_password,
    verify_password,
)
from confidence import confidence_score
from cost_engine import itemized_estimate
from database import get_db
from exceptions import DatabaseError
from feedback import submit_feedback
from models import Estimate, LandPrice, LaborRate, Material, Permit, User
from pdf_export import generate_pdf
from retrieval import get_land_prices, get_labor_rates, get_material_prices, get_permits
from schemas import (
    AdminCreate,
    EstimateRequest,
    FeedbackCreate,
    LandPriceCreate,
    LaborRateCreate,
    MaterialCreate,
    PermitCreate,
    RegisterRequest,
)


router = APIRouter()


@router.get("/", tags=["Authentication"])
async def root():
    return {"message": "Welcome to Land Price API"}


@router.post("/admin/register", include_in_schema=False, tags=["Authentication"])
async def register_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    bootstrap_token: str | None = Header(default=None, alias="X-Bootstrap-Token"),
):
    configured_token = os.getenv("ADMIN_BOOTSTRAP_TOKEN")
    if not configured_token or bootstrap_token != configured_token:
        raise HTTPException(status_code=404, detail="Not found")
    existing_user = db.query(User).filter(User.username == admin.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_admin = User(
        username=admin.username,
        hashed_password=hash_password(admin.password),
        is_admin=True,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin registered successfully", "admin_id": new_admin.id}


@router.post("/register", tags=["Authentication"])
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(username=data.username, hashed_password=hash_password(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": user.username}, expires_delta=timedelta(minutes=30))
    refresh_token = create_token(
        {"sub": user.username}, expires_delta=timedelta(days=7), token_type="refresh"
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", tags=["Authentication"])
async def refresh(refresh_token: str, user: User = Depends(get_current_user)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh" or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Ensure the refresh token belongs to the current user
    if payload.get("sub") != user.username:
        raise HTTPException(status_code=403, detail="Token does not match user")

    new_access_token = create_token(
        {"sub": payload["sub"], "type": "access"},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": new_access_token}


@router.post("/logout", tags=["Authentication"])
async def logout(user: User = Depends(get_current_user)):
    return {"user": user, "message": "Logout successful. Please discard your tokens."}


@router.post("/land_prices", tags=["ADMIN'S ONLY"])
async def create_land_price(
    land: LandPriceCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    new_land = LandPrice(**land.model_dump())
    db.add(new_land)
    db.commit()
    db.refresh(new_land)
    return {"message": "Land price added successfully", "land_price": new_land.id}


@router.post("/permits", tags=["ADMIN'S ONLY"])
async def create_permit(
    permit: PermitCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    new_permit = Permit(**permit.model_dump())
    db.add(new_permit)
    db.commit()
    db.refresh(new_permit)
    return {"message": "Permit added successfully", "permit": new_permit.id}


@router.post("/materials", tags=["ADMIN'S ONLY"])
async def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    new_material = Material(**material.model_dump())
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return {"message": "Material added successfully", "material_id": new_material.id}


@router.post("/labor_rates", tags=["ADMIN'S ONLY"])
async def create_labor_rate(
    labor: LaborRateCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    new_labor = LaborRate(**labor.model_dump())
    db.add(new_labor)
    db.commit()
    db.refresh(new_labor)
    return {"message": "Labor rate added successfully", "labor_rate": new_labor.id}


@router.post("/estimate")
async def generate_estimate(
    request: EstimateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    region = request.region.value
    district = request.district.value
    sources = {
        "materials": get_material_prices(region, db, district),
        "labor": get_labor_rates(region, db, district),
        "land": get_land_prices(district, db, region),
        "permits": get_permits(region, db, district),
    }
    itemized = itemized_estimate(request.model_dump(), db, sources)
    confidence = confidence_score([source for category in sources.values() for source in category])

    try:
        estimate = Estimate(
            user_input=request.model_dump(),
            user_id=user.id,
            itemized=itemized,
            total=itemized["total"],
            confidence=confidence["level"],
        )
        db.add(estimate)
        db.commit()
        db.refresh(estimate)
    except Exception as error:
        db.rollback()
        raise DatabaseError(f"Failed to save estimate: {error}") from error

    return {
        "user": user.username,
        "estimate_id": estimate.id,
        "itemized": itemized,
        "sources": sources,
        "confidence": confidence,
        "disclaimer": "Planning estimate, not certified QS quote",
    }


@router.post("/export")
async def export_pdf(
    params: EstimateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    region = params.region.value
    district = params.district.value
    sources = {
        "materials": get_material_prices(region, db, district),
        "labor": get_labor_rates(region, db, district),
        "land": get_land_prices(district, db, region),
        "permits": get_permits(region, db, district),
    }
    itemized = itemized_estimate(params.model_dump(), db, sources)
    return {"user": user.username, "pdf_file": generate_pdf(itemized, sources)}


@router.post("/feedback")
async def feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    estimate = (
        db.query(Estimate)
        .filter(Estimate.id == data.estimate_id, Estimate.user_id == user.id)
        .first()
    )
    if estimate is None:
        raise HTTPException(status_code=404, detail="Estimate not found")
    result = submit_feedback(db, data.estimate_id, data.actual_cost, data.notes or "")
    return {"user": user.username, "result": result}