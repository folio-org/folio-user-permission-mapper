import random
import string
from typing import Optional

from folio_upm.model.okapi.permission_set import PermissionSet


class Utils:

    @staticmethod
    def bool_to_char(value: bool | None) -> chr:
        if value is None:
            return chr(0x003F)
        return chr(0x2705) if value else chr(0x2BBD)

    @staticmethod
    def safe_cast(val, to_type, default=None):
        try:
            return to_type(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def random_string(length):
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=length))
        return random_string

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
    def is_system_permission(permission: str) -> bool:
        return permission.startswith("SYS#")

    @staticmethod
    def get_module_id(permission_set: PermissionSet) -> Optional[str]:
        module_name = permission_set.moduleName
        if not module_name:
            return None
        module_version = permission_set.moduleVersion
        if not module_version:
            return module_name
        return f"{module_name}-{module_version}"
