from logging import INFO, WARN
from typing import List

from folio_upm.dto.okapi import PermissionSet
from folio_upm.dto.results import OkapiLoadResult, PermissionAnalysisResult
from folio_upm.dto.source_type import FLAT_PS, OKAPI_PS, PS, SourceType
from folio_upm.dto.support import AnalyzedPermissionSet, SourcedPermissionSet
from folio_upm.services.questionable_ps_validator import QuestionablePermissionValidator
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.service_utils import ServiceUtils


class PermissionAnalyzer:

    def __init__(self, load_result: OkapiLoadResult):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._analyzed_ps_dict = dict[str, AnalyzedPermissionSet]()
        self._result = PermissionAnalysisResult()
        self.__analyze_permissions()

    def get_analysis_result(self) -> PermissionAnalysisResult:
        return self._result

    def __analyze_permissions(self):
        self._log.info("Starting permissions analysis...")
        self._analyzed_permissions = 0
        self._system_perms_count = dict[SourceType, int]()
        self._system_permission_names = OrderedSet[str]()
        self.__process_permissions()
        self.__process_flat_permissions()
        self.__process_okapi_permissions()
        self._result.systemPermissionNames = self._system_permission_names
        self._put_permissions_in_buckets()
        self.__log_results()

    def __process_permissions(self):
        self.__process_ps_list(PS, self._load_result.allPermissions)

    def __process_flat_permissions(self):
        self.__process_ps_list(FLAT_PS, self._load_result.allPermissionsExpanded)

    def __process_okapi_permissions(self):
        for descriptor in self._load_result.okapiPermissions:
            self.__process_ps_list(OKAPI_PS, descriptor.permissionSets)

    def __process_ps_list(self, src_type: SourceType, permissions: List[PermissionSet]):
        self._system_perms_count[src_type] = 0
        for ps in permissions:
            self._analyzed_permissions += 1
            if ServiceUtils.is_system_permission(ps.permissionName):
                self._system_perms_count[src_type] += 1
                self._system_permission_names.add(ps.permissionName)
            else:
                self.__process_permission(ps, src_type)

    def __process_permission(self, ps: PermissionSet, src_type: SourceType):
        name = ps.permissionName
        found_value = self._analyzed_ps_dict.get(name)
        if not found_value:
            self._analyzed_ps_dict[name] = _Utils.create_ap(ps, src_type)
        else:
            found_value.sourcePermSets.append(SourcedPermissionSet(src=src_type, val=ps))

    def _put_permissions_in_buckets(self):
        for ps_name, ap in self._analyzed_ps_dict.items():
            self.__put_permission_in_bucket(ps_name, ap)

    def __put_permission_in_bucket(self, ps_name: str, ap: AnalyzedPermissionSet):
        if _Utils.is_deprecated_ps(ap):
            self._result.deprecated[ps_name] = ap
            return

        all_sources = set([svh.src for svh in ap.sourcePermSets])
        if len(all_sources) == 1:
            ap.reasons.append(f"single def in {next(iter(all_sources)).value}")
            self._result.invalid[ps_name] = ap
            return

        qvc = QuestionablePermissionValidator(ap)
        if qvc.is_questionable():
            ap.reasons = qvc.get_reasons()
            self._result.questionable[ps_name] = ap
            return

        okapi_sources = set([sp.src for sp in ap.sourcePermSets if sp.src == SourceType.OKAPI_PS])
        if okapi_sources:
            self._result.okapi[ps_name] = ap
        elif len(all_sources) != 2:
            ap.reasons.append(f"multiple def in {sorted([x.value for x in all_sources])}")
            self._result.invalid[ps_name] = ap
        elif next(iter(set([sp.val.mutable for sp in ap.sourcePermSets]))):
            self._result.mutable[ps_name] = ap
        else:
            self._result.unprocessed[ps_name] = ap

    def __log_results(self):
        rs = self._result
        self._log.info(f"Permissions analysis completed. Amount of analyzed permissions: {self._analyzed_permissions}")
        self._log.info(f"System permissions found: {len(rs.okapi)}")
        self._log.info(f"Mutable permissions found: {len(rs.mutable)}")
        self._log.info(f"Questionable permissions found: {len(rs.questionable)}")
        self._log.log(
            _Utils.get_log_level(rs.invalid),
            f"Invalid permissions found: {len(rs.invalid)}",
        )
        self._log.info(f"Unprocessed permissions found: {len(rs.unprocessed)}")
        for t in [e for e in SourceType]:
            self._log.info(f"System permissions filtered for type '{t.value}': {self._system_perms_count.get(t, 0)}")


class _Utils:

    @staticmethod
    def create_ap(ps: PermissionSet, ps_type: SourceType) -> AnalyzedPermissionSet:
        return AnalyzedPermissionSet(
            permissionName=ps.permissionName,
            sourcePermSets=[SourcedPermissionSet(src=ps_type, val=ps)],
        )

    @staticmethod
    def wrap_or_empty_list(value: List[str]) -> List[List[str]]:
        if value:
            return [value]
        return []

    @staticmethod
    def is_deprecated_ps(ap: AnalyzedPermissionSet) -> bool:
        deprecated_values_without_okapi = set([sp.val.deprecated for sp in ap.sourcePermSets if sp.src != OKAPI_PS])
        if len(deprecated_values_without_okapi) == 1 and next(iter(deprecated_values_without_okapi)) is True:
            ap.note = "Deprecated (not in okapi)"
            return True
        deprecated_values_set = set([sp.val.deprecated for sp in ap.sourcePermSets])
        return len(deprecated_values_set) == 1 and next(iter(deprecated_values_set)) is True

    @staticmethod
    def is_mutable_ps(ap: AnalyzedPermissionSet) -> bool:
        mutable_values_set = set([sp.val.mutable for sp in ap.sourcePermSets])
        return len(mutable_values_set) == 1 and next(iter(mutable_values_set)) is True

    @staticmethod
    def get_log_level(value) -> int:
        return WARN if len(value) > 0 else INFO
