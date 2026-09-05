from statistics import median
from exceptions import ValidationError

REGION_MULTIPLIERS = {
    "Greater Accra": 1.15,
    "Ashanti": 1.0,
    "Central": 0.95,
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

    # Extract material and labor factors
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

    factor = location_factor * building_factor * finishing_factor

    # Core cost components
    foundation_cost = calculate_cost(area, 50 * material_factor, 1.1 * location_factor)
    superstructure_cost = calculate_cost(area, 120 * material_factor, factor)
    roofing_cost = calculate_cost(area, 80 * material_factor, 1.2 * finishing_factor * location_factor)
    labor_cost = calculate_cost(area, 70 * labor_factor, factor)

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

    total = foundation_cost + superstructure_cost + roofing_cost + labor_cost + extras_cost + permits_cost + land_cost

    return {
        "foundation": foundation_cost,
        "superstructure": superstructure_cost,
        "roofing": roofing_cost,
        "labor": labor_cost,
        "extras": extras_cost,
        "permits": permits_cost,
        "land": land_cost,
        "total": total
    }
