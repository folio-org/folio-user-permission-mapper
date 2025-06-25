from typing import List, Optional, Tuple, Callable

from pydantic import BaseModel

from folio_upm.dto.eureka import Role
from folio_upm.dto.okapi import PermissionSet
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
    val: PermissionSet


class AnalyzedPermissionSet(BaseModel):
    note: Optional[str] = None
    reasons: List[str] = []
    permissionName: str = None
    values: List[SourcedPermissionSet] = []

    def get_first_value(self, value_extractor: Callable[[PermissionSet], str]) -> Optional[str]:
        extracted_values = [value_extractor(i.val) for i in self.values]
        return extracted_values[0] if len(extracted_values) > 1 else None


class AnalyzedRole(BaseModel):
    role: Role
    src: str
