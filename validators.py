from pydantic import field_validator
from constants import *
from exceptions import *



from pydantic import field_validator
from constants import DistrictEnum, RegionEnum
from exceptions import ValidationError

# class DistrictValidator:
#     @staticmethod
#     @field_validator("district")
#     def validate_district(cls, value, values):
#         region = values.get(RegionEnum)
#         if region:
#             enum_class = DISTRICT_ENUM_MAP[region]
#             allowed_values = [e.value for e in enum_class]
#             if value not in allowed_values:
#                 allowed = ", ".join(allowed_values)
#                 raise ValidationError(
#                     f"Invalid district '{value}'. Allowed districts for {region.value}: {allowed}"
#                 )
#         return value



class ExtrasValidator:
    @staticmethod
    @field_validator("extras")
    def validate_extras( value):
        # value is a list of ExtraEnum
        invalid = [item for item in value if item not in ExtraEnum]
        if invalid:
            allowed = ", ".join([e.value for e in ExtraEnum])
            raise ValidationError(
                f"Invalid extras: {invalid}. Allowed extras: {allowed}"
            )
        return value