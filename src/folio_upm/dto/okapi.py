from typing import Optional, List

from pydantic import BaseModel


class Permission(BaseModel):
    id: Optional[str] = None
    permissionName: str
    subPermissions: List[str] = []
    displayName: Optional[str] = None
    description: Optional[str] = None
    mutable: bool = False
    deprecated: bool = False
    moduleName: Optional[str] = None
    moduleVersion: Optional[str] = None
    childOf: List[str] = []
    grantedTo: List[str] = []
    assignedUserIds: List[str] = []


class ModuleDescriptor(BaseModel):
    id: str
    name: str = None
    description: str = None
    permissionSets: List[Permission] = []
