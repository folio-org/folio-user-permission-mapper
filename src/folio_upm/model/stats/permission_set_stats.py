from typing import List, Optional

from pydantic import BaseModel

from folio_upm.model.types.permission_type import PermissionType


class PermissionSetStats(BaseModel):
    name: str
    displayNames: List[str]
    permissionType: Optional[str] = None
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
