from typing import List

from pydantic import BaseModel


class RoleRelations(BaseModel):
    name: str
    userIds: List[str]
    permissionNames: List[str]
    capabilityNames: List[str]
