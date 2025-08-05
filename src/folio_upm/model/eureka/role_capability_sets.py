from typing import List

from pydantic import BaseModel


class RoleCapabilitySets(BaseModel):
    roleId: str
    capabilitySetId: List[str] = []
