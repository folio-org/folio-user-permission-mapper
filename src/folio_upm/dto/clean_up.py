from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel


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


class UserCapabilities(BaseModel):
    allCapabilities: List[str] = []
    allCapabilitySets: List[str] = []
    roleCapabilities: List[str] = []
    roleCapabilitySets: List[str] = []
    hashRoleCapabilities: List[str] = []
    hashRoleCapabilitySets: List[str] = []

class EurekaUserStats(BaseModel):
    userId: str
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

class CleanUpRoleCapability(BaseModel):
    roleId: str
    roleName: str
    capabilityId: str
    type: CleanUpType = CleanUpType.KEEP

class CleanUpRoleCapabilitySet(BaseModel):
    roleId: str
    roleName: str
    capabilitySetId: str
    type: CleanUpType = CleanUpType.KEEP

class HashRolesAnalysisResult(BaseModel):
    userStats: List[EurekaUserStats]
    roleStats: List[EurekaRoleStats]
    roles: List[CleanUpRole]
    roleCapabilities: List[CleanUpRoleCapability]
    roleCapabilitySets: List[CleanUpRoleCapabilitySet]


class EurekaCleanUpData(BaseModel):
    roles: List[CleanUpRole] = []
    roleCapabilities: List[CleanUpRoleCapability] = []
    roleCapabilitySets: List[CleanUpRoleCapabilitySet] = []

KEEP = CleanUpType.KEEP
REMOVE = CleanUpType.REMOVE
