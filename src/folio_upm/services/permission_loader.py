from collections import OrderedDict
from typing import OrderedDict as OrdDict

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.services.okapi_service import OkapiService
from folio_upm.services.permission_service import PermissionService
from folio_upm.utils import log_factory

_log = log_factory.get_logger(__name__)


class PermissionLoader(metaclass=SingletonMeta):
    def __init__(self):
        self._ps_service = PermissionService()
        self._okapi_service = OkapiService()

    def load_permission_data(self) -> OrdDict[str, any]:
        _log.info("Permission loading started...")

        okapi_permissions = self._okapi_service.get_okapi_defined_permissions()
        all_perms = self._ps_service.load_all_permissions_by_query("cql.allRecords=1", expanded=False)
        all_perms_expanded = self._ps_service.load_all_permissions_by_query("cql.allRecords=1", expanded=True)
        all_perm_users = self._ps_service.load_permission_users(all_perms)
        all_perm_users_expanded = self._ps_service.load_permission_users(all_perms_expanded)

        _log.info("Permissions are loaded successfully.")
        return OrderedDict(
            {
                "okapiPermissions": okapi_permissions,
                "allPermissions": all_perms,
                "allPermissionsExpanded": all_perms_expanded,
                "allPermissionUsers": all_perm_users,
                "allPermissionUsersExpanded": all_perm_users_expanded,
            }
        )
