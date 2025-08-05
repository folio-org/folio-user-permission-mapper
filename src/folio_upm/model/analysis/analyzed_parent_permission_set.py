from typing import List, Optional

from pydantic import BaseModel, field_serializer

from folio_upm.model.types.permission_type import PermissionType
from folio_upm.utils.ordered_set import OrderedSet


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
