import os

from fastapi import FastAPI, Header

from exceptions import *
from models import *
from cost_engine import itemized_estimate
from retrieval import get_material_prices, get_labor_rates, get_land_prices, get_permits
from confidence import confidence_score
from pdf_export import generate_pdf
from feedback import submit_feedback
from auth import *
from datetime import timedelta
from schemas import *
from error_handlers import register_error_handlers


app = FastAPI()
register_error_handlers(app)


@app.get("/", tags=["Authentication"])
async def root():
    return {"message": "Welcome to Land Price API"}

@app.post("/admin/register", include_in_schema=False, tags=["Authentication"])
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
        is_admin=True
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin registered successfully", "admin_id": new_admin.id}

@app.post("/register", tags=["Authentication"])
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username
    password = data.password
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(username=username, hashed_password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": user.username}, expires_delta=timedelta(minutes=30))
    refresh_token = create_token({"sub": user.username}, expires_delta=timedelta(days=7), token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post("/refresh", tags=["Authentication"])
async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh" or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    username = payload.get("sub")
    new_access_token = create_token({"sub": username}, expires_delta=timedelta(minutes=30), token_type="access")
    return {"access_token": new_access_token}

@app.post("/logout", tags=["Authentication"])
async def logout(user: str = Depends(get_current_user)):
    # Optional: add token invalidation logic here if you implement blacklisting
    return {
        "user": user,
        "message": "Logout successful. Please discard your tokens."
    }

@app.post("/land_prices", tags=["ADMIN'S ONLY"])
async def create_land_price(land: LandPriceCreate, db: Session = Depends(get_db),
                            current_admin: User = Depends(get_current_admin)):
    new_land = LandPrice(**land.dict())
    db.add(new_land)
    db.commit()
    db.refresh(new_land)
    return {"message": "Land price added successfully", "land_price": new_land.id}

@app.post("/permits", tags=["ADMIN'S ONLY"])
async def create_permit(permit: PermitCreate, db: Session = Depends(get_db),
                        current_admin: User = Depends(get_current_admin)):
    new_permit = Permit(**permit.dict())
    db.add(new_permit)
    db.commit()
    db.refresh(new_permit)
    return {"message": "Permit added successfully", "permit": new_permit.id}

@app.post("/materials", tags=["ADMIN'S ONLY"])
async def create_material(material: MaterialCreate, db: Session = Depends(get_db),
                          current_admin: User = Depends(get_current_admin)):
    new_material = Material(**material.dict())
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return {"message": "Material added successfully", "material_id": new_material.id}

@app.post("/labor_rates", tags=["ADMIN'S ONLY"])
async def create_labor_rate(labor: LaborRateCreate, db: Session = Depends(get_db),
                            current_admin: User = Depends(get_current_admin)):
    new_labor = LaborRate(**labor.dict())
    db.add(new_labor)
    db.commit()
    db.refresh(new_labor)
    return {"message": "Labor rate added successfully", "labor_rate": new_labor.id}

from models import Estimate

@app.post("/estimate")
async def generate_estimate(
    request: EstimateRequest,
    db=Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Compute estimate details
    region = request.region.value
    district = request.district.value
    sources = {
        "materials": get_material_prices(region, db, district),
        "labor": get_labor_rates(region, db, district),
        "land": get_land_prices(district, db, region),
        "permits": get_permits(region, db, district)
    }
    itemized = itemized_estimate(request.model_dump(), db, sources)
    confidence = confidence_score([s for cat in sources.values() for s in cat])
    disclaimer = "Planning estimate, not certified QS quote"

    # 2. Save to database
    try:
        estimate = Estimate(
            user_input=request.dict(),
            user_id=user.id,
            itemized=itemized,
            total=itemized["total"],
            confidence=confidence["level"],
        )

        db.add(estimate)
        db.commit()
        db.refresh(estimate)
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to save estimate: {e}")

    # 3. Return response including DB record ID
    return {
        "user": user.username,
        "estimate_id": estimate.id,
        "itemized": itemized,
        "sources": sources,
        "confidence": confidence,
        "disclaimer": disclaimer
    }

@app.post("/export")
async def export_pdf(params: EstimateRequest, db=Depends(get_db), user: User = Depends(get_current_user)):
    region = params.region.value
    district = params.district.value
    sources = {
        "materials": get_material_prices(region, db, district),
        "labor": get_labor_rates(region, db, district),
        "land": get_land_prices(district, db, region),
        "permits": get_permits(region, db, district),
    }
    itemized = itemized_estimate(params.model_dump(), db, sources)
    filename = generate_pdf(itemized, sources)
    return {"user": user.username, "pdf_file": filename}

@app.post("/feedback")
async def feedback(data: FeedbackCreate, db=Depends(get_db), user: User = Depends(get_current_user)):
    estimate = db.query(Estimate).filter(Estimate.id == data.estimate_id, Estimate.user_id == user.id).first()
    if estimate is None:
        raise HTTPException(status_code=404, detail="Estimate not found")
    result = submit_feedback(db, data.estimate_id, data.actual_cost, data.notes or "")
    return {
        "user": user.username,
        "result": result
    }


