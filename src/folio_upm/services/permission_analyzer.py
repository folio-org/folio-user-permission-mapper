from collections import OrderedDict
from logging import INFO, WARN
from typing import List, Tuple
from typing import OrderedDict as OrdDict

from folio_upm.dto.models import AnalyzedPermission, LoadResult, Permission, ValueHolder, PermissionAnalysisResult
from folio_upm.utils import log_factory
from folio_upm.utils.service_utils import ServiceUtils

_log = log_factory.get_logger(__name__)


class PermissionAnalyzer:

    _ps_type = "ps"
    _ps_flat_type = "ps_flat"
    _ps_okapi_type = "ps_okapi"

    def __init__(self, load_result: LoadResult):
        _log.info("Starting permissions analysis...")
        self._load_result = load_result
        self._analyzed_permissions = 0
        self._analyzed_ps_dict = OrderedDict[str, AnalyzedPermission]()
        self._result = PermissionAnalysisResult()
        self._system_perms_count = {}
        self.__analyze_permissions()
        self._put_permissions_in_buckets()
        self.__log_results()

    def get_analysis_result(self) -> PermissionAnalysisResult:
        return self._result

    def __analyze_permissions(self):
        self.__collect_permissions()
        self.__enhance_with_flat_permissions()
        self.__enhance_with_okapi_permissions()

    def __collect_permissions(self):
        self.__process_ps_list(self._ps_type, self._load_result.allPermissions)

    def __enhance_with_flat_permissions(self):
        self.__process_ps_list(self._ps_flat_type, self._load_result.allPermissionsExpanded)

    def __enhance_with_okapi_permissions(self):
        for descriptor in self._load_result.okapiPermissions:
            self.__process_ps_list(self._ps_okapi_type, descriptor.permissionSets)

    def __process_ps_list(self, ps_type, permissions):
        self._system_perms_count[ps_type] = 0
        for ps in permissions:
            self._analyzed_permissions += 1
            if ServiceUtils.is_system_permission(ps.permissionName):
                self._system_perms_count[ps_type] += 1
            else:
                self.__process_permission(ps, ps_type)

    def __process_permission(self, ps: Permission, ps_type: str):
        name = ps.permissionName
        ap = self._analyzed_ps_dict.get(name)
        if not ap:
            self._analyzed_ps_dict[name] = Utils.create_ap(ps, ps_type)
        else:
            ap.modules += Utils.get_module_version_vh_list(ps_type, ps)
            ap.sources.append(ps_type)
            ap.mutable.append(ValueHolder(s=ps_type, v=ps.mutable))
            ap.displayNames.append(ValueHolder(s=ps_type, v=ps.displayName))
            ap.refPermissions.append(ValueHolder(s=ps_type, v=ps))
            ap.deprecated.append(ValueHolder(s=ps_type, v=ps.deprecated))
            ap.subPermissions.append(ValueHolder(s=ps_type, v=ps.subPermissions))

    def __collect_okapi_permissions(self) -> OrdDict[str, List[Permission]]:
        okapi_permissions = OrderedDict()
        for module_desc in self._load_result.okapiPermissions:
            for permission in module_desc.permissionSets:
                if not okapi_permissions.get(permission):
                    okapi_permissions[permission] = []
                okapi_permissions[permission].append(permission)
        return okapi_permissions

    def _put_permissions_in_buckets(self):
        for ps_name, ap in self._analyzed_ps_dict.items():
            self.__put_permission_in_bucket(ap)

    def __put_permission_in_bucket(self, ap: AnalyzedPermission):
        ps_name = ap.permissionName
        if Utils.is_deprecated_ps(ap):
            self._result.deprecated[ps_name] = ap
            return

        all_sources = set(ap.sources)
        if len(all_sources) == 1:
            self._result.invalid[ps_name] = ap
            return

        qvc = QuestionableValueChecker(ap)
        if qvc.is_questionable():
            ap.reasons = qvc.get_reasons()
            self._result.questionable[ps_name] = ap
            return

        okapi_sources = set([x for x in ap.sources if x == self._ps_okapi_type])
        if okapi_sources:
            self._result.system[ps_name] = ap
        elif len(all_sources) != 2:
            self._result.invalid[ps_name] = ap
        elif next(iter(set([vh.v for vh in ap.mutable]))):
            self._result.mutable[ps_name] = ap
        else:
            self._result.unprocessed[ps_name] = ap

    def __log_results(self):
        rs = self._result
        _log.info("Permissions analysis completed. Amount of analyzed permissions: {self._analyzed_permissions}")
        _log.info(f"System permissions found: {len(rs.system)}")
        _log.info(f"Mutable permissions found: {len(rs.mutable)}")
        _log.info(f"Questionable permissions found: {len(rs.questionable)}")
        _log.log(
            Utils.get_log_level(rs.invalid),
            f"Invalid permissions found: {len(rs.invalid)}",
        )
        _log.info(f"Unprocessed permissions found: {len(rs.unprocessed)}")
        for t in [self._ps_type, self._ps_flat_type, self._ps_okapi_type]:
            _log.info(f"System permissions filtered for type '{t}': {self._system_perms_count[t]}")


