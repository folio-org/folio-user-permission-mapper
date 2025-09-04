from typing import Optional

from pydantic import BaseModel


class EurekaRoleStats(BaseModel):
    roleId: Optional[str] = None
    roleName: Optional[str] = None
    isHashRole: bool = False
    totalUsers: int = 0
    capabilitiesNum: int = 0
    capabilitySetsNum: int = 0
