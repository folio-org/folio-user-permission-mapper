from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from folio_upm.dto.eureka import RoleUsers, UserRoles


class CleanUpType(Enum):
    KEEP = "keep"
    REMOVE = "remove"

    @staticmethod
    def from_string(value: Optional[str]) -> Optional["CleanUpType"]:
        if value is None:
            return None
        value_to_find = value.upper()
        if value_to_find in CleanUpType.__members__:
            return CleanUpType[value_to_find]
        return None

    def get_name(self) -> str:
        return self.value[0]


KEEP = CleanUpType.KEEP
REMOVE = CleanUpType.REMOVE


class UserCapabilities(BaseModel):
    allCapabilities: List[str] = []
    allCapabilitySets: List[str] = []
    roleCapabilities: List[str] = []
    roleCapabilitySets: List[str] = []
    hashRoleCapabilities: List[str] = []
    hashRoleCapabilitySets: List[str] = []


class EurekaRoleCapability(BaseModel):
    roleId: str
    roleName: str
    c_type: str
    capabilityId: str
    name: str
    resource: str
    action: str
    capabilityType: str


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


class EurekaRoleStats(BaseModel):
    roleId: str
    roleName: str
    isHashRole: bool = False
    totalUsers: int
    capabilitiesNum: int
    capabilitySetsNum: int


class CleanUpRole(BaseModel):
    roleId: str
    roleName: str
    isHashRole: bool = False
    type: CleanUpType = CleanUpType.KEEP


class HashRolesAnalysisResult(BaseModel):
    userStats: List[EurekaUserStats]
    roleStats: List[EurekaRoleStats]
    userRoles: List[UserRoles]
    roleCapabilities: List[EurekaRoleCapability]