class Utils:
    @staticmethod
    def create_ap(ps: Permission, ps_type: str) -> AnalyzedPermission:
        return AnalyzedPermission(
            sources=[ps_type],
            deprecated=[ValueHolder(s=ps_type, v=ps.deprecated)],
            modules=Utils.get_module_version_vh_list(ps_type, ps),
            permissionName=ps.permissionName,
            mutable=[ValueHolder(s=ps_type, v=ps.mutable)],
            displayNames=[ValueHolder(s=ps_type, v=ps.displayName)],
            subPermissions=[ValueHolder(s=ps_type, v=ps.subPermissions)],
            parentPermissions=[ValueHolder(s=ps_type, v=ps.childOf)],
            refPermissions=[ValueHolder(s=ps_type, v=ps)],
        )

    @staticmethod
    def wrap_or_empty_list(value: List[str]) -> List[List[str]]:
        if value:
            return [value]
        return []

    @staticmethod
    def get_module_version_vh_list(ps_type: str, ps: Permission) -> List[ValueHolder]:
        if ps.moduleName:
            if ps.moduleVersion:
                return [ValueHolder(s=ps_type, v=f"{ps.moduleName}-{ps.moduleVersion}")]
            return [ValueHolder(s=ps_type, v=ps.moduleName)]
        return []

    @staticmethod
    def is_deprecated_ps(ap: AnalyzedPermission) -> bool:
        deprecated_values_without_okapi = set([vh.v for vh in ap.deprecated if vh.s != "ps_okapi"])
        if len(deprecated_values_without_okapi) == 1 and next(iter(deprecated_values_without_okapi)) is True:
            ap.note = "Deprecated (not in okapi)"
            return True
        deprecated_values_set = set([vh.v for vh in ap.deprecated])
        return len(deprecated_values_set) == 1 and next(iter(deprecated_values_set)) is True

    @staticmethod
    def is_mutable_ps(ap: AnalyzedPermission) -> bool:
        mutable_values_set = set([vh.v for vh in ap.mutable])
        return len(mutable_values_set) == 1 and next(iter(mutable_values_set)) is True

    @staticmethod
    def get_log_level(value) -> int:
        return WARN if len(value) > 0 else INFO


class QuestionableValueChecker:

    def __init__(self, ps: AnalyzedPermission):
        self._ps = ps
        self._reasons = []
        _multiple_values_msg = "Multiple values"
        self._verifiers = [
            (self.__check_multiple_mutable_values, _multiple_values_msg),
            (self.__check_multiple_deprecated_values, _multiple_values_msg),
            (self.__check_multiple_deprecated_values, _multiple_values_msg),
            (self.__check_different_sub_permissions, _multiple_values_msg),
        ]
        self.__perform_analysis()

    def is_questionable(self) -> bool:
        return len(self._reasons) == 1

    def get_reasons(self) -> List[Tuple[str, str]]:
        return self._reasons

    def __perform_analysis(self):
        for verifier, reason in self._verifiers:
            verification_result = verifier()
            if verification_result[0]:
                self.__add_reason(reason, verification_result[1])

    def __add_reason(self, reason: str, field: str):
        self._reasons.append((reason, field))

    def __check_multiple_mutable_values(self) -> Tuple[bool, str]:
        mutable = self._ps.mutable
        return len(set([vh.v for vh in mutable])) > 1, "mutable"

    def __check_multiple_deprecated_values(self):
        deprecated = self._ps.deprecated
        return len(set([vh.v for vh in deprecated])) > 1, "deprecated"

    def __has_multiple_display_names(self):
        display_names = self._ps.displayNames
        return len(set([vh.v for vh in display_names])) > 1, "displayNames"

    def __check_different_sub_permissions(self) -> Tuple[bool, str]:
        sub_permissions_sets = [frozenset(vh.v) for vh in self._ps.subPermissions if vh.s != "ps_flat"]
        f_sub_perms_sets = [x for x in sub_permissions_sets if len(x) > 0]
        flat_sub_permissions_sets = [frozenset(vh.v) for vh in self._ps.subPermissions if vh.s == "ps_flat"]
        f_flat_sub_perm_sets = [x for x in flat_sub_permissions_sets if len(x) > 0]
        field_name = "subPermissions"

        if len(f_sub_perms_sets) == 0 and len(f_sub_perms_sets) == len(f_flat_sub_perm_sets):
            return False, field_name

        unique_sub_permissions = set(sub_permissions_sets)
        unique_flat_sub_permissions = set(flat_sub_permissions_sets)
        if len(unique_sub_permissions) == 1:
            if len(unique_flat_sub_permissions) != 1:
                return False, field_name
            sub_permissions = next(iter(unique_sub_permissions))
            flat_sub_permissions = next(iter(unique_flat_sub_permissions))
            return not sub_permissions.issubset(flat_sub_permissions), field_name

        return True, field_name
