from typing import List

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
    error: HttpReqErr | None = None

    @staticmethod
    def for_role(role, status, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role",
            entityId=role.name,
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_removed_role(role_id: str, status: str, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role",
            entityId=role_id,
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability(role: Role, capability_id: str, status: str, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capability",
            entityId=f"Role: '{role.name}' -> {role.id}\nCapability: {capability_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capabilities(role, capability_ids: List[str], status: str, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capabilities",
            entityId=f"Role: '{role.name}' -> {role.id}\nCapabilities: {capability_ids}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability_set(role, set_id: str, status: str, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capability-set",
            entityId=f"Role: '{role.name}' -> {role.id}\nCapabilitySet: {set_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability_sets(role, set_ids: List[str], status: str, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role-capability-sets",
            entityId=f"Role: '{role.name}' -> {role.id}\nCapabilitySets: {set_ids}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_users(role, user_id: str, status: str, reason=None, error=None):
        return EntityMigrationResult(
            status=status,
            entityName="role-user",
            entityId=f"Role: '{role.name}' -> {role.id}\nUser: {user_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def role_not_found_result(role_name: str):
        return EntityMigrationResult(
            status="not_matched",
            entityName="role",
            entityId=f"{role_name}",
            reason="Failed to find by name",
        )
