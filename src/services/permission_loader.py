from collections import OrderedDict
from typing import OrderedDict as OrdDict

from services import okapi_service, permission_service
from utils import log_factory

_log = log_factory.get_logger(__name__)


def load_permission_data() -> OrdDict[str, any]:
    _log.info("Starting permission data loading...")
    okapi_permissions = okapi_service.get_okapi_defined_permissions()
    all_perms = permission_service.load_all_permissions_by_query("cql.allRecords=1", expanded=False)
    all_perms_expanded = permission_service.load_all_permissions_by_query("cql.allRecords=1", expanded=True)
    all_perm_users = permission_service.load_permission_users(all_perms)
    all_perms_enriched = permission_service.enrich_permissions(all_perms, all_perm_users)

    _log.info("Permissions are loaded successfully.")
    return OrderedDict(
        {
            "okapiPermissions": okapi_permissions,
            "allPermissions": all_perms_enriched,
            "allPermissionsExpanded": all_perms_expanded,
            "allPermissionUsers": all_perm_users,
        }
    )
