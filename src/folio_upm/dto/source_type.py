from enum import Enum


class SourceType(str, Enum):
    PS = "ps"
    FLAT_PS = "flat"
    OKAPI_PS = "okapi"


PS = SourceType.PS
FLAT_PS = SourceType.FLAT_PS
OKAPI_PS = SourceType.OKAPI_PS
