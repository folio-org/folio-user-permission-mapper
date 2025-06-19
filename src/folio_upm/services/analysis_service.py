import uuid
from collections import Counter, OrderedDict
from typing import List
from typing import OrderedDict as OrdDict
from typing import Set

from folio_upm.dto.models import (
    AnalysisResult,
    AnalyzedPermission,
    LoadResult,
    Permission,
    Role,
    RoleCapabilityHolder,
    UserPermsHolder,
)
from folio_upm.services.permission_analyzer import PermissionAnalyzer
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.service_utils import ServiceUtils

_log = log_factory.get_logger(__name__)


def analyze_results(analysis_json: dict, strategy: str = "distributed") -> AnalysisResult:
    report = LoadResult(**analysis_json)
    result = PermissionAnalyzer(report).get_analysis_result()

    all_ps = __get_all_ps_desc(report)
    mutable_ps = set([name for name, value in all_ps.items() if value.mutable])
    ps_nesting = __get_mutable_permission_set_nesting(report)
    user_permission_sets = __get_user_permission_sets(report, all_ps, mutable_ps)
    mutable_ps_users = __get_permission_set_users(report)

    roles = __create_roles(all_ps)

    return AnalysisResult(
        permissionSets=all_ps,
        flatPermissionSets=__get_flatten_ps_pss(report),
        permissionSetsNesting=ps_nesting,
        usersPermissionSets=user_permission_sets,
        permissionPermissionSets=permission_permission_sets,
        roles=roles,
        roleUsers=__create_role_users(roles, mutable_ps_users, strategy),
        roleCapabilities=__create_role_capabilities(roles, all_ps),
    )


def __get_all_ps_desc(report: LoadResult) -> OrdDict[str, List[Permission]]:
    result = OrderedDict()
    for permission in report.allPermissions:
        name = permission.permissionName
        if ServiceUtils.is_system_permission(permission.permissionName):
            continue
        value = result.get(permission.permissionName)
        if not value:
            result[permission.permissionName] = []
        result[name] += permission
    return result


def __get_mutable_permission_set_nesting(report: LoadResult) -> OrdDict[str, List[str]]:
    result = OrderedDict()
    for permission in report.allPermissions:
        if not permission.mutable:
            continue
        permission_name = permission.permissionName
        parent_permissions_names = permission.childOf
        result[permission_name] = []
        for parent_permission_name in parent_permissions_names:
            result[permission_name].append(parent_permission_name)
    return result


def __get_user_permission_sets(
    report: LoadResult, all_perms: OrdDict[str, Permission], mutable_perm_names: Set[str]
) -> OrdDict[str, UserPermsHolder]:
    result = OrderedDict()
    flat_ps_pss = __get_flatten_ps_pss(report)
    for permission_user in report.allPermissionUsers:
        uph = UserPermsHolder()
        user_id = permission_user.userId
        for permission in permission_user.permissions:
            if permission in mutable_perm_names:
                uph.mutablePermissions.append(permission)
        mutable_user_pss = set(uph.mutablePermissions)
        for permission in permission_user.permissions:
            if permission in mutable_perm_names or ServiceUtils.is_system_permission(permission):
                continue
            has_mutable_permission = __has_mutable_permission(permission, mutable_user_pss, flat_ps_pss)
            permission_exists = bool(all_perms.get(permission, None))
            uph.systemPermissions.append((permission, has_mutable_permission, permission_exists))
        result[user_id] = uph
    return result


def __get_perm_set_perm_sets(permissions: List[Permission]) -> OrdDict[str, List[str]]:
    result = OrderedDict()
    for permission in permissions:
        permission_name = permission.permissionName
        sub_permissions = permission.subPermissions
        if ServiceUtils.is_system_permission(permission_name):
            continue
        if not result.get(permission_name):
            result[permission_name] = []
        result[permission_name] += sub_permissions
        result[permission_name] += __unique_values(result[permission_name])
    return result


def __get_permission_set_users(report: LoadResult) -> OrdDict[str, List[str]]:
    result = OrderedDict()
    mutable_permission_names = __get_mutable_permission_names(report)
    for permission in report.allPermissions:
        permission_name = permission.permissionName
        if permission_name not in mutable_permission_names:
            continue
        if permission.assignedUserIds:
            result[permission_name] = permission.assignedUserIds
    return result


def __create_roles(mutable_descriptors: OrdDict[str, Permission]) -> List[Role]:
    result = []
    for permission_name, permission_value in mutable_descriptors.items():
        result.append(
            Role(
                id=str(uuid.uuid4()),
                name=permission_value.displayName,
                description=permission_value.description,
                source=permission_name,
            )
        )
    return result


