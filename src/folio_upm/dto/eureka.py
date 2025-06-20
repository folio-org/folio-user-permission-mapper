from typing import Optional, List

from pydantic import BaseModel


class Role(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    source: str


class Endpoint(BaseModel):
    path: str
    method: str


class UserRoles(BaseModel):
    userId: str
    roleId: str


class RoleUsers(BaseModel):
    roleId: str
    userIds: List[str] = []


class Capability(BaseModel):
    id: str
    name: str
    description: Optional[str]
    resource: str
    action: str
    applicationId: str
    moduleId: str
    permission: str
    endpoints: List[Endpoint] = []
    dummyCapability: bool
    type: str
    visible: bool


class CapabilitySet(BaseModel):
    id: str
    name: str
    description: Optional[str]
    resource: str
    action: str
    applicationId: str
    moduleId: str
    permission: str
    capabilities: Optional[List[str]] = []
    type: str
    visible: bool


class UserPermission(BaseModel):
    id: str
    userId: str
    permissions: List[str] = []
