from typing import Callable, List, Optional, Tuple

from pydantic import BaseModel

from folio_upm.dto.okapi import PermissionSet
from folio_upm.dto.permission_type import PermissionType
from folio_upm.dto.source_type import SourceType
from folio_upm.utils.ordered_set import OrderedSet


class UserPermsHolder(BaseModel):
    mutablePermissions: List[str] = []
    systemPermissions: List[Tuple[str, bool, bool]] = []


class CapabilityPlaceholder(BaseModel):
    resolvedType: str
    permissionName: str
    permissionType: Optional[str]
    displayName: Optional[str] = None
    expandedFrom: List[str] = []
    name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    capabilityType: Optional[str] = None

    def get_permission_type_name(self) -> str:
        return PermissionType.from_string(self.permissionType).get_visible_name()


class RoleCapabilitiesHolder(BaseModel):
    roleName: str
    capabilities: List[CapabilityPlaceholder]


class SourcedPermissionSet(BaseModel):
    src: SourceType
    val: PermissionSet


class ExpandedPermissionSet(BaseModel):
    permissionName: str
    expandedFrom: List[str] = []


class AnalyzedPermissionSet(BaseModel):
    note: Optional[str] = None
    reasons: List[str] = []
    permissionName: str = None
    sourcePermSets: List[SourcedPermissionSet] = []

    def get_first_value(self, value_extractor: Callable[[PermissionSet], str]) -> Optional[str]:
        extracted_values = [value_extractor(i.val) for i in self.sourcePermSets]
        return extracted_values[0] if len(extracted_values) > 1 else None

    def get_parent_permission_names(self) -> OrderedSet[str]:
        parent_permissions = OrderedSet[str]()
        for source_perm_set in self.sourcePermSets:
            if source_perm_set.val.childOf:
                parent_permissions.add_all(source_perm_set.val.childOf)
        return parent_permissions

    def get_sub_permissions(self, include_flat: bool = False) -> OrderedSet[str]:
        sub_permissions = OrderedSet()
        if include_flat:
            for source_perm_set in self.sourcePermSets:
                if source_perm_set.src == SourceType.FLAT_PS:
                    sub_permissions.add_all(source_perm_set.val.subPermissions)
            return sub_permissions

        for source_perm_set in self.sourcePermSets:
            source = source_perm_set.src
            if source == SourceType.PS or source == SourceType.OKAPI_PS:
                sub_permissions += source_perm_set.val.subPermissions
        return sub_permissions

    def get_uq_display_names_str(self) -> str:
        names = OrderedSet[str]([x.val.displayName for x in self.sourcePermSets if x.val.displayName]).to_list()
        return "\n".join(sorted(names))
