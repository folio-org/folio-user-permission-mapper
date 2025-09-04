from typing import List

from pydantic import BaseModel


class RoleCapabilities(BaseModel):
    roleId: str
    capabilityIds: List[str] = []
