from collections import OrderedDict


class ServiceUtils:

    @staticmethod
    def is_system_permission(permission: str) -> bool:
        return permission.startswith("SYS#")

    @staticmethod
    def unique_values(iterable):
        return list(OrderedDict.fromkeys(iterable).keys())
