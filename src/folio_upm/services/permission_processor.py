from typing import List

from folio_upm.dto.results import LoadResult, PermissionAnalysisResult, UserStatistics
from folio_upm.utils import log_factory


class PermissionProcessor:

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
        pass

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
        pass

    def get_parent_permission_sets(self):
        """
        Returns a list with an analysis result for parent permission sets, including the following fields:
            - permission name
            - permission is mutable or not
            - parent permission set name
            - parent permission is mutable or not

        :return: a list with data to generate a report page about user mutable permission sets
        """

    def __process_permissions(self):
        self._log.info("Extracting permission set data from analysis results...")
        self._all_permission_sets = list()
        self._user_permission_sets = list()
        self._parent_permission_sets = list()
        self._user_stats = list[UserStatistics]()
        self._log.info("Permission set data extracted successfully...")

    def __collect_user_stats(self):
        all_type = "all"
        for user_permission in self._load_result.allPermissionUsers:
            counts = dict[str, int]()
            for ps_name in user_permission.permissions:
                ps_type = self._ps_analysis_result.identify_permission(ps_name)
                if ps_type not in counts:
                    counts[ps_type] = 0
                if all_type not in counts:
                    counts[all_type] = 0
                counts[ps_type] += 1
                counts[all_type] += 1

            self._user_stats.append(
                UserStatistics(
                    userId=user_permission.userId,
                    mutablePermissionSetsCount=counts.get("mutable", 0),
                    invalidPermissionSetsCount=counts.get("invalid", 0),
                    okapiPermissionSetsCount=counts.get("okapi", 0),
                    allPermissionSetsCount=counts.get(all_type, 0),
                )
            )

    def enrich_permissions(self, permissions, permission_users):
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
