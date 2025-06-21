import uuid
from collections import Counter, OrderedDict
from typing import List
from typing import OrderedDict as OrdDict
from typing import Set

from folio_upm.dto.eureka import Role
from folio_upm.dto.okapi import Permission
from folio_upm.dto.results import LoadResult, AnalysisResult
from folio_upm.dto.strategy_type import DISTRIBUTED, StrategyType
from folio_upm.dto.support import RoleCapabilities, AnalyzedPermission, UserPermsHolder
from folio_upm.services.permission_analyzer import PermissionAnalyzer
from folio_upm.services.permission_processor import PermissionProvider
from folio_upm.services.roles_provider import RolesProvider
from folio_upm.utils import log_factory
from folio_upm.utils.service_utils import ServiceUtils

_log = log_factory.get_logger(__name__)


class LoadedDataAnalyzer:

    def __init__(self, analysis_json: dict, strategy: StrategyType = DISTRIBUTED):
        self._analysis_json = analysis_json
        self._load_result = LoadResult(**analysis_json)
        self._strategy = strategy
        self._ps_analysis_result = PermissionAnalyzer(self._load_result).get_analysis_result()
        self._result = self.__analyze_results()

    def get_results(self) -> AnalysisResult:
        return self._result

    def __analyze_results(self) -> AnalysisResult:
        load_result = self._load_result
        roles_provider = RolesProvider(self._load_result, self._ps_analysis_result, self._strategy)
        ps_data_provider = PermissionProvider(self._load_result, self._ps_analysis_result)

        all_ps = __get_all_ps_desc(load_result)
        mutable_ps = set([name for name, value in all_ps.items() if value.mutable])
        ps_nesting = __get_mutable_permission_set_nesting(load_result)
        user_permission_sets = __get_user_permission_sets(load_result, all_ps, mutable_ps)
        mutable_ps_users = __get_permission_set_users(load_result)

        return AnalysisResult(
            permsAnalysisResult=self._ps_analysis_result,
            allPermissionSets=ps_data_provider.get_all_permission_sets(),
            mutablePermissionSets=all_ps,
            flatPermissionSets=__get_flatten_ps_pss(load_result),
            permissionSetsNesting=ps_nesting,
            usersPermissionSets=user_permission_sets,
            permissionPermissionSets=permission_permission_sets,
            roles=roles_provider.get_roles(),
            roleUsers=roles_provider.get_role_users(),
            roleCapabilities=roles_provider.get_role_capabilities(),
        )

class _Utils:

    @staticmethod
    def get_all_ps_desc(report: LoadResult) -> OrdDict[str, List[Permission]]:
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

    @staticmethod
    def create_roles(mutable_perms: List[AnalyzedPermission]) -> List[Role]:
        result = []
        for ap in mutable_perms:
            result.append(_Utils.create_role(ap))
        return result

    @staticmethod
    def create_role(ps: AnalyzedPermission) -> Role:
        return Role(
            id=str(uuid.uuid4()),
            name=next(iter(set(vh.val for vh in ps.displayNames))),
            description=permission_value.description,
            source=permission_name,
        )


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


def __create_role_users(roles: List[Role], psu: OrdDict[str, List[str]], strategy: str) -> OrdDict[str, List[str]]:
    # distributed approach
    if strategy == "distributed":
        role_users = OrderedDict()
        for role in roles:
            permission_users = psu.get(role.source, [])
            role_users[role.id] = permission_users
        return role_users
    return OrderedDict()


def __create_role_capabilities(roles: List[Role], p: OrdDict[str, Permission]) -> OrdDict[str, RoleCapabilities]:
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
        holder = RoleCapabilities()
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


def __get_flatten_ps_pss(report: LoadResult) -> OrdDict[str, List[str]]:
    result = OrderedDict()
    for permission in report.allPermissionsExpanded:
        permission_name = permission.permissionName
        if ServiceUtils.is_system_permission(permission_name):
            continue
        else:
            result[permission_name] = permission.subPermissions
    return result


def __has_mutable_permission(permission: str, mutable_user_pss: Set[str], flat_ps_pss: OrdDict[str, List[str]]) -> bool:
    for mutable_permission in mutable_user_pss:
        if permission in flat_ps_pss.get(mutable_permission, []):
            return True
    return False


def __collect_okapi_permissions(load_result: LoadResult) -> OrdDict[str, List[Permission]]:
    okapi_permissions = OrderedDict()
    for module_desc in load_result.okapiPermissions:
        for permission in module_desc.permissionSets:
            if not okapi_permissions.get(permission):
                okapi_permissions[permission] = []
            okapi_permissions[permission].append(permission)
    return okapi_permissions
