from functools import reduce
from typing import List, Optional, Callable, Set

from folio_upm.dto.okapi import PermissionSet
from folio_upm.dto.results import LoadResult, PermissionAnalysisResult, UserStatistics, PsStatistics
from folio_upm.dto.source_type import FLAT_PS, PS, OKAPI_PS
from folio_upm.dto.source_type import SourceType
from folio_upm.dto.support import AnalyzedPermissionSet
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class PermSetProcessor:

    _all_type = "all"

    def __init__(self, load_result: LoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self.__process_permissions()

    def get_user_stats(self) -> List[UserStatistics]:
        """
        Returns a list with an analysis result for user permission sets, including the following fields:
            - user id
            - number of mutable permission sets
            - number of invalid permission sets
            - number of deprecated permission sets
            - number of okapi permission sets
            - number of all permission sets

        :return: a list with data to generate a report page about user permission sets
        """

        return self._user_stats

    def get_permission_set_stats(self):
        """
        Returns a list with an analysis result for all permission sets, including the following fields:
            - permission name
            - permission display name
            - description
            - mutable or not
            - deprecated or not
            - number of sub permissions
            - number of flat sub permissions
            - created userId from metadata (if available)
            - how many times defined in the system (to identify duplicates)
            - if permission set is invalid - reason for invalidity

        :return: a list with data to generate a report page about all permission sets
        """
        return self._ps_stats

    def get_all_permission_sets(self):
        """
        Returns a list with an analysis result for all permission sets, including the following fields:
            - permission name
            - permission display name
            - description
            - mutable or not
            - deprecated or not
            - number of sub permissions
            - number of flat sub permissions
            - created userId from metadata (if available)
            - how many times defined in the system (to identify duplicates)
            - if permission set is invalid - reason for invalidity

        :return: a list with data to generate a report page about all permission sets
        """
        return self._all_permission_sets

    def get_user_permission_sets(self):
        """
        Returns a list with an analysis result for user permission sets, including the following fields:
            - user id
            - permission set name
            - permission set source type
            - is permission being mutable
            - is permission being deprecated
            - is permission being valid
            - has sub permissions

        :return: a list with data to generate a report page about user mutable permission sets
        """
        return self._user_permission_sets

    def get_parent_permission_sets(self):
        """
        Returns a list with an analysis result for parent permission sets, including the following fields:
            - permission name
            - permission is mutable or not
            - parent permission set name
            - parent permission is mutable or not

        :return: a list with data to generate a report page about user mutable permission sets
        """
        return self._parent_permission_sets

    def __process_permissions(self):
        self._log.info("Extracting permission set data from analysis results...")
        self._all_permission_sets = list()
        self._ps_stats = self.__collect_ps_stats()
        self._user_permission_sets = list()
        self._parent_permission_sets = list()
        self._user_stats = self.__collect_user_stats()
        self._log.info("Permission set data extracted successfully...")

    def __collect_user_stats(self):
        user_stats = []
        for user_permission in self._load_result.allPermissionUsers:
            user_stats.append(self.__collect_user_perms_stats(user_permission))
        return user_stats

    def __collect_user_perms_stats(self, user_permission):
        counts = dict[str, int]()
        for ps_name in user_permission.permissions:
            ps_type = self._ps_analysis_result.identify_permission(ps_name)
            if ps_type not in counts:
                counts[ps_type] = 0
            if self._all_type not in counts:
                counts[self._all_type] = 0
            counts[ps_type] += 1
            counts[self._all_type] += 1

        return UserStatistics(
            userId=user_permission.userId,
            mutablePermissionSetsCount=counts.get("mutable", 0),
            invalidPermissionSetsCount=counts.get("invalid", 0),
            okapiPermissionSetsCount=counts.get("okapi", 0),
            allPermissionSetsCount=counts.get(self._all_type, 0),
        )

    def __collect_ps_stats(self):
        result = []
        for ps_type in self._ps_analysis_result.get_types():
            for ap in self._ps_analysis_result[ps_type].values():
                result.append(self.__get_stats_for_analyzed_ps(ap, ps_type))
        return result

    @staticmethod
    def __get_stats_for_analyzed_ps(ap: AnalyzedPermissionSet, ps_type: str) -> PsStatistics:
        return PsStatistics(
            name=ap.permissionName,
            displayNames=list(OrderedSet([x.val.displayName for x in ap.srcPermSets if x.val.displayName])),
            type=ps_type,
            note=ap.note,
            reasons=ap.reasons,
            uniqueSources=list(OrderedSet([x.src for x in ap.srcPermSets])),
            refCount=len(ap.srcPermSets),
            uniqueModules = PermSetProcessor.__get_uq_module_ids(ap),
            subPermsCount=PermSetProcessor.__get_sub_perms_count_by_type(ap, {PS, OKAPI_PS}),
            flatPermCount=PermSetProcessor.__get_sub_perms_count_by_type(ap, {FLAT_PS}),
            parentPermsCount=PermSetProcessor.__get_parent_perms_count(ap)
        )

    @staticmethod
    def __get_uq_module_ids(ap: AnalyzedPermissionSet) -> List[str]:
        module_ids = OrderedSet()
        for x in ap.srcPermSets:
            module_id = PermSetProcessor.__get_module_id(x.val)
            if module_id:
                module_ids.add(module_id)
        return module_ids.to_list()


    @staticmethod
    def __get_sub_perms_count_by_type(ap: AnalyzedPermissionSet, src_types: Set[SourceType]) -> int:
        unique_sub_permissions = set()
        for src_ps in ap.srcPermSets:
            if not src_ps.src in src_types:
                continue
            unique_sub_permissions |= set(src_ps.val.subPermissions)
        return len(unique_sub_permissions)

    @staticmethod
    def __get_parent_perms_count(ap: AnalyzedPermissionSet) -> int:
        unique_parent_perms = reduce(lambda x, y: x | y, [set(sp.val.childOf) for sp in ap.srcPermSets])
        return len(unique_parent_perms)

    @staticmethod
    def __get_module_id(permission_set: PermissionSet) -> Optional[str]:
        module_name = permission_set.moduleName
        if not module_name:
            return None
        module_version = permission_set.moduleVersion
        if not module_version:
            return module_name
        return f"{module_name}-{module_version}"

    def __enrich_permissions(self, permissions, permission_users):
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
                    self._log.warning(f"User ID not found for grantedTo: {granted_to}")
            permission["assignedUserIds"] = assigned_user_ids
        return permissions
