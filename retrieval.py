from sqlalchemy.orm import Session
from models import Material, LaborRate, LandPrice, Permit
from exceptions import DatabaseError, ValidationError

def get_material_prices(region: str, db_session: Session, district: str | None = None):
    if not isinstance(region, str):
        raise ValidationError("Region must be a string")

    try:
        query = db_session.query(Material).filter(Material.region == region)
        if district:
            query = query.filter(Material.district == district)
        results = query.all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve material prices: {e}")

    if not results:
        raise ValidationError(f"No material prices found for region '{region}'")

    return [
        {
            "id": r.id,
            "item": r.item,
            "unit": r.unit,
            "price": float(r.price),
            "source": r.source,
            "region": r.region,
            "district": r.district,
            "date": r.date.isoformat() if r.date else None
        }
        for r in results
    ]


def get_labor_rates(region: str, db_session: Session, district: str | None = None):
    if not isinstance(region, str):
        raise ValidationError("Region must be a string")

    try:
        query = db_session.query(LaborRate).filter(LaborRate.region == region)
        if district:
            query = query.filter(LaborRate.district == district)
        results = query.all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve labor rates: {e}")

    if not results:
        raise ValidationError(f"No labor rates found for region '{region}'")

    return [
        {
            "id": r.id,
            "trade": r.trade,
            "rate": float(r.rate),
            "source": r.source,
            "region": r.region,
            "date": r.date.isoformat() if r.date else None
        }
        for r in results
    ]


def get_land_prices(district: str, db_session: Session, region: str | None = None):
    if not isinstance(district, str):
        raise ValidationError("District must be a string")

    try:
        query = db_session.query(LandPrice).filter(LandPrice.district == district)
        if region:
            query = query.filter(LandPrice.region == region)
        results = query.all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve land prices: {e}")

    if not results:
        raise ValidationError(f"No land prices found for district '{district}'")

    return [
        {
            "id": r.id,
            "district": r.district,
            "price": float(r.price),
            "source": r.source,
            "region": r.region,
            "date": r.date.isoformat() if r.date else None
        }
        for r in results
    ]


def get_permits(region: str, db_session: Session, district: str | None = None):
    if not isinstance(region, str):
        raise ValidationError("Region must be a string")

    try:
        query = db_session.query(Permit).filter(Permit.region == region)
        if district:
            query = query.filter(Permit.district == district)
        results = query.all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve permits: {e}")

    if not results:
        raise ValidationError(f"No permits found for region '{region}'")

    return [
        {
            "id": r.id,
            "fee_type": r.fee_type,
            "amount": float(r.amount),
            "source": r.source,
            "region": r.region,
            "date": r.date.isoformat() if r.date else None
        }
        for r in results
    ]
