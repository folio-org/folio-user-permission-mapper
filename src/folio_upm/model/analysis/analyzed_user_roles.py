from typing import List

from pydantic import BaseModel


class AnalyzedUserRoles(BaseModel):
    userId: str
    skipRoleAssignment: bool = False
    roleNames: List[str] | None = []
