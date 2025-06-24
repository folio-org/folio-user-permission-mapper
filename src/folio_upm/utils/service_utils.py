from collections import OrderedDict


class ServiceUtils:

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
