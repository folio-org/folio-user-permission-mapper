from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult
from folio_upm.model.stats.permission_user_stats import PermissionUserStats
from folio_upm.model.types.permission_type import DEPRECATED, INVALID, MUTABLE, OKAPI, QUESTIONABLE, UNPROCESSED


class UserStatsCollector:
    """
    Collects statistics about users and their associated permission sets.

    For each user, the following statistics are gathered:
        - userId: Unique identifier of the user
        - mutablePermissionSetsCount: Number of mutable permission sets assigned to the user
        - invalidPermissionSetsCount: Number of invalid permission sets assigned to the user
        - deprecatedPermissionSetsCount: Number of deprecated permission sets assigned to the user
        - okapiPermissionSetsCount: Number of okapi permission sets assigned to the user
        - allPermissionSetsCount: Total number of permission sets assigned to the user

    The statistics are computed by analyzing the user's permissions and classifying each permission set type.
    """

    def __init__(self, load_result: OkapiLoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._all_type = "all"
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self._user_stats = self.__collect_data()

    def get(self):
        return self._user_stats

    def __collect_data(self):
        user_stats = []
        for user_permission in self._load_result.allPermissionUsers:
            user_stats.append(self.__collect_user_perms_stats(user_permission))
        return user_stats

    def __collect_user_perms_stats(self, user_permission):
        counts = dict[str, int]()

        for ps_name in user_permission.permissions:
            ps_type = self._ps_analysis_result.identify_permission_type(ps_name)
            if ps_type.get_name() not in counts:
                counts[ps_type.get_name()] = 0
            if self._all_type not in counts:
                counts[self._all_type] = 0
            counts[ps_type.get_name()] += 1
            counts[self._all_type] += 1

        return PermissionUserStats(
            userId=user_permission.userId,
            mutablePermissionSetsCount=self.get_mutable_ps_count(counts),
            invalidPermissionSetsCount=counts.get(INVALID.get_name(), 0),
            okapiPermissionSetsCount=counts.get(OKAPI.get_name(), 0),
            deprecatedPermissionSetsCount=counts.get(DEPRECATED.get_name(), 0),
            allPermissionSetsCount=counts.get(self._all_type, 0),
        )

    @staticmethod
    def get_mutable_ps_count(counts: dict[str, int]) -> int:
        return (
            counts.get(MUTABLE.get_name(), 0)
            + counts.get(QUESTIONABLE.get_name(), 0)
            + counts.get(UNPROCESSED.get_name(), 0)
        )
