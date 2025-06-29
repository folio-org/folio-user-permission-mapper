from collections import OrderedDict
from typing import List, Optional
from typing import OrderedDict as OrdDict

from pydantic import BaseModel, field_serializer

from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.dto.eureka import Capability, CapabilitySet, Role, RoleUsers, UserPermission
from folio_upm.dto.okapi import ModuleDescriptor, PermissionSet
from folio_upm.dto.support import AnalyzedPermissionSet, ExpandedPermissionSet, RoleCapabilitiesHolder
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

    def __getitem__(self, key: str) -> Optional[OrdDict[str, "AnalyzedPermissionSet"]]:
        if key not in self._all_types:
            return OrderedDict()
        return getattr(self, key)

    def identify_permission_type(self, ps_name: str) -> Optional[str]:
        for ps_type in self._all_types:
            if ps_name in getattr(self, ps_type):
                return ps_type
        return "unknown"

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
    users: OrderedSet[str]
    permissionSets: List[ExpandedPermissionSet]
    source: str
    systemGenerated: bool
    originalPermissionsCount: int
    totalPermissionsCount: int

    def get_assigned_users_count(self) -> int:
        return len(self.users)

    def get_total_permissions_count(self) -> int:
        return len(self.permissionSets)

    @field_serializer("users")
    def serialize_ordered_set(self, value: OrderedSet[str]) -> List[str]:
        return list(value)


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


class AnalyzedParentPermSets(BaseModel):
    permissionName: str
    permissionType: str
    displayName: Optional[str] = None
    parentPermissionName: str
    parentDisplayName: Optional[str] = None
    parentPsTypes: OrderedSet[str]
    parentPsSources: OrderedSet[str]

    def get_parent_types_str(self):
        return ", ".join(sorted(self.parentPsTypes)) or "not found"

    def get_parent_sources_str(self):
        return ", ".join(sorted(self.parentPsSources))

    @field_serializer("parentPsTypes", "parentPsSources")
    def serialize_ordered_set(self, value: OrderedSet[str]) -> List[str]:
        return list(value)


class AnalyzedUserPermissionSet(BaseModel):
    userId: str
    psName: str
    psType: Optional[str]


class AnalyzedRoleCapabilities(BaseModel):
    roleId: str
    psNames: List[str] = list[str]()
    capabilityNames: List[str] = list[str]()
    capabilitySetNames: List[str] = list[str]()


class AnalysisResult(BaseModel):
    psStatistics: List[PsStatistics]
    userStatistics: List[UserStatistics]
    userPermissionSets: List[AnalyzedUserPermissionSet]
    permSetNesting: List[AnalyzedParentPermSets]
    roles: OrdDict[str, AnalyzedRole]
    roleUsers: List[RoleUsers]
    roleCapabilities: List[RoleCapabilitiesHolder]


class EurekaMigrationResult(BaseModel):
    roles: List[EntityMigrationResult] = []
    roleUsers: List[EntityMigrationResult] = []
    roleCapabilities: List[EntityMigrationResult] = []
