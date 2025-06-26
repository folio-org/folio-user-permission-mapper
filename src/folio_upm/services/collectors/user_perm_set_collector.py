from folio_upm.dto.results import LoadResult, PermissionAnalysisResult


class UserPermSetCollector:

    def __init__(self, load_result: LoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self._user_perm_sets = self.__collect_data()

    def get(self):
        return self._user_perm_sets

    def __collect_data(self):
        pass
