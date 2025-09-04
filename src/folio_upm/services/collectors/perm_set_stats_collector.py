from functools import reduce
from typing import List, Optional, Set

from folio_upm.model.analysis.analyzed_permission_set import AnalyzedPermissionSet
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult
from folio_upm.model.stats.permission_set_stats import PermissionSetStats
from folio_upm.model.types.permission_type import PermissionType
from folio_upm.model.types.source_type import FLAT_PS, OKAPI_PS, PS, SourceType
from folio_upm.services.capability_service import CapabilityService
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.utils import Utils


class PermSetStatisticsCollector:
    """
    Collects and returns statistics for all analyzed permission sets.

    Each statistics entry (`PsStatistics`) includes:
        - name: Permission set name
        - displayNames: List of unique display names from all sources
        - type: Source type of the permission set
        - note: Additional notes or comments
        - reasons: Reasons for invalidity, if any
        - uniqueSources: List of unique sources where the permission set is defined
        - refCount: Number of times the permission set is defined (across all sources)
        - uniqueModules: List of unique module IDs associated with the permission set
        - subPermsCount: Number of unique sub-permissions of types PS or OKAPI_PS
        - flatPermCount: Number of unique sub-permissions of type FLAT_PS
        - parentPermsCount: Number of unique parent permissions (permissions this set is a child of)
    """

    def __init__(self, ps_analysis_result: PermissionAnalysisResult, eureka_load_result: Optional[EurekaLoadResult]):
        self._eureka_load_result = eureka_load_result
        self._ps_analysis_result = ps_analysis_result

        self._capability_service = CapabilityService(eureka_load_result)
        self._ps_statistics = self.__collect_data()

    def get(self):
        return self._ps_statistics

    def __collect_data(self):
        result = []
        for ps_type in self._ps_analysis_result.get_supported_types():

            for ap in self._ps_analysis_result.get(ps_type).values():
                result.append(self.__get_stats_for_analyzed_ps(ap, ps_type))
        return result

    def __get_stats_for_analyzed_ps(self, ap: AnalyzedPermissionSet, ps_type: PermissionType) -> PermissionSetStats:
        return PermissionSetStats(
            name=ap.permissionName,
            displayNames=list(OrderedSet[str]([x.val.displayName for x in ap.sourcePermSets if x.val.displayName])),
            permissionType=ps_type.get_name(),
            note=ap.note,
            reasons=ap.reasons,
            uniqueSources=list(OrderedSet[str]([x.src.get_name() for x in ap.sourcePermSets])),
            refCount=len(ap.sourcePermSets),
            uniqueModules=self.__get_uq_module_ids(ap),
            subPermsCount=self.__get_sub_perms_count_by_type(ap, {PS, OKAPI_PS}),
            flatPermCount=self.__get_sub_perms_count_by_type(ap, {FLAT_PS}),
            parentPermsCount=self.__get_parent_perms_count(ap),
        )

    @staticmethod
    def __get_uq_module_ids(ap: AnalyzedPermissionSet) -> List[str]:
        module_ids = OrderedSet()
        for x in ap.sourcePermSets:
            module_id = Utils.get_module_id(x.val)
            if module_id:
                module_ids.add(module_id)
        return module_ids.to_list()

    @staticmethod
    def __get_sub_perms_count_by_type(ap: AnalyzedPermissionSet, src_types: Set[SourceType]) -> int:
        unique_sub_permissions = set()
        for src_ps in ap.sourcePermSets:
            if src_ps.src not in src_types:
                continue
            unique_sub_permissions |= set(src_ps.val.subPermissions)
        return len(unique_sub_permissions)

    @staticmethod
    def __get_parent_perms_count(ap: AnalyzedPermissionSet) -> int:
        unique_parent_perms = reduce(lambda x, y: x | y, [set(sp.val.childOf) for sp in ap.sourcePermSets])
        return len(unique_parent_perms)

    def __check_capability(self, ps_name) -> bool | None:
        if self._eureka_load_result is None:
            return None
        capability_or_set_type = self._capability_service.find_by_ps_name(ps_name)
        return capability_or_set_type[0] is not None
