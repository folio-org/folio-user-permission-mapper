from typing import List, Optional

from pydantic import BaseModel

from folio_upm.model.eureka.role import Role
from folio_upm.model.report.detailed_http_error import DetailedHttpError


class HttpRequestResult(BaseModel):

    status: str
    srcEntityName: Optional[str] = None
    srcEntityId: Optional[str] = None
    srcEntityDisplayName: Optional[str] = None
    tarEntityName: Optional[str] = None
    tarEntityId: Optional[str] = None
    tarEntityDisplayName: Optional[str] = None
    reason: Optional[str] = None
    error: Optional[DetailedHttpError] = None

    @staticmethod
    def for_role(role, status, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role",
            srcEntityId=role.name,
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_removed_role(role_id: str, status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role",
            srcEntityId=role_id,
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability(role: Role, capability_id: str, status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role-capability",
            srcEntityId=f"Role: '{role.name}' -> {role.id}\nCapability: {capability_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capabilities(role, capability_ids: List[str], status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role-capabilities",
            srcEntityId=f"Role: '{role.name}' -> {role.id}\nCapabilities: {capability_ids}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability_set(role, set_id: str, status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role-capability-set",
            srcEntityId=f"Role: '{role.name}' -> {role.id}\nCapabilitySet: {set_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_capability_sets(role, set_ids: List[str], status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role-capability-sets",
            srcEntityId=f"Role: '{role.name}' -> {role.id}\nCapabilitySets: {set_ids}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_role_users(role, user_id: str, status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role-user",
            srcEntityId=f"Role: '{role.name}' -> {role.id}\nUser: {user_id}",
            reason=reason,
            error=error,
        )

    @staticmethod
    def role_not_found_result(role_name: str):
        return HttpRequestResult(
            status="not_matched",
            srcEntityName="role",
            srcEntityId=f"{role_name}",
            reason="Failed to find by name",
        )
