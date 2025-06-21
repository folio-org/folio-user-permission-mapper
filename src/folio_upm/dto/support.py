from typing import List, Tuple, Optional

from pydantic import BaseModel

from folio_upm.dto.okapi import Permission
from folio_upm.dto.source_type import SourceType


class UserPermsHolder(BaseModel):
    mutablePermissions: List[str] = []
    systemPermissions: List[Tuple[str, bool, bool]] = []


class RoleCapabilities(BaseModel):
    roleId: str
    capabilityPS: List[str] = []
    capabilitySetPS: List[str] = []


class SourcedPermissionSet(BaseModel):
    src: SourceType
    val: Permission


class AnalyzedPermission(BaseModel):
    note: Optional[str] = None
    reasons: List[str] = []
    permissionName: str = None
    values: List[SourcedPermissionSet] = []
