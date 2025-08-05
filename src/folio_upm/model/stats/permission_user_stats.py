from pydantic import BaseModel


class PermissionUserStats(BaseModel):
    userId: str
    mutablePermissionSetsCount: int
    okapiPermissionSetsCount: int
    invalidPermissionSetsCount: int
    deprecatedPermissionSetsCount: int
    allPermissionSetsCount: int
