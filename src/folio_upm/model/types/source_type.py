from enum import Enum
from typing import Optional


class SourceType(Enum):
    PS = "ps"
    FLAT_PS = "flat"
    OKAPI_PS = "okapi"

    def get_name(self) -> str:
        return self.value

    @staticmethod
    def from_string(value: Optional[str]) -> Optional["SourceType"]:
        if value is None:
            return None
        value_to_find = value.upper()
        if value_to_find in SourceType.__members__:
            return SourceType[value_to_find]
        return None


PS = SourceType.PS
FLAT_PS = SourceType.FLAT_PS
OKAPI_PS = SourceType.OKAPI_PS
