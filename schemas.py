from pydantic import BaseModel
from constants import *
# from validators import DistrictValidator


class AdminCreate(BaseModel):
    username: str
    password: str


class EstimateRequest(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    area: float
    building_type: BuildingTypeEnum
    finishing: FinishingEnum
    extras: list[ExtraEnum] = []


class MaterialCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    item: MaterialItemEnum
    unit: str
    price: float
    source: str


class LaborRateCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    trade: str
    rate: float
    source: str


class LandPriceCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    price: float
    source: str


class PermitCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    fee_type: str
    amount: float
    source: str

class FeedbackCreate(BaseModel):
    estimate_id: int
    actual_cost: float
    notes: str | None = None