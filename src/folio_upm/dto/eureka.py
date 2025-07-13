from typing import List, Optional

from pydantic import BaseModel, Field


class Role(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Endpoint(BaseModel):
    path: str
    method: str


class UserRole(BaseModel):
    userId: str
    roleId: str


class UserRoles(BaseModel):
    userId: str
    roles: List[str] | None = []


class RoleUsers(BaseModel):
    roleName: Optional[str]
    userIds: List[str]


class RoleCapability(BaseModel):
    roleId: str
    capabilityId: str


class RoleCapabilities(BaseModel):
    roleId: str
    capabilityIds: List[str] = []


class RoleCapabilitySet(BaseModel):
    roleId: str
    capabilitySetId: str


class RoleCapabilitySets(BaseModel):
    roleId: str
    capabilitySetId: List[str] = []


class Capability(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    applicationId: str
    moduleId: str
    permission: str
    endpoints: List[Endpoint] = []
    dummyCapability: bool
    capabilityType: str = Field(..., alias="type", serialization_alias="type")


class CapabilitySet(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    applicationId: str
    moduleId: str
    permission: str
    capabilities: Optional[List[str]] = []
    capabilityType: str = Field(..., alias="type", serialization_alias="type")


class UserPermission(BaseModel):
    id: str
    userId: str
    permissions: List[str] = []
