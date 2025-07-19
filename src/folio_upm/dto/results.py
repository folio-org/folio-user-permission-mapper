from typing import Dict, List, Optional

from pydantic import BaseModel, field_serializer

from folio_upm.dto.eureka import (
    Capability,
    CapabilitySet,
    Role,
    RoleCapability,
    RoleCapabilitySet,
    UserPermission,
    UserRole,
    UserRoles,
)
from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.dto.okapi import ModuleDescriptor, PermissionSet
from folio_upm.dto.permission_type import SUPPORTED_PS_TYPES, PermissionType
from folio_upm.dto.support import AnalyzedPermissionSet, ExpandedPermissionSet, RoleCapabilitiesHolder
from folio_upm.utils.ordered_set import OrderedSet


class OkapiLoadResult(BaseModel):
    okapiPermissions: List[ModuleDescriptor] = []
    allPermissions: List[PermissionSet] = []
    allPermissionsExpanded: List[PermissionSet] = []
    allPermissionUsers: List[UserPermission] = []


class EurekaLoadResult(BaseModel):
    roles: List[Role] = []
    roleCapabilities: List[RoleCapability] = []
    roleCapabilitySets: List[RoleCapabilitySet] = []
    roleUsers: List[UserRole] = []
    capabilities: List[Capability] = []
    capabilitySets: List[CapabilitySet] = []


class PermissionAnalysisResult(BaseModel):
    mutable: Dict[str, AnalyzedPermissionSet] = {}
    okapi: Dict[str, AnalyzedPermissionSet] = {}
    invalid: Dict[str, AnalyzedPermissionSet] = {}
    deprecated: Dict[str, AnalyzedPermissionSet] = {}
    questionable: Dict[str, AnalyzedPermissionSet] = {}
    unprocessed: Dict[str, AnalyzedPermissionSet] = {}
    systemPermissionNames: OrderedSet[str] = []

    def __getitem__(self, ps_type: PermissionType) -> Optional[Dict[str, "AnalyzedPermissionSet"]]:
        if ps_type not in SUPPORTED_PS_TYPES:
            return {}
        return getattr(self, ps_type.get_name())

    def identify_permission_type(self, ps_name: str) -> PermissionType:
        for ps_type in SUPPORTED_PS_TYPES:
            key = ps_type.get_name()
            if ps_name in getattr(self, key):
                return PermissionType.from_string(key)
        return PermissionType.UNKNOWN

    @staticmethod
    def get_supported_types() -> List[PermissionType]:
        return SUPPORTED_PS_TYPES


class UserStatistics(BaseModel):
    userId: str
    mutablePermissionSetsCount: int
    okapiPermissionSetsCount: int
    invalidPermissionSetsCount: int
    deprecatedPermissionSetsCount: int
    allPermissionSetsCount: int


class AnalyzedRole(BaseModel):
    role: Role
    permissionSets: List[ExpandedPermissionSet]
    source: str
    users: OrderedSet[str]
    usersCount: int = 0
    systemGenerated: bool = False
    capabilitiesCount: int = 0
    originalPermissionsCount: int = 0
    expandedPermissionsCount: int = 0

    def get_total_permissions_count(self) -> int:
        return len(self.permissionSets)

    @field_serializer("users")
    def serialize_ordered_set(self, value: OrderedSet[str]) -> List[str]:
        return list(value)


class PsStatistics(BaseModel):
    name: str
    displayNames: List[str]
    permissionType: str = None
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

    def get_permission_type_name(self) -> str:
        return PermissionType.from_string(self.permissionType).get_visible_name()


class AnalyzedParentPermSets(BaseModel):
    permissionName: str
    permissionType: str = None
    displayName: Optional[str] = None
    parentPermissionName: str
    parentDisplayName: Optional[str] = None
    parentPsTypes: OrderedSet[str]
    parentPsSources: OrderedSet[str]

    def get_parent_types_str(self):
        sorted_types = sorted(self.parentPsTypes)
        visible_parent_types = [PermissionType.from_string(p).get_visible_name() for p in sorted_types]
        return ", ".join(visible_parent_types) or "not found"

    def get_parent_sources_str(self):
        return ", ".join(sorted(self.parentPsSources))

    def get_permission_type_name(self) -> str:
        return PermissionType.from_string(self.permissionType).get_visible_name()

    @field_serializer("parentPsTypes", "parentPsSources")
    def serialize_ordered_set(self, value: OrderedSet[str]) -> List[str]:
        return list(value)


class AnalyzedUserPermissionSet(BaseModel):
    userId: str
    permissionName: str
    displayName: Optional[str] = None
    permissionType: Optional[str] = None

    def get_permission_type_name(self) -> str:
        return PermissionType.from_string(self.permissionType).get_visible_name()


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
    roles: Dict[str, AnalyzedRole]
    roleUsers: List[UserRoles]
    roleCapabilities: List[RoleCapabilitiesHolder]


class PreparedEurekaData(BaseModel):
    roles: List[AnalyzedRole]
    roleUsers: List[UserRoles]
    roleCapabilities: List[RoleCapabilitiesHolder]


class EurekaMigrationResult(BaseModel):
    roles: List[EntityMigrationResult]
    roleUsers: List[EntityMigrationResult]
    roleCapabilities: List[EntityMigrationResult]


class EurekaCleanUpResult(BaseModel):
    roles: List[EntityMigrationResult]
    roleCapabilities: List[EntityMigrationResult]
