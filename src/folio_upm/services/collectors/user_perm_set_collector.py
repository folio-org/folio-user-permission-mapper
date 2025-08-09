from folio_upm.model.analysis.analyzed_user_permission_setresults import AnalyzedUserPermissionSet
from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult


class UserPermSetCollector:
    """
    Collects data for user permission sets, including the following fields:
        - user id
        - permission set name
        - permission set type (mutable, invalid, deprecated, okapi, etc.)
    """

    def __init__(self, load_result: OkapiLoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self._user_perm_sets = self.__collect_data()

    def get(self):
        return self._user_perm_sets

    def __collect_data(self) -> list[AnalyzedUserPermissionSet]:
        result = []
        for user_perms in self._load_result.allPermissionUsers:
            user_id = user_perms.userId
            for ps_name in user_perms.permissions:
                ps_type = self._ps_analysis_result.identify_permission_type(ps_name)

                ar = self._ps_analysis_result.get(ps_type).get(ps_name)
                analyzed_user_ps = AnalyzedUserPermissionSet(
                    userId=user_id,
                    permissionName=ps_name,
                    displayName=ar.get_uq_display_names_str() if ar else None,
                    permissionType=ps_type.get_name(),
                )
                result.append(analyzed_user_ps)
        return result
