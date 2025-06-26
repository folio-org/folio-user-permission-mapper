from collections import OrderedDict

from folio_upm.dto.results import LoadResult, PermissionAnalysisResult, AnalyzedPermSetPermSets
from folio_upm.dto.support import AnalyzedPermissionSet


class ParentPermSetCollector:
    """
    Collector for Parent Permission Sets.
    """

    def __init__(self, load_result: LoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self._parent_perm_sets = self.__collect_data()

    def get(self):
        return self._parent_perm_sets

    def __collect_data(self):
        result = []
        for ps_type in self._ps_analysis_result.get_types():
            for ap in self._ps_analysis_result[ps_type].values():
                result.append(self.__get_analyzed_parent_perm_set(ap, ps_type))
        return result

    def __get_analyzed_parent_perm_set(self, ap: AnalyzedPermissionSet, ps_type: str) -> AnalyzedPermSetPermSets:
        result = []
        parent_ps_dict = OrderedDict()
        for sourcePermSet in ap.sourcePermSets:
            sourcePermSet.
            result.append(analyzed_value)
        return result
