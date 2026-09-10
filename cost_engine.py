# PLEASE NOTE THIS CODE IS FOR TESTING PURPOSE AND IT STANDS TO BE CHANGES BASED ON THE RIGHT LOGIC
# THE MATHEMATICAL LOGIC STANDS TO BE CHANGED TOO
from statistics import median
from exceptions import ValidationError

REGION_MULTIPLIERS = {
    "Ahafo": 0.92,
    "Bono": 0.90,
    "Bono East": 0.88,
    "Greater Accra": 1.15,
    "Ashanti": 1.0,
    "Central": 0.95,
    "Eastern": 0.98,
    "North East": 0.84,
    "Northern": 0.86,
    "Oti": 0.86,
    "Savannah": 0.82,
    "Upper East": 0.88,
    "Upper West": 0.84,
    "Volta": 0.92,
    "Western": 1.02,
    "Western North": 0.94,
}

BUILDING_MULTIPLIERS = {
    "Residential": 1.0,
    "Commercial": 1.25,
    "Mixed-Use": 1.2,
    "Industrial": 1.1,
}

FINISHING_MULTIPLIERS = {
    "Basic": 0.85,
    "Standard": 1.0,
    "Premium": 1.2,
    "Luxury": 1.45,
}

EXTRA_COSTS = {
    "Fence": 18000,
    "Gate": 9000,
    "Borehole": 25000,
    "Septic Tank": 18000,
    "Garage": 30000,
    "Boys Quarters": 70000,
    "Solar System": 45000,
}

STRUCTURAL_MULTIPLIERS = {
    "Sandcrete block": 1.0,
    "Brick": 1.08,
    "Steel frame": 1.22,
}

ROOFING_MULTIPLIERS = {
    "Long-span aluminium": 1.0,
    "Tile": 1.18,
    "Concrete tile": 1.25,
}


def calculate_cost(area, unit_cost, multiplier=1.0):
    if area <= 0:
        raise ValidationError("Area must be greater than zero")
    if unit_cost <= 0:
        raise ValidationError("Unit cost must be greater than zero")
    if multiplier <= 0:
        raise ValidationError("Multiplier must be greater than zero")

    return area * unit_cost * multiplier


def itemized_estimate(params, db_session=None, sources=None):
    required_keys = ["area"]
    for key in required_keys:
        if key not in params:
            raise ValidationError(f"Missing required parameter: {key}")

    area = params["area"]
    if not isinstance(area, (int, float)):
        raise ValidationError("Area must be numeric")

    sources = sources or {}

    # Retrieved prices influence the deterministic calculation; the model never
    # invents a total when the source tables are available.
    material_prices = [item["price"] for item in sources.get("materials", []) if item.get("price", 0) > 0]
    labor_rates = [item["rate"] for item in sources.get("labor", []) if item.get("rate", 0) > 0]
    material_factor = median(material_prices) / 100 if material_prices else 1.0
    labor_factor = median(labor_rates) / 100 if labor_rates else 1.0

    # Region factor
    region = params.get("region")
    region_key = region.value if hasattr(region, "value") else region
    location_factor = REGION_MULTIPLIERS.get(region_key, 1.0)

    # Building factor
    building_type = params.get("building_type")
    building_key = building_type.value if hasattr(building_type, "value") else building_type
    building_factor = BUILDING_MULTIPLIERS.get(building_key, 1.0)

    # Finishing factor
    finishing = params.get("finishing")
    finishing_key = finishing.value if hasattr(finishing, "value") else finishing
    finishing_factor = FINISHING_MULTIPLIERS.get(finishing_key, 1.0)
    structural_factor = STRUCTURAL_MULTIPLIERS.get(params.get("structural_type"), 1.0)
    roofing_factor = ROOFING_MULTIPLIERS.get(params.get("roofing_type"), 1.0)

    factor = location_factor * building_factor * finishing_factor * structural_factor

    # Planning rates are deliberately separated by phase so the result can be
    # reviewed and adjusted by a quantity surveyor.
    foundation_cost = calculate_cost(area, 250 * material_factor, 1.1 * location_factor)
    superstructure_cost = calculate_cost(area, 650 * material_factor, factor)
    roofing_cost = calculate_cost(area, 300 * material_factor, 1.2 * finishing_factor * roofing_factor * location_factor)
    finishing_cost = calculate_cost(area, 500 * material_factor, 0.9 * finishing_factor * building_factor)
    labor_cost = calculate_cost(area, 350 * labor_factor, factor)

    # Extras
    extras = params.get("extras", [])
    extras_cost = 0
    for extra in extras:
        extra_key = extra.value if hasattr(extra, "value") else extra
        extras_cost += EXTRA_COSTS.get(extra_key, 0)

    # Permits
    permits_cost = sum(item.get("amount", 0) for item in sources.get("permits", []))

    # Land
    land_prices = [item["price"] for item in sources.get("land", []) if item.get("price", 0) > 0]
    land_cost = median(land_prices) if land_prices and not params.get("land_owned", False) else 0

    subtotal = (
        foundation_cost
        + superstructure_cost
        + roofing_cost
        + finishing_cost
        + labor_cost
        + extras_cost
        + permits_cost
        + land_cost
    )
    contingency = subtotal * 0.10
    total = subtotal + contingency

    return {
        "land": round(land_cost, 2),
        "site_preparation_and_foundation": round(foundation_cost, 2),
        "superstructure": round(superstructure_cost, 2),
        "roofing": round(roofing_cost, 2),
        "finishes": round(finishing_cost, 2),
        "labor": round(labor_cost, 2),
        "permits": round(permits_cost, 2),
        "extras": round(extras_cost, 2),
        "contingency": round(contingency, 2),
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
    }


def estimate_range(total, confidence_level):
    """Return a planning range; tighter ranges require better source coverage."""
    variance = {"High": 0.15, "Medium": 0.20, "Low": 0.25}.get(confidence_level, 0.25)
    return {
        "low": round(total * (1 - variance), 2),
        "high": round(total * (1 + variance), 2),
        "variance_percent": round(variance * 100),
    }
