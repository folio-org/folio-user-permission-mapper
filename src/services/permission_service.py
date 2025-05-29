from collections import OrderedDict

from integrations import permissions_client
from utils import log_factory, env

_log = log_factory.get_logger(__name__)


def load_all_permissions_by_query(query):
    tenant_id = env.get_tenant_id()
    _log.info(f"Loading all permissions by query: tenant={tenant_id}, query='{query}'")
    result = []
    limit = 500
    last_offset = 0

    while True:
        page = permissions_client.load_perms_page(limit, last_offset, query)
        last_load_size = len(page)
        result += __convert_permissions(page)
        last_offset += limit
        if last_load_size < limit:
            _log.info(f"All permissions loaded: total={len(result)}")
            break

    return result


def load_permission_users(permissions):
    _log.info(f"Loading permission users...")
    all_granted_to = []
    for permission in permissions:
        granted_to_coll = permission.get('grantedTo', [])
        all_granted_to += granted_to_coll
    uniqueValues = list(OrderedDict.fromkeys(all_granted_to).keys())
    partitioned_values = __partition(uniqueValues, env.get_ids_partition_size())
    result = []
    for partition in partitioned_values:
        perm_users = permissions_client.load_user_permissions_by_id(partition)
        result += __convert_permission_users(perm_users)
    _log.info(f"Permission users are loaded: total={len(result)}")
    return result


def enrich_permissions(permissions, permission_users):
    permission_users_map = {}
    for permission_user in permission_users:
        user_id = permission_user.get('userId')
        permission_users_map[permission_user.get('id')] = user_id

    for permission in permissions:
        granted_to_coll = permission.get('grantedTo', [])
        assigned_user_ids = []
        for granted_to in granted_to_coll:
            resolved_user_id = permission_users_map.get(granted_to, None)
            if resolved_user_id:
                assigned_user_ids.append(resolved_user_id)
            else:
                _log.warning(f"User ID not found for grantedTo: {granted_to}")
        permission['assignedUserIds'] = assigned_user_ids
    return permissions


def __partition(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i: i + size]


def __convert_permissions(page):
    result = []
    for permission in page:
        result.append(OrderedDict({
            'permissionName': permission.get('permissionName'),
            'subPermissions': permission.get('subPermissions', []),
            'description': permission.get('description', ''),
            'mutable': permission.get('mutable', False),
            'childOf': permission.get('childOf', []),
            'grantedTo': permission.get('grantedTo', []),
        }))
    return result


def __convert_permission_users(page):
    result = []
    for permission_user in page:
        result.append(OrderedDict({
            'id': permission_user.get('id'),
            'userId': permission_user.get('userId'),
            'permissions': permission_user.get('permissions', []),
        }))
    return result
