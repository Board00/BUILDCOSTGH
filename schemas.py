from pydantic import BaseModel, Field, model_validator
from constants import *


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class ProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=100)


class RegionDistrictModel(BaseModel):
    region: RegionEnum
    district: DistrictEnum

    @model_validator(mode="after")
    def district_must_match_region(self):
        if self.district.value not in REGION_DISTRICTS[self.region]:
            raise ValueError(
                f"District '{self.district.value}' does not belong to region '{self.region.value}'"
            )
        return self


class OptionalRegionDistrictModel(BaseModel):
    region: RegionEnum | None = None
    district: DistrictEnum | None = None

    @model_validator(mode="after")
    def district_must_match_region(self):
        if self.region is not None and self.district is not None:
            if self.district.value not in REGION_DISTRICTS[self.region]:
                raise ValueError(
                    f"District '{self.district.value}' does not belong to region '{self.region.value}'"
                )
        return self


class EstimateRequest(RegionDistrictModel):
    land_owned: bool = False
    area: float = Field(gt=0)
    building_type: BuildingTypeEnum
    finishing: FinishingEnum
    extras: list[ExtraEnum] = Field(default_factory=list)

class MaterialCreate(RegionDistrictModel):
    item: MaterialItemEnum
    unit: str
    price: float = Field(gt=0)
    source: str


class LaborRateCreate(RegionDistrictModel):
    trade: str
    rate: float = Field(gt=0)
    source: str


class LandPriceCreate(RegionDistrictModel):
    price: float = Field(gt=0)
    source: str


class PermitCreate(RegionDistrictModel):
    fee_type: str
    amount: float = Field(gt=0)
    source: str


class MaterialUpdate(OptionalRegionDistrictModel):
    item: MaterialItemEnum | None = None
    unit: str | None = None
    price: float | None = Field(default=None, gt=0)
    source: str | None = None


class LaborRateUpdate(OptionalRegionDistrictModel):
    trade: str | None = None
    rate: float | None = Field(default=None, gt=0)
    source: str | None = None


class LandPriceUpdate(OptionalRegionDistrictModel):
    price: float | None = Field(default=None, gt=0)
    source: str | None = None


class PermitUpdate(OptionalRegionDistrictModel):
    fee_type: str | None = None
    amount: float | None = Field(default=None, gt=0)
    source: str | None = None

class FeedbackCreate(BaseModel):
    estimate_id: int
    actual_cost: float = Field(gt=0)
    notes: str | None = None