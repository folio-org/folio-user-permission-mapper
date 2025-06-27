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
    def for_role(role: Role, status: str, reason: str | None = None, error: HttpReqErr | None = None) -> "EntityMigrationResult":
        return EntityMigrationResult(
            status=status,
            entityName="role",
            entityId=role.id,
            reason=reason,
            error=error,
        )
