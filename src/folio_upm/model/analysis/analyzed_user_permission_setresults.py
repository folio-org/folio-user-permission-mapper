from typing import Optional

from pydantic import BaseModel

from folio_upm.model.types.permission_type import PermissionType


class AnalyzedUserPermissionSet(BaseModel):
    userId: str
    permissionName: str
    displayName: Optional[str] = None
    permissionType: Optional[str] = None

    def get_permission_type_name(self) -> str:
        return PermissionType.from_string(self.permissionType).get_visible_name()
