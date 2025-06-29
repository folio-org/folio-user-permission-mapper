from typing import Optional, List

from pydantic import BaseModel

from folio_upm.dto.eureka import Role


class HttpReqErr(BaseModel):
    message: str
    status: int = 500
    responseBody: str = ""


class EntityMigrationResult(BaseModel):
    status: str
    entityName: str
    entityId: str
    reason: str | None = None
    error: HttpReqErr | None = []

    @staticmethod
    def for_role(role, status, reason = None, error= None):
        return EntityMigrationResult(
            status=status,
            entityName="role",
            entityId=role.id,
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability(rch, capability_id: str, status: str, reason = None, error  = None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capability",
            entityId=f"Role: '{rch.roleName}' -> {rch.roleId}\nCapability: {capability_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability_set(rch, set_id: str, status: str, reason = None, error  = None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capability-set",
            entityId=f"Role: '{rch.roleName}' -> {rch.roleId}\nCapabilitySet: {set_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_users(ru, user_id: str, status: str, reason = None, error  = None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capability-set",
            entityId=f"Role: '{ru.roleName}' -> {ru.roleId}\nUser: {user_id}",
            reason=reason,
            error=error,
        )
