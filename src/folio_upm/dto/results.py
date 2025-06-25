from typing import List, Optional, OrderedDict as OrdDict
from collections import OrderedDict

from pydantic import BaseModel

from folio_upm.dto.eureka import Capability, CapabilitySet, Role, RoleUsers, UserPermission
from folio_upm.dto.okapi import ModuleDescriptor, PermissionSet
from folio_upm.dto.support import AnalyzedPermissionSet, RoleCapabilities, UserPermsHolder, AnalyzedRole
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
    mutablePermissionSets: OrdDict[str, List[PermissionSet]] = OrderedDict()
    flatPermissionSets: OrdDict[str, List[str]] = OrderedDict()
    permissionSetsNesting: OrdDict[str, List[str]] = OrderedDict()
    usersPermissionSets: OrdDict[str, UserPermsHolder] = OrderedDict()
    permissionSetUsers: OrdDict[str, List[str]] = OrderedDict()
    permissionPermissionSets: OrdDict[str, List[str]] = OrderedDict()
    permissionFlatPermissionSets: OrdDict[str, List[str]] = OrderedDict()
    roles: OrdDict[str, AnalyzedRole] = OrderedDict[str, AnalyzedRole] ()
    roleUsers: List[RoleUsers] = list[RoleUsers]()
    roleCapabilities: List[RoleCapabilities] = list[RoleCapabilities]()
