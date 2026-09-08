import os
from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Response
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
from cost_engine import estimate_range, itemized_estimate
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
    LandPriceUpdate,
    LaborRateCreate,
    LaborRateUpdate,
    MaterialCreate,
    MaterialUpdate,
    PermitCreate,
    PermitUpdate,
    ProfileUpdate,
    RegisterRequest,
)


router = APIRouter()


def _source_records(sources):
    return [
        {**record, "category": category}
        for category, records in sources.items()
        for record in records
    ]


def _get_reference_record(db: Session, model, record_id: int, resource_name: str):
    record = db.query(model).filter(model.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail=f"{resource_name} not found")
    return record


def _update_reference_record(db: Session, record, values: dict):
    for field, value in values.items():
        setattr(record, field, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(record)
    return record


def _delete_reference_record(db: Session, record):
    db.delete(record)
    db.commit()


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

    new_user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login", tags=["Authentication"])
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": user.username}, expires_delta=timedelta(minutes=30))
    refresh_token = create_token(
        {"sub": user.username}, expires_delta=timedelta(days=7), token_type="refresh"
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False,
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

@router.get("/user", tags=["Authentication"])
async def logged_user(user: User = Depends(get_current_user)):
    return {
        "message": f"Welcome, {user.username}! You are logged in.",
        "user_id": user.id,
        "is_admin": user.is_admin,
    }


@router.patch("/user", tags=["Authentication"])
async def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    values = data.model_dump(exclude_unset=True)
    for field, value in values.items():
        existing = db.query(User).filter(User.username == value).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail=f"{field.capitalize()} already exists")
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    access_token = create_token({"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {
        "message": "Profile updated successfully",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
        },
    }


@router.delete("/user", tags=["Authentication"])
async def deactivate_account(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.is_active = False
    db.commit()
    return {"message": "Account deactivated successfully"}


@router.get("/estimates", tags=["General User"])
async def list_my_estimates(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Estimate)
        .filter(Estimate.user_id == user.id)
        .order_by(Estimate.date.desc())
        .all()
    )


@router.get("/admin/dashboard-data", tags=["Admin"])
async def admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return {
        "users": db.query(User).count(),
        "estimates": db.query(Estimate).count(),
        "materials": db.query(Material).count(),
        "labor_rates": db.query(LaborRate).count(),
        "land_prices": db.query(LandPrice).count(),
        "permits": db.query(Permit).count(),
    }

@router.post("/logout", tags=["Authentication"])
async def logout(response: Response, user: User = Depends(get_current_user)):
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    return {"user": user, "message": "Logout successful. Please discard your tokens."}


@router.post("/admin/land_prices", tags=["Admin: Land Prices"])
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


@router.get("/admin/land_prices", tags=["Admin: Land Prices"])
async def list_land_prices(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(LandPrice).all()


@router.get("/admin/land_prices/{land_price_id}", tags=["Admin: Land Prices"])
async def get_land_price(
    land_price_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return _get_reference_record(db, LandPrice, land_price_id, "Land price")


@router.patch("/admin/land_prices/{land_price_id}", tags=["Admin: Land Prices"])
async def update_land_price(
    land_price_id: int,
    land: LandPriceUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, LandPrice, land_price_id, "Land price")
    return _update_reference_record(db, record, land.model_dump(exclude_unset=True))


@router.put("/admin/land_prices/{land_price_id}", tags=["Admin: Land Prices"])
async def replace_land_price(
    land_price_id: int,
    land: LandPriceCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, LandPrice, land_price_id, "Land price")
    return _update_reference_record(db, record, land.model_dump())


@router.delete("/admin/land_prices/{land_price_id}", tags=["Admin: Land Prices"])
async def delete_land_price(
    land_price_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, LandPrice, land_price_id, "Land price")
    _delete_reference_record(db, record)
    return {"message": "Land price deleted successfully"}


@router.post("/admin/permits", tags=["Admin: Permits"])
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


@router.get("/admin/permits", tags=["Admin: Permits"])
async def list_permits(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(Permit).all()


@router.get("/admin/permits/{permit_id}", tags=["Admin: Permits"])
async def get_permit(
    permit_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return _get_reference_record(db, Permit, permit_id, "Permit")


@router.patch("/admin/permits/{permit_id}", tags=["Admin: Permits"])
async def update_permit(
    permit_id: int,
    permit: PermitUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, Permit, permit_id, "Permit")
    return _update_reference_record(db, record, permit.model_dump(exclude_unset=True))


@router.put("/admin/permits/{permit_id}", tags=["Admin: Permits"])
async def replace_permit(
    permit_id: int,
    permit: PermitCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, Permit, permit_id, "Permit")
    return _update_reference_record(db, record, permit.model_dump())


@router.delete("/admin/permits/{permit_id}", tags=["Admin: Permits"])
async def delete_permit(
    permit_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, Permit, permit_id, "Permit")
    _delete_reference_record(db, record)
    return {"message": "Permit deleted successfully"}


@router.post("/admin/materials", tags=["Admin: Materials"])
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


@router.get("/admin/materials", tags=["Admin: Materials"])
async def list_materials(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(Material).all()


@router.get("/admin/materials/{material_id}", tags=["Admin: Materials"])
async def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return _get_reference_record(db, Material, material_id, "Material")


@router.patch("/admin/materials/{material_id}", tags=["Admin: Materials"])
async def update_material(
    material_id: int,
    material: MaterialUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, Material, material_id, "Material")
    return _update_reference_record(db, record, material.model_dump(exclude_unset=True))


@router.put("/admin/materials/{material_id}", tags=["Admin: Materials"])
async def replace_material(
    material_id: int,
    material: MaterialCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, Material, material_id, "Material")
    return _update_reference_record(db, record, material.model_dump())


@router.delete("/admin/materials/{material_id}", tags=["Admin: Materials"])
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, Material, material_id, "Material")
    _delete_reference_record(db, record)
    return {"message": "Material deleted successfully"}


@router.post("/admin/labor_rates", tags=["Admin: Labor"])
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


@router.get("/admin/labor_rates", tags=["Admin: Labor"])
async def list_labor_rates(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(LaborRate).all()


@router.get("/admin/labor_rates/{labor_rate_id}", tags=["Admin: Labor"])
async def get_labor_rate(
    labor_rate_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return _get_reference_record(db, LaborRate, labor_rate_id, "Labor rate")


@router.patch("/admin/labor_rates/{labor_rate_id}", tags=["Admin: Labor"])
async def update_labor_rate(
    labor_rate_id: int,
    labor: LaborRateUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, LaborRate, labor_rate_id, "Labor rate")
    return _update_reference_record(db, record, labor.model_dump(exclude_unset=True))


@router.put("/admin/labor_rates/{labor_rate_id}", tags=["Admin: Labor"])
async def replace_labor_rate(
    labor_rate_id: int,
    labor: LaborRateCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, LaborRate, labor_rate_id, "Labor rate")
    return _update_reference_record(db, record, labor.model_dump())


@router.delete("/admin/labor_rates/{labor_rate_id}", tags=["Admin: Labor"])
async def delete_labor_rate(
    labor_rate_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    record = _get_reference_record(db, LaborRate, labor_rate_id, "Labor rate")
    _delete_reference_record(db, record)
    return {"message": "Labor rate deleted successfully"}


@router.post("/estimate", tags=["General User"])
async def generate_estimate(
    request: EstimateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    region = request.region.value
    district = request.district
    sources = {
        "materials": get_material_prices(region, db, district),
        "labor": get_labor_rates(region, db, district),
        "land": get_land_prices(district, db, region),
        "permits": get_permits(region, db, district),
    }
    itemized = itemized_estimate(request.model_dump(), db, sources)
    source_records = _source_records(sources)
    confidence = confidence_score(source_records)
    planning_range = estimate_range(itemized["total"], confidence["level"])

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
        "planning_range": planning_range,
        "assumptions": [
            f"{request.area:g} m² of {request.building_type.value.lower()} floor area",
            f"{request.finishing.value.lower()} finishing using {request.structural_type.lower()}",
            "10% contingency is included for price movement and scope uncertainty",
            "Land is excluded because the plot is marked as already owned" if request.land_owned else "Land is included using the district or regional median",
        ],
        "disclaimer": "Planning estimate, not certified QS quote",
    }


@router.post("/export", tags=["General User"])
async def export_pdf(
    params: EstimateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    region = params.region.value
    district = params.district
    sources = {
        "materials": get_material_prices(region, db, district),
        "labor": get_labor_rates(region, db, district),
        "land": get_land_prices(district, db, region),
        "permits": get_permits(region, db, district),
    }
    itemized = itemized_estimate(params.model_dump(), db, sources)
    return {"user": user.username, "pdf_file": generate_pdf(itemized, sources)}


@router.post("/feedback", tags=["General User"])
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