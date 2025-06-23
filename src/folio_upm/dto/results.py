from typing import List, Optional, OrderedDict

from pydantic import BaseModel

from folio_upm.dto.eureka import Capability, CapabilitySet, Role, RoleUsers, UserPermission
from folio_upm.dto.okapi import ModuleDescriptor, Permission
from folio_upm.dto.support import AnalyzedPermission, RoleCapabilities, UserPermsHolder
from folio_upm.utils.ordered_set import OrderedSet


class LoadResult(BaseModel):
    okapiPermissions: List[ModuleDescriptor] = []
    allPermissions: List[Permission] = []
    allPermissionsExpanded: List[Permission] = []
    allPermissionUsers: List[UserPermission] = []


class EurekaLoadResult(BaseModel):
    capabilities: List[Capability] = []
    capabilitySets: List[CapabilitySet] = []


class PermissionAnalysisResult(BaseModel):
    mutable: OrderedDict[str, AnalyzedPermission] = OrderedDict()
    okapi: OrderedDict[str, AnalyzedPermission] = OrderedDict()
    invalid: OrderedDict[str, AnalyzedPermission] = OrderedDict()
    deprecated: OrderedDict[str, AnalyzedPermission] = OrderedDict()
    questionable: OrderedDict[str, AnalyzedPermission] = OrderedDict()
    unprocessed: OrderedDict[str, AnalyzedPermission] = OrderedDict()
    systemPermissionNames: OrderedSet[str] = []

    def identify_permission(self, ps_name: str) -> Optional[str]:
        """
        Returns a tuple of permission name and its source type.
        If the permission is not found, returns an empty string and the source type.
        """
        if ps_name in self.mutable:
            return "mutable"
        if ps_name in self.okapi:
            return "okapi"
        if ps_name in self.invalid:
            return "invalid"
        if ps_name in self.deprecated:
            return "deprecated"
        if ps_name in self.questionable:
            return "questionable"
        if ps_name in self.unprocessed:
            return "unprocessed"
        if ps_name in self.systemPermissionNames:
            return "system"
        return None


class UserStatistics(BaseModel):
    userId: str
    mutablePermissionSetsCount: int = 0
    invalidPermissionSetsCount: int = 0
    okapiPermissionSetsCount: int = 0
    deprecatedPermissionSetsCount: int = 0
    allPermissionSetsCount: int = 0


class AnalysisResult(BaseModel):
    userStatistics: List[UserStatistics] = list[UserStatistics]()
    permsAnalysisResult: PermissionAnalysisResult = None
    mutablePermissionSets: OrderedDict[str, List[Permission]] = OrderedDict()
    flatPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    permissionSetsNesting: OrderedDict[str, List[str]] = OrderedDict()
    usersPermissionSets: OrderedDict[str, UserPermsHolder] = OrderedDict()
    permissionSetUsers: OrderedDict[str, List[str]] = OrderedDict()
    permissionPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    permissionFlatPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    roles: List[Role] = list[Role]()
    roleUsers: List[RoleUsers] = list[RoleUsers]()
    roleCapabilities: List[RoleCapabilities] = list[RoleCapabilities]()
