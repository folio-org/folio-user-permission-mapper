from enum import Enum


class SourceType(str, Enum):
    PS = "ps"
    FLAT_PS = "flat_ps"
    OKAPI_PS = "okapi_ps"


PS = SourceType.PS
FLAT_PS = SourceType.FLAT_PS
OKAPI_PS = SourceType.OKAPI_PS
