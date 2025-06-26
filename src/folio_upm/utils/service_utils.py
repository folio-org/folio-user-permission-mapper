from collections import OrderedDict
from typing import Any, Optional, Sequence

from folio_upm.dto.okapi import PermissionSet


class ServiceUtils:

    @staticmethod
    def last(value: Sequence[Any | None]):
        if value is not None and len(value) > 0:
            return value[-1]
        return None

    @staticmethod
    def is_system_permission(permission: str) -> bool:
        return permission.startswith("SYS#")

    @staticmethod
    def unique_values(iterable):
        return list(OrderedDict.fromkeys(iterable).keys())

    @staticmethod
    def parse_bool(value: str, default_val: bool) -> bool:
        if not value:
            return default_val
        value = value.lower()
        if value in ("true", "yes", "1"):
            return True
        elif value in ("false", "no", "0"):
            return False
        return default_val

    @staticmethod
    def get_module_id(permission_set: PermissionSet) -> Optional[str]:
        module_name = permission_set.moduleName
        if not module_name:
            return None
        module_version = permission_set.moduleVersion
        if not module_version:
            return module_name
        return f"{module_name}-{module_version}"
