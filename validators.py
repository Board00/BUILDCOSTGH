from constants import *
from pydantic import field_validator
from exceptions import ValidationError


class ExtrasValidator:
    @staticmethod
    @field_validator("extras")
    def validate_extras( value):
        invalid = [item for item in value if item not in ExtraEnum]
        if invalid:
            allowed = ", ".join([e.value for e in ExtraEnum])
            raise ValidationError(
                f"Invalid extras: {invalid}. Allowed extras: {allowed}"
            )
        return value