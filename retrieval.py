# from sqlalchemy import text
#
# def get_material_prices(region, db_session):
#     return db_session.execute(
#         "SELECT item, price, unit, source, date FROM materials WHERE region=%s",
#         (region,)
#     ).fetchall()
#
# def get_labor_rates(region, db_session):
#     return db_session.execute(
#         "SELECT trade, rate, source, date FROM labor_rates WHERE region=%s",
#         (region,)
#     ).fetchall()
#
# def get_land_prices(district, db_session):
#     return db_session.execute(
#         "SELECT district, price, source, date FROM land_prices WHERE district=%s",
#         (district,)
#     ).fetchall()
#
# def get_permits(region, db_session):
#     return db_session.execute(
#         "SELECT fee_type, amount, source, date FROM permits WHERE region=%s",
#         (region,)
#     ).fetchall()


from sqlalchemy.orm import Session
from models import Material, LaborRate, LandPrice, Permit

def get_material_prices(region: str, db_session: Session):
    return db_session.query(Material).filter(Material.region == region).all()

def get_labor_rates(region: str, db_session: Session):
    return db_session.query(LaborRate).filter(LaborRate.region == region).all()

def get_land_prices(district: str, db_session: Session):
    return db_session.query(LandPrice).filter(LandPrice.district == district).all()

def get_permits(region: str, db_session: Session):
    return db_session.query(Permit).filter(Permit.region == region).all()
