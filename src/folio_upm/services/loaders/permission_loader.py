from typing import Dict

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.services.okapi_service import OkapiService
from folio_upm.integration.services.permission_service import PermissionService
from folio_upm.utils import log_factory


class PermissionLoader(metaclass=SingletonMeta):
    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._permission_service = PermissionService()
        self._okapi_service = OkapiService()

    def load_permission_data(self) -> Dict[str, any]:
        self._log.info("Permission loading started...")
        all_records_query = "cql.allRecords=1"
        pass

        okapi_permissions = self._okapi_service.get_okapi_defined_permissions()
        all_perms = self._permission_service.load_all_permissions_by_query(all_records_query, expanded=False)
        all_perms_expanded = self._permission_service.load_all_permissions_by_query(all_records_query, expanded=True)
        all_perm_users = self._permission_service.load_permission_users(all_perms)
        all_perm_users_expanded = self._permission_service.load_permission_users(all_perms_expanded)

        self._log.info("Permissions are loaded successfully.")
        return {
            "okapiPermissions": okapi_permissions,
            "allPermissions": all_perms,
            "allPermissionsExpanded": all_perms_expanded,
            "allPermissionUsers": all_perm_users,
            "allPermissionUsersExpanded": all_perm_users_expanded,
        }
