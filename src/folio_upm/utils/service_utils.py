class ServiceUtils:

    @staticmethod
    def is_system_permission(permission: str) -> bool:
        return permission.startswith("SYS#")
