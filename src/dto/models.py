from typing import List, Optional, OrderedDict

from pydantic import BaseModel


class Permission(BaseModel):
    permissionName: str
    subPermissions: List[str] = []
    displayName: Optional[str] = None
    description: Optional[str] = None
    mutable: bool = False
    childOf: List[str] = []
    grantedTo: List[str] = []
    assignedUserIds: List[str] = []


class UserPermission(BaseModel):
    id: str
    userId: str
    permissions: List[str] = []


class OkapiPermission(BaseModel):
    id: str
    name: str = None
    description: str = None
    permissionSets: List[Permission] = []


class LoadResult(BaseModel):
    okapiPermissions: List[OkapiPermission] = []
    allPermissions: List[Permission] = []
    allPermissionUsers: List[UserPermission] = []


class Role(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    source: str


class UserRoles(BaseModel):
    userId: str
    roleId: str


class Endpoint(BaseModel):
    path: str
    method: str


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


class UserPermsHolder(BaseModel):
    mutablePermissions: List[str] = []
    systemPermissions: List[str] = []


class AnalysisResult(BaseModel):
    permissionSets: OrderedDict[str, Permission] = OrderedDict()
    flatPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    permissionSetsNesting: OrderedDict[str, List[str]] = OrderedDict()
    usersPermissionSets: OrderedDict[str, UserPermsHolder] = OrderedDict()
    permissionSetUsers: OrderedDict[str, List[str]] = OrderedDict()
    permissionPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    roles: List[Role] = []
    roleUsers: OrderedDict[str, List[str]] = OrderedDict()
    rolePermissions: OrderedDict[str, List[str]] = OrderedDict()
    roleCapabilities: OrderedDict[str, List[str]] = OrderedDict()
    roleCapabilitySets: OrderedDict[str, List[str]] = OrderedDict()
