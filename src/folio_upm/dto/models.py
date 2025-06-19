from typing import List, Optional, OrderedDict, Tuple

from pydantic import BaseModel, field_serializer

from folio_upm.utils.ordered_set import OrderedSet


class Permission(BaseModel):
    id: Optional[str] = None
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


class ModuleDescriptor(BaseModel):
    id: str
    name: str = None
    description: str = None
    permissionSets: List[Permission] = []


class ValueHolder(BaseModel):
    s: str
    v: List[str] | str | bool | None | Permission


class AnalyzedPermission(BaseModel):
    sources: List[str]
    permissionName: str
    mutable: List[ValueHolder] = False
    displayNames: List[ValueHolder] = []
    definedInOkapi: bool = False
    subPermissions: List[ValueHolder] = []
    parentPermissions: List[ValueHolder] = []
    flatSubPermissions: List[ValueHolder] = []
    okapiSubPermissions: List[ValueHolder] = []
    refPermissions: List[ValueHolder] = []

    @field_serializer("subPermissions", "parentPermissions", "flatSubPermissions", "okapiSubPermissions")
    def serialize_ordered_set(self, value: OrderedSet[str]) -> List[str]:
        return value.to_list()

    @field_serializer("refPermissions")
    def serialize_ref_permissions(self, value: List[Permission]) -> List[str] | None:
        return None


class LoadResult(BaseModel):
    okapiPermissions: List[ModuleDescriptor] = []
    allPermissions: List[Permission] = []
    allPermissionsExpanded: List[Permission] = []
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
    systemPermissions: List[Tuple[str, bool, bool]] = []


class RoleCapabilityHolder(BaseModel):
    capabilityPS: List[str] = []
    capabilitySetPS: List[str] = []


class AnalysisResult(BaseModel):
    permissionSets: OrderedDict[str, List[Permission]] = OrderedDict()
    flatPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    permissionSetsNesting: OrderedDict[str, List[str]] = OrderedDict()
    usersPermissionSets: OrderedDict[str, UserPermsHolder] = OrderedDict()
    permissionSetUsers: OrderedDict[str, List[str]] = OrderedDict()
    permissionPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    permissionFlatPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    roles: List[Role] = []
    roleUsers: OrderedDict[str, List[str]] = OrderedDict()
    rolePermissions: OrderedDict[str, List[str]] = OrderedDict()
    roleCapabilities: OrderedDict[str, RoleCapabilityHolder] = OrderedDict()
