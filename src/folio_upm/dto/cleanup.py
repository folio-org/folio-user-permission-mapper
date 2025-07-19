from typing import List

from pydantic import BaseModel

from folio_upm.dto.eureka import Capability, CapabilitySet, Role, UserRoles


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


class CleanHashRole(BaseModel):
    role: Role
    capabilities: List[Capability]
    capabilitySets: List[CapabilitySet]


class HashRolesAnalysisResult(BaseModel):
    userStats: List[EurekaUserStats]
    roleStats: List[EurekaRoleStats]
    userRoles: List[UserRoles]
    roleCapabilities: List[EurekaRoleCapability]
    cleanHashRoles: List[CleanHashRole]
