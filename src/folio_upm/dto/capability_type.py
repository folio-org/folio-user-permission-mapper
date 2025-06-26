from enum import Enum


class CapabilityType(str, Enum):
    UNKNOWN = "unknown"
    CAPABILITY = "capability"
    CAPABILITY_SET = "capability-set"


UNKNOWN = CapabilityType.UNKNOWN
CAPABILITY = CapabilityType.CAPABILITY
CAPABILITY_SET = CapabilityType.CAPABILITY_SET
