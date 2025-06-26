from collections import OrderedDict
from typing import List, Optional, Tuple
from typing import OrderedDict as OrdDict

from pydantic import BaseModel

from folio_upm.dto.eureka import Capability, CapabilitySet, Role, UserPermission
from folio_upm.dto.okapi import ModuleDescriptor, PermissionSet
from folio_upm.dto.support import AnalyzedPermissionSet, UserPermsHolder
from folio_upm.utils.ordered_set import OrderedSet


class LoadResult(BaseModel):
    okapiPermissions: List[ModuleDescriptor] = []
    allPermissions: List[PermissionSet] = []
    allPermissionsExpanded: List[PermissionSet] = []
    allPermissionUsers: List[UserPermission] = []


class EurekaLoadResult(BaseModel):
    capabilities: List[Capability] = []
    capabilitySets: List[CapabilitySet] = []


class PermissionAnalysisResult(BaseModel):
    mutable: OrdDict[str, AnalyzedPermissionSet] = OrderedDict()
    okapi: OrdDict[str, AnalyzedPermissionSet] = OrderedDict()
    invalid: OrdDict[str, AnalyzedPermissionSet] = OrderedDict()
    deprecated: OrdDict[str, AnalyzedPermissionSet] = OrderedDict()
    questionable: OrdDict[str, AnalyzedPermissionSet] = OrderedDict()
    unprocessed: OrdDict[str, AnalyzedPermissionSet] = OrderedDict()
    systemPermissionNames: OrderedSet[str] = []
    _all_types: List[str] = ["mutable", "invalid", "deprecated", "questionable", "unprocessed", "okapi"]

    def __getitem__(self, key: str) -> OrdDict[str, "AnalyzedPermissionSet"]:
        return getattr(self, key)

    def identify_permission_type(self, ps_name: str) -> Optional[str]:
        for ps_type in self._all_types:
            if ps_name in getattr(self, ps_type):
                return ps_type
        return None

    def get_types(self):
        return self._all_types


class UserStatistics(BaseModel):
    userId: str
    mutablePermissionSetsCount: int
    invalidPermissionSetsCount: int
    okapiPermissionSetsCount: int
    deprecatedPermissionSetsCount: int
    allPermissionSetsCount: int


class AnalyzedRole(BaseModel):
    role: Role
    users: List[str] = list[str]()
    source: str
    excluded: bool = False
    assignedUsersCount: int
    permissionsCount: int
    flatPermissionsCount: int
    totalPermissionsCount: int


class PsStatistics(BaseModel):
    name: str
    displayNames: List[str]
    type: str
    uniqueSources: List[str]
    refCount: int
    note: Optional[str]
    reasons: List[str]
    subPermsCount: int
    flatPermCount: int
    parentPermsCount: int
    uniqueModules: List[str]

    def get_uq_sources_num(self):
        return len(self.uniqueSources)

    def get_uq_sources_str(self):
        return ", ".join(sorted(self.uniqueSources))

    def get_reasons_str(self):
        return "\n".join(sorted(self.reasons))

    def get_uq_modules_str(self) -> str:
        return "\n".join(sorted(self.uniqueModules))

    def get_uq_display_names_str(self) -> str:
        return "\n".join(sorted(self.displayNames))


class AnalyzedPermSetPermSets(BaseModel):
    permissionName: str
    permissionType: str
    parentPermissionName: str
    parentPermissionTypes: List[str]


class AnalyzedUserPermissionSet(BaseModel):
    userId: str
    psName: str
    psType: str


class AnalyzedRoleUsers(BaseModel):
    roleId: str
    users: List[str] = list[str]()


class AnalyzedRoleCapabilities(BaseModel):
    roleId: str
    psNames: List[str] = list[str]()
    capabilityNames: List[str] = list[str]()
    capabilitySetNames: List[str] = list[str]()


class AnalysisResult(BaseModel):
    psStatistics: List[PsStatistics]
    userStatistics: List[UserStatistics]
    userPermissionSets: List[AnalyzedUserPermissionSet]
    permSetNesting: List[AnalyzedPermSetPermSets]
    roles: OrdDict[str, AnalyzedRole] = []
    roleUsers: List[AnalyzedRoleUsers] = []
    roleCapabilities: List[AnalyzedRoleCapabilities] = []

    permsAnalysisResult: PermissionAnalysisResult = None
    mutablePermissionSets: OrdDict[str, List[PermissionSet]] = OrderedDict()
    flatPermissionSets: OrdDict[str, List[str]] = OrderedDict()
    permissionSetsNesting: OrdDict[str, List[str]] = OrderedDict()
    usersPermissionSets: OrdDict[str, UserPermsHolder] = OrderedDict()
    permissionSetUsers: OrdDict[str, List[str]] = OrderedDict()
    permissionPermissionSets: OrdDict[str, List[str]] = OrderedDict()
    permissionFlatPermissionSets: OrdDict[str, List[str]] = OrderedDict()
