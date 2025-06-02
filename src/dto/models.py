from typing import OrderedDict, List, Optional

from pydantic import BaseModel


class Permission(BaseModel):
    permissionName: str
    subPermissions: List[str] = []
    description: str = None
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


class AnalysisReport(BaseModel):
    okapiPermissions: List[OkapiPermission] = []
    allPermissions: List[Permission] = []
    allPermissionUsers: List[UserPermission] = []


class AnalysisResult(BaseModel):
    permissionSets: OrderedDict[str, Permission] = OrderedDict()
    permissionSetsNesting: OrderedDict[str, List[str]] = OrderedDict()
    usersPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
    permissionSetUsers: OrderedDict[str, List[str]] = OrderedDict()
    permissionPermissionSets: OrderedDict[str, List[str]] = OrderedDict()
