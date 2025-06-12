import uuid
from collections import OrderedDict
from typing import KeysView, List
from typing import OrderedDict as OrdDict

from dto.models import AnalysisResult, LoadResult, Permission, Role, UserPermsHolder


def analyze_results(analysis_json: dict, strategy: str) -> AnalysisResult:
    report = LoadResult(**analysis_json)

    mutable_descriptors = __get_mutable_perms_descriptors(report)
    permission_set_nesting = __get_mutable_permission_set_nesting(report)

    mutable_permission_names = mutable_descriptors.keys()
    user_permission_sets = __get_user_permissions_rels(report, mutable_permission_names)
    mutable_ps_users = ____get_permission_set_users(report)
    permission_permission_sets = __get_perm_set_perm_sets(report)
    roles = __create_roles(mutable_descriptors)

    return AnalysisResult(
        permissionSets=mutable_descriptors,
        permissionSetsNesting=permission_set_nesting,
        usersPermissionSets=user_permission_sets,
        permissionPermissionSets=permission_permission_sets,
        roles=roles,
        roleUsers=__create_role_users(roles, mutable_ps_users, strategy),
        roleCapabilities=__create_role_capabilities(),
        roleCapabilitySets=__create_role_capability_sets(),
    )


def __get_mutable_perms_descriptors(report: LoadResult) -> OrdDict[str, Permission]:
    result = OrderedDict()
    for permission in report.allPermissions:
        mutable = permission.mutable
        if mutable:
            result[permission.permissionName] = permission
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


def __get_user_permissions_rels(report: LoadResult, mutable_perm_names: KeysView[str]) -> OrdDict[str, UserPermsHolder]:
    result = OrderedDict()
    for permission_user in report.allPermissionUsers:
        uph = UserPermsHolder()
        user_id = permission_user.userId
        for permission in permission_user.permissions:
            if permission in mutable_perm_names:
                uph.mutablePermissions.append(permission)
            else:
                uph.systemPermissions.append(permission)
        result[user_id] = uph
    return result


def __get_perm_set_perm_sets(report: LoadResult) -> OrdDict[str, List[str]]:
    result = OrderedDict()
    for permission in report.allPermissions:
        permission_name = permission.permissionName
        sub_permissions = permission.subPermissions
        if permission_name.startswith("SYS#"):
            continue
        else:
            result[permission_name] = sub_permissions
    return result


def ____get_permission_set_users(report: LoadResult) -> OrdDict[str, List[str]]:
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


def __create_role_capabilities():
    return OrderedDict()


def __create_role_capability_sets():
    return OrderedDict()


def __get_mutable_permission_names(report: LoadResult):
    mutable_permissions = report.allPermissions
    return set([x.permissionName for x in mutable_permissions if x.mutable])
