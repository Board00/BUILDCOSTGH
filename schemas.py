from pydantic import BaseModel


class AdminCreate(BaseModel):
    username: str
    password: str

# ✅ Add this class right below the imports
class EstimateRequest(BaseModel):
    region: str
    district: str
    area: float
    building_type: str
    finishing: str
    extras: list[str] = []

class MaterialCreate(BaseModel):
    item: str
    unit: str
    price: float
    region: str
    source: str

class LaborRateCreate(BaseModel):
    trade: str
    rate: float
    region: str
    source: str

class LandPriceCreate(BaseModel):
    district: str
    price: float
    source: str

class PermitCreate(BaseModel):
    fee_type: str
    amount: float
    region: str
    source: str