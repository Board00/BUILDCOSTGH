# def calculate_cost(area, unit_cost, multiplier=1.0):
#     return area * unit_cost * multiplier
#
# def itemized_estimate(params, db_session):
#     # Example deterministic calculations
#     foundation_cost = calculate_cost(params['area'], 50, 1.1)
#     superstructure_cost = calculate_cost(params['area'], 120, 1.0)
#     roofing_cost = calculate_cost(params['area'], 80, 1.2)
#
#     total = foundation_cost + superstructure_cost + roofing_cost
#     return {
#         "foundation": foundation_cost,
#         "superstructure": superstructure_cost,
#         "roofing": roofing_cost,
#         "total": total
#     }


from exceptions import ValidationError

def calculate_cost(area, unit_cost, multiplier=1.0):
    if area <= 0:
        raise ValidationError("Area must be greater than zero")
    if unit_cost <= 0:
        raise ValidationError("Unit cost must be greater than zero")
    if multiplier <= 0:
        raise ValidationError("Multiplier must be greater than zero")

    return area * unit_cost * multiplier


def itemized_estimate(params, db_session):
    required_keys = ["area"]
    for key in required_keys:
        if key not in params:
            raise ValidationError(f"Missing required parameter: {key}")

    area = params["area"]

    foundation_cost = calculate_cost(area, 50, 1.1)
    superstructure_cost = calculate_cost(area, 120, 1.0)
    roofing_cost = calculate_cost(area, 80, 1.2)

    total = foundation_cost + superstructure_cost + roofing_cost

    return {
        "foundation": foundation_cost,
        "superstructure": superstructure_cost,
        "roofing": roofing_cost,
        "total": total
    }
