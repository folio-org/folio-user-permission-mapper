from collections import OrderedDict

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integrations.permissions_client import PermissionsClient
from folio_upm.utils import common_utils, env, log_factory

_log = log_factory.get_logger(__name__)


class PermissionService(metaclass=SingletonMeta):

    def __init__(self):
        self._permissions_client = PermissionsClient()

    def load_all_permissions_by_query(self, query: str, expanded=False):
        _log.info(f"Loading all permissions by query: expanded={expanded}, query='{query}'")
        result = []
        limit = 500
        last_offset = 0

        while True:
            page = self._permissions_client.load_perms_page(limit, last_offset, query, expanded)
            last_load_size = len(page)
            result += page
            last_offset += limit
            if last_load_size < limit:
                _log.info(f"All permissions loaded: total={len(result)}")
                break

        return result

    def load_permission_users(self, permissions):
        _log.info("Loading permission users...")
        all_granted_to = []
        for permission in permissions:
            granted_to_coll = permission.get("grantedTo", [])
            all_granted_to += granted_to_coll
        uniqueValues = list(OrderedDict.fromkeys(all_granted_to).keys())
        batch_size = int(env.require_env("PERMISSION_IDS_PARTITION_SIZE", default_value=50, log_result=False))
        partitioned_values = common_utils.partition(uniqueValues, batch_size)
        result = []
        for partition_ids in partitioned_values:
            perm_users = self._permissions_client.load_user_permissions_by_id(partition_ids)
            result += perm_users
        _log.info(f"Permission users are loaded: total={len(result)}")
        return result

    @staticmethod
    def enrich_permissions(permissions, permission_users):
        permission_users_map = {}
        for permission_user in permission_users:
            user_id = permission_user.get("userId")
            permission_users_map[permission_user.get("id")] = user_id

        for permission in permissions:
            granted_to_coll = permission.get("grantedTo", [])
            assigned_user_ids = []
            for granted_to in granted_to_coll:
                resolved_user_id = permission_users_map.get(granted_to, None)
                if resolved_user_id:
                    assigned_user_ids.append(resolved_user_id)
                else:
                    _log.warning(f"User ID not found for grantedTo: {granted_to}")
            permission["assignedUserIds"] = assigned_user_ids
        return permissions
