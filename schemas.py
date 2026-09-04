from pydantic import BaseModel, Field, field_validator
from constants import *
# from validators import DistrictValidator


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class EstimateRequest(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    land_owned: bool = False
    area: float = Field(gt=0)
    building_type: BuildingTypeEnum
    finishing: FinishingEnum
    extras: list[ExtraEnum] = Field(default_factory=list)

    @field_validator("district")
    @classmethod
    def district_must_match_region(cls, district, info):
        region = info.data.get("region")
        if region is not None:
            district_text = district.value
            region_districts = {
                "Central": {"Central", "Greater Accra", "Ashanti"},
            }
            prefixes = {
                "Central": ("Central", "Cape", "Abura", "Agona", "Ajumako", "Asikuma", "Assin", "Awutu", "Effutu", "Ekumfi", "Gomoa", "Komenda", "Mfantsiman", "Twifo", "Upper Denkyira"),
                "Greater Accra": ("Accra", "Ada", "Adentan", "Ashaiman", "Ayawaso", "Ga ", "Korle", "Kpone", "Krowor", "La ", "Ledzokuku", "Ningo", "Okaikwei", "Shai", "Tema"),
                "Ashanti": ("Adansi", "Afigya", "Ahafo", "Amansie", "Asante", "Asokore", "Asokwa", "Atwima", "Bekwai", "Bosome", "Bosomtwe", "Ejisu", "Ejura", "Kumasi", "Kwabre", "Kwadaso", "Mampong", "Obuasi", "Offinso", "Oforikrom", "Old Tafo", "Sekyere", "Suame"),
            }
            if not district_text.startswith(prefixes[region.value]):
                raise ValueError(f"District '{district_text}' does not belong to region '{region.value}'")
        return district


class MaterialCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    item: MaterialItemEnum
    unit: str
    price: float = Field(gt=0)
    source: str


class LaborRateCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    trade: str
    rate: float = Field(gt=0)
    source: str


class LandPriceCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    price: float = Field(gt=0)
    source: str


class PermitCreate(BaseModel):
    region: RegionEnum
    district: DistrictEnum
    fee_type: str
    amount: float = Field(gt=0)
    source: str


class MaterialUpdate(BaseModel):
    region: RegionEnum | None = None
    district: DistrictEnum | None = None
    item: MaterialItemEnum | None = None
    unit: str | None = None
    price: float | None = Field(default=None, gt=0)
    source: str | None = None


class LaborRateUpdate(BaseModel):
    region: RegionEnum | None = None
    district: DistrictEnum | None = None
    trade: str | None = None
    rate: float | None = Field(default=None, gt=0)
    source: str | None = None


class LandPriceUpdate(BaseModel):
    region: RegionEnum | None = None
    district: DistrictEnum | None = None
    price: float | None = Field(default=None, gt=0)
    source: str | None = None


class PermitUpdate(BaseModel):
    region: RegionEnum | None = None
    district: DistrictEnum | None = None
    fee_type: str | None = None
    amount: float | None = Field(default=None, gt=0)
    source: str | None = None

class FeedbackCreate(BaseModel):
    estimate_id: int
    actual_cost: float = Field(gt=0)
    notes: str | None = None