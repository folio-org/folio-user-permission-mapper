from pydantic import BaseModel


class EurekaUserStats(BaseModel):
    userId: str
    hashRoles: int
    totalRoles: int
    allCapabilities: int
    allCapabilitySets: int
    roleCapabilities: int
    roleCapabilitySets: int
    hashRoleCapabilities: int
    hashRoleCapabilitySets: int
