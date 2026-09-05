from sqlalchemy.orm import Session
from models import Material, LaborRate, LandPrice, Permit
from exceptions import DatabaseError, ValidationError

MATERIAL_ITEMS = (
    ("Cement", "bag", 95),
    ("Sand", "ton", 180),
    ("Stones", "ton", 220),
    ("Iron Rods", "ton", 6200),
    ("Wood", "cubic meter", 2400),
    ("Tiles", "square meter", 85),
    ("Paint", "bucket", 420),
    ("Plumbing Materials", "lot", 1800),
    ("Electrical Materials", "lot", 2200),
)

REGION_BASELINES = {
    "Greater Accra": {"multiplier": 1.15, "land": 300000, "permit": 6000},
    "Ashanti": {"multiplier": 1.0, "land": 220000, "permit": 5000},
    "Central": {"multiplier": 0.95, "land": 180000, "permit": 4500},
}


def _baseline_materials(region: str, district: str | None):
    baseline = REGION_BASELINES[region]
    return [
        {
            "id": None,
            "item": item,
            "unit": unit,
            "price": price * baseline["multiplier"],
            "source": "Built-in planning baseline",
            "region": region,
            "district": district or region,
            "date": None,
        }
        for item, unit, price in MATERIAL_ITEMS
    ]


def _baseline_labor(region: str, district: str | None):
    baseline = REGION_BASELINES[region]
    return [
        {
            "id": None,
            "trade": trade,
            "rate": rate * baseline["multiplier"],
            "source": "Built-in planning baseline",
            "region": region,
            "district": district or region,
            "date": None,
        }
        for trade, rate in (
            ("Mason", 90),
            ("Carpenter", 85),
            ("Electrician", 100),
            ("Plumber", 100),
            ("Painter", 75),
        )
    ]


def _baseline_land(region: str, district: str | None):
    baseline = REGION_BASELINES[region]
    return [{
        "id": None,
        "district": district or region,
        "price": baseline["land"],
        "source": "Built-in planning baseline",
        "region": region,
        "date": None,
    }]


def _baseline_permits(region: str, district: str | None):
    baseline = REGION_BASELINES[region]
    return [{
        "id": None,
        "fee_type": "Building permit",
        "amount": baseline["permit"],
        "source": "Built-in planning baseline",
        "region": region,
        "district": district or region,
        "date": None,
    }]


def _require_known_region(region: str):
    if region not in REGION_BASELINES:
        raise ValidationError(f"No pricing baseline configured for region '{region}'")


def get_material_prices(region: str, db_session: Session, district: str | None = None):
    if not isinstance(region, str):
        raise ValidationError("Region must be a string")

    try:
        query = db_session.query(Material).filter(Material.region == region)
        if district:
            query = query.filter(Material.district == district)
        results = query.all()
        if not results and district:
            results = db_session.query(Material).filter(Material.region == region).all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve material prices: {e}")

    if not results:
        _require_known_region(region)
        return _baseline_materials(region, district)

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
        if not results and district:
            results = db_session.query(LaborRate).filter(LaborRate.region == region).all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve labor rates: {e}")

    if not results:
        _require_known_region(region)
        return _baseline_labor(region, district)

    return [
        {
            "id": r.id,
            "trade": r.trade,
            "rate": float(r.rate),
            "source": r.source,
            "region": r.region,
            "district": r.district,
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
        if not results and region:
            results = db_session.query(LandPrice).filter(LandPrice.region == region).all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve land prices: {e}")

    if not results:
        if region:
            _require_known_region(region)
            return _baseline_land(region, district)
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
        if not results and district:
            results = db_session.query(Permit).filter(Permit.region == region).all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve permits: {e}")

    if not results:
        _require_known_region(region)
        return _baseline_permits(region, district)

    return [
        {
            "id": r.id,
            "fee_type": r.fee_type,
            "amount": float(r.amount),
            "source": r.source,
            "region": r.region,
            "district": r.district,
            "date": r.date.isoformat() if r.date else None
        }
        for r in results
    ]
