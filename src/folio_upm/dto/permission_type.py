from enum import Enum
from typing import Optional


class PermissionType(Enum):
    MUTABLE = ("mutable", "user-created")
    INVALID = ("invalid", None)
    DEPRECATED = ("deprecated", None)
    QUESTIONABLE = ("questionable", None)
    UNPROCESSED = ("unprocessed", None)
    OKAPI = ("okapi", "system-created")
    UNKNOWN = ("unknown", None)

    @staticmethod
    def from_string(value: Optional[str]) -> "PermissionType":
        if value is None:
            return PermissionType.UNKNOWN
        value_to_find = value.upper()
        if value_to_find in PermissionType.__members__:
            return PermissionType[value_to_find]
        return PermissionType.UNKNOWN

    def get_name(self) -> str:
        return self.value[0]

    def get_visible_name(self) -> str:
        return self.value[1] if self.value[1] else self.value[0]


MUTABLE = PermissionType.MUTABLE
INVALID = PermissionType.INVALID
DEPRECATED = PermissionType.DEPRECATED
QUESTIONABLE = PermissionType.QUESTIONABLE
UNPROCESSED = PermissionType.UNPROCESSED
OKAPI = PermissionType.OKAPI
UNKNOWN = PermissionType.UNKNOWN


SUPPORTED_PS_TYPES = list[PermissionType](
    [
        PermissionType.MUTABLE,
        PermissionType.INVALID,
        PermissionType.DEPRECATED,
        PermissionType.QUESTIONABLE,
        PermissionType.UNPROCESSED,
        PermissionType.OKAPI,
    ]
)