def __create_role_users(roles: List[Role], psu: OrdDict[str, List[str]], strategy: str) -> OrdDict[str, List[str]]:
    # distributed approach
    if strategy == "distributed":
        role_users = OrderedDict()
        for role in roles:
            permission_users = psu.get(role.source, [])
            role_users[role.id] = permission_users
        return role_users
    return OrderedDict()


def __create_role_capabilities(roles: List[Role], p: OrdDict[str, Permission]) -> OrdDict[str, RoleCapabilityHolder]:
    result = OrderedDict()
    for role in roles:
        src_ps = role.source
        permission = p.get(src_ps)
        if not permission:
            # _log.warning(f"Permission '{src_ps}' not found for role {role.name}. Skipping it...")
            continue
        sub_permissions = permission.subPermissions
        if not sub_permissions:
            # _log.warning(f"Role '{role.name}' has no sub-permissions. Skipping it...")
            continue
        holder = RoleCapabilityHolder()
        for sub_permission in sub_permissions:
            sub_permission_desc = p.get(sub_permission)
            if not sub_permission_desc:
                msg = f"Sub-permission '{sub_permission}' descriptor not found " f"for role {role.name}. Skipping it..."
                # _log.warning(msg)
                continue
            if sub_permission_desc.subPermissions:
                holder.capabilitySetPS.append(sub_permission)
            else:
                holder.capabilityPS.append(sub_permission)
        result[role.id] = holder

    return result


def __create_role_capability_sets():
    return OrderedDict()


def __get_mutable_permission_names(report: LoadResult):
    mutable_permissions = report.allPermissions
    return set([x.permissionName for x in mutable_permissions if x.mutable])


def __get_flatten_ps_pss(report: LoadResult) -> OrdDict[str, List[str]]:
    result = OrderedDict()
    for permission in report.allPermissionsExpanded:
        permission_name = permission.permissionName
        if is_system_permission(permission_name):
            continue
        else:
            result[permission_name] = permission.subPermissions
    return result


def __has_mutable_permission(permission: str, mutable_user_pss: Set[str], flat_ps_pss: OrdDict[str, List[str]]) -> bool:
    for mutable_permission in mutable_user_pss:
        if permission in flat_ps_pss.get(mutable_permission, []):
            return True
    return False


def __unique_values(iterable):
    return list(OrderedDict.fromkeys(iterable).keys())


def __analyze_permissions(load_result: LoadResult) -> OrdDict[str, AnalyzedPermission]:
    system_permissions_count = 0
    analyzed_perms = OrderedDict[str, AnalyzedPermission]()
    flat_perms = load_result.allPermissionsExpanded
    okapi_perms_dict = __collect_okapi_permissions(load_result)

    for permission in load_result.allPermissions:
        name = permission.permissionName
        if ServiceUtils.is_system_permission(name):
            system_permissions_count += 1
            continue
        ap = analyzed_perms.get(name)

        if ap:
            ap.refPermissions.append(permission)
            if permission.subPermissions:
                ap.subPermissions.add(permission.subPermissions)
        else:
            ap = _create_analyzed_permission(name, permission)
            analyzed_perms[name] = ap

    _log.info(f"System permissions filtered: {system_permissions_count}")
    return analyzed_perms


def _create_analyzed_permission(permission):
    return AnalyzedPermission(
        permissionName=permission.permissionName,
        mutable=[permission.mutable],
        displayNames=[permission.displayName],
        subPermissions=OrderedSet(permission.subPermissions),
        parentPermissions=OrderedSet(permission.childOf),
        flatSubPermissions=OrderedSet(),
        okapiSubPermissions=OrderedSet(),
        refPermissions=[permission],
    )


def __collect_okapi_permissions(load_result: LoadResult) -> OrdDict[str, List[Permission]]:
    okapi_permissions = OrderedDict()
    for module_desc in load_result.okapiPermissions:
        for permission in module_desc.permissionSets:
            if not okapi_permissions.get(permission):
                okapi_permissions[permission] = []
            okapi_permissions[permission].append(permission)
    return okapi_permissions


def __analyze_permissions2(permissions: List[Permission]):
    non_system_permissions = [x for x in permissions if not is_system_permission(x.permissionName)]
    unique_permissions = OrderedDict((x.permissionName, x) for x in non_system_permissions).keys()
    counter = Counter([x.permissionName for x in non_system_permissions])
    ps_pss = __get_perm_set_perm_sets(permissions)
    return non_system_permissions, unique_permissions, counter, ps_pss
