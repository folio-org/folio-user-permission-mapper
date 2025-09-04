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
    def for_role(role: Optional[Role], status: str, reason=None, error=None) -> "HttpRequestResult":
        return HttpRequestResult(
            status=status,
            srcEntityName="role",
            srcEntityId=role.id if role else None,
            srcEntityDisplayName=role.name if role else None,
            reason=reason,
            error=error,
        )

    @staticmethod
    def for_removed_role(role_id: str, status: str, reason=None, error=None) -> "HttpRequestResult":
        return HttpRequestResult(
            status=status,
            srcEntityName="role",
            srcEntityId=role_id,
            reason=reason,
            error=error,
        )

    @staticmethod
    def user_role_not_found_result(user_id: str, role_name: str) -> "HttpRequestResult":
        return HttpRequestResult(
            status="not_found",
            srcEntityName="user",
            srcEntityId=user_id,
            tarEntityName="role",
            tarEntityDisplayName=role_name,
            reason="Role not found",
        )

    @staticmethod
    def role_capability_not_found_result(role_name: str) -> "HttpRequestResult":
        return HttpRequestResult(
            status="not_found",
            srcEntityName="role",
            srcEntityDisplayName=f"{role_name}",
            tarEntityName="capability | capability-set",
            reason="Role not found by name",
        )

    @staticmethod
    def for_user_role(role: Optional[Role], user_id: str, status: str, reason=None, error=None) -> "HttpRequestResult":
        return HttpRequestResult(
            status=status,
            srcEntityName="user",
            srcEntityId=user_id,
            tarEntityName="role",
            tarEntityId=role.id if role else None,
            tarEntityDisplayName=role.name if role else None,
            reason=reason,
            error=error,
        )
