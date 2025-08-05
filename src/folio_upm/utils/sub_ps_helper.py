from typing import List, Set, Tuple

from folio_upm.model.analysis.analyzed_permission_set import AnalyzedPermissionSet
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult
from folio_upm.model.support.expanded_permission_set import ExpandedPermissionSet
from folio_upm.model.types.permission_type import MUTABLE
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.utils import Utils


class SubPermissionsHelper:

    def __init__(self, ps_analysis_result: PermissionAnalysisResult):
        self._log = log_factory.get_logger(__class__.__name__)
        self._ps_analysis_result = ps_analysis_result
        self._parent_ps_names = dict[str, OrderedSet[str]]()

    def expand_sub_ps(self, permission_name) -> list[ExpandedPermissionSet]:
        self._parent_ps_names = dict[str, OrderedSet[str]]()
        ps_type = self._ps_analysis_result.identify_permission_type(permission_name)
        analyzed_ps = self._ps_analysis_result[ps_type].get(permission_name)
        if analyzed_ps is None:
            return []
        _, parent_sub_ps = self.__get_sub_permissions(analyzed_ps, set(), None)
        sub_permissions = self.__expand_sub_permissions(analyzed_ps, set(), None)

        parent_sub_ps_set = set(parent_sub_ps)

        result_sub_permissions = []
        for sp in parent_sub_ps:
            expanded_ps = ExpandedPermissionSet(permissionName=sp, expandedFrom=[])
            result_sub_permissions.append(expanded_ps)

        for sp in sub_permissions:
            if sp in parent_sub_ps_set:
                continue
            expanded_from = self._parent_ps_names.get(sp, OrderedSet()).to_list()
            expanded_ps = ExpandedPermissionSet(permissionName=sp, expandedFrom=expanded_from)
            result_sub_permissions.append(expanded_ps)

        return sorted(result_sub_permissions, key=lambda p: (len(p.expandedFrom) > 0))

    def __expand_sub_permissions(self, ap, visited_ps_names: Set[str], root_ps_name) -> OrderedSet[str]:
        result_set = OrderedSet[str]()

        mutable_ps_sets, other_ps_names = self.__get_sub_permissions(ap, visited_ps_names, root_ps_name)
        mutable_ps_names_set = set([x.permissionName for x in mutable_ps_sets])
        new_visited_ps_names = visited_ps_names | mutable_ps_names_set

        new_root_ps_name = ap.permissionName
        result_set.add_all([x.permissionName for x in mutable_ps_sets])
        result_set.add_all(other_ps_names)
        for mutable_ap in mutable_ps_sets:
            result_set.add_all(self.__expand_sub_permissions(mutable_ap, new_visited_ps_names, new_root_ps_name))

        return result_set

    def __get_sub_permissions(self, ap, visited_names, root_ps_name) -> Tuple[List[AnalyzedPermissionSet], List[str]]:
        mutable_ps_sets = list[AnalyzedPermissionSet]()
        other_ps_set_names = list[str]()
        source_ps_name = ap.permissionName

        for permission_name in ap.get_sub_permissions():
            if source_ps_name == permission_name or Utils.is_system_permission(permission_name):
                continue

            self.__add_parent(permission_name, root_ps_name)
            if permission_name in visited_names:
                continue

            ps_type = self._ps_analysis_result.identify_permission_type(permission_name)
            if ps_type == MUTABLE:
                mutable_ps_sets.append(self._ps_analysis_result[ps_type].get(permission_name))
            else:
                other_ps_set_names.append(permission_name)

        return mutable_ps_sets, other_ps_set_names

    def __add_parent(self, permission_name, root_ps_name):
        if permission_name not in self._parent_ps_names:
            self._parent_ps_names[permission_name] = OrderedSet()
        if root_ps_name is not None:
            self._parent_ps_names[permission_name].add(root_ps_name)
