from typing import List

from pydantic import BaseModel

from folio_upm.model.okapi.module_descriptor import ModuleDescriptor
from folio_upm.model.okapi.permission_set import PermissionSet
from folio_upm.model.okapi.user_permission import UserPermission


class OkapiLoadResult(BaseModel):
    okapiPermissions: List[ModuleDescriptor] = []
    allPermissions: List[PermissionSet] = []
    allPermissionsExpanded: List[PermissionSet] = []
    allPermissionUsers: List[UserPermission] = []
