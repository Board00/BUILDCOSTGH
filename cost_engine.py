def calculate_cost(area, unit_cost, multiplier=1.0):
    return area * unit_cost * multiplier

def itemized_estimate(params, db_session):
    # Example deterministic calculations
    foundation_cost = calculate_cost(params['area'], 50, 1.1)
    superstructure_cost = calculate_cost(params['area'], 120, 1.0)
    roofing_cost = calculate_cost(params['area'], 80, 1.2)

    total = foundation_cost + superstructure_cost + roofing_cost
    return {
        "foundation": foundation_cost,
        "superstructure": superstructure_cost,
        "roofing": roofing_cost,
        "total": total
    }
