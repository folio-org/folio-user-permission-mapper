from typing import List

from folio_upm.model.analysis.analyzed_parent_permission_set import AnalyzedParentPermSets
from folio_upm.model.analysis.analyzed_permission_set import AnalyzedPermissionSet
from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult
from folio_upm.model.types.permission_type import PermissionType
from folio_upm.model.types.source_type import FLAT_PS
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.utils import Utils


class ParentPermSetCollector:

    def __init__(self, load_result: OkapiLoadResult, ps_analysis_result: PermissionAnalysisResult):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self._skipped_service_permissions = OrderedSet()
        self._parent_perm_sets = self.__collect_data()

    def get(self):
        return self._parent_perm_sets

    def __collect_data(self):
        result = []
        for ps_type in self._ps_analysis_result.get_supported_types():

            for ap in self._ps_analysis_result.get(ps_type).values():
                result += self.__get_analyzed_parent_perm_set(ap, ps_type)

        skipped_perms_count = len(self._skipped_service_permissions)
        self._log.info("Skipped parent service permissions: %s ", skipped_perms_count)
        return result

    def __get_analyzed_parent_perm_set(
        self, ap: AnalyzedPermissionSet, ps_type: PermissionType
    ) -> List[AnalyzedParentPermSets]:
        parent_ps_dict = {}

        for source_perm_set in ap.sourcePermSets:
            if source_perm_set.src == FLAT_PS:
                continue
            for parent_ps in source_perm_set.val.childOf:
                if Utils.is_system_permission(parent_ps):
                    self._skipped_service_permissions.add(parent_ps)
                    continue
                parent_ps_type = self._ps_analysis_result.identify_permission_type(parent_ps)

                analyzed_ps = self._ps_analysis_result.get(parent_ps_type).get(parent_ps)
                if parent_ps not in parent_ps_dict:
                    parent_ps_dict[parent_ps] = AnalyzedParentPermSets(
                        permissionName=ap.permissionName,
                        permissionType=ps_type.get_name(),
                        displayName=ap.get_uq_display_names_str(),
                        parentPermissionName=parent_ps,
                        parentDisplayName=analyzed_ps.get_uq_display_names_str() if analyzed_ps else None,
                        parentPsTypes=OrderedSet(parent_ps_type.get_name()),
                        parentPsSources=OrderedSet(source_perm_set.src.get_name()),
                    )
                else:
                    parent_ps_dict[parent_ps].parentPsTypes.add(parent_ps_type.get_name())
                    parent_ps_dict[parent_ps].parentPsSources.add(source_perm_set.src.get_name())

        return list(parent_ps_dict.values())
