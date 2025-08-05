from pydantic import BaseModel


class EurekaRoleStats(BaseModel):
    roleId: str
    roleName: str
    isHashRole: bool = False
    totalUsers: int
    capabilitiesNum: int
    capabilitySetsNum: int
