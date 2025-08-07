from typing import Optional

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
    def role_not_found_result(role_name: str):
        return HttpRequestResult(
            status="not_matched",
            srcEntityName="role",
            srcEntityId=f"{role_name}",
            reason="Failed to find by name",
        )

    @staticmethod
    def for_user_role(role: Role, user_id: str, status: str, reason=None, error=None):
        return HttpRequestResult(
            status=status,
            srcEntityName="role-user",
            srcEntityId=role.id,
            srcEntityDisplayName=role.name,
            tarEntityName="user",
            tarEntityId=user_id,
            reason=reason,
            error=error,
        )
