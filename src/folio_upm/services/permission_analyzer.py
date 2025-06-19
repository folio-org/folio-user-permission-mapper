from collections import OrderedDict
from typing import Callable, List
from typing import OrderedDict as OrdDict

from folio_upm.dto.models import AnalyzedPermission, LoadResult, Permission, ValueHolder
from folio_upm.utils import log_factory
from folio_upm.utils.service_utils import ServiceUtils


class PermissionAnalyzer:

    def __init__(self, load_result: LoadResult):
        self._load_result = load_result
        self._result = OrderedDict[str, AnalyzedPermission]()
        self._system_permissions_count = 0
        self._log = log_factory.get_logger(__name__)
        self.__analyze_permissions()

    def get_analysis_result(self) -> OrdDict[str, AnalyzedPermission]:
        return self._result

    def __analyze_permissions(self):
        self.__collect_permissions()
        self.__enhance_with_flat_permissions()
        self.__enhance_with_okapi_permissions()

        self._log.info(f"System permissions filtered: {self._system_permissions_count}")

    def __collect_permissions(self):
        ps_type = "ps"

        def permission_consumer(ps: Permission, ap: AnalyzedPermission):
            ap.subPermissions.append(ValueHolder(s=ps_type, v=ps.subPermissions))

        self.__process_ps_list(ps_type, self._load_result.allPermissions, permission_consumer)

    def __enhance_with_flat_permissions(self):
        ps_type = "ps_flat"

        def permission_consumer(ps: Permission, ap: AnalyzedPermission):
            ap.flatSubPermissions.append(ValueHolder(s=ps_type, v=ps.subPermissions))

        self.__process_ps_list(ps_type, self._load_result.allPermissionsExpanded, permission_consumer)

    def __enhance_with_okapi_permissions(self):
        ps_type = "ps_okapi"

        def permission_consumer(ps: Permission, ap: AnalyzedPermission):
            ap.okapiSubPermissions.append(ValueHolder(s=ps_type, v=ps.subPermissions))
            ap.definedInOkapi = True

        for descriptor in self._load_result.okapiPermissions:
            self.__process_ps_list(ps_type, descriptor.permissionSets, permission_consumer)

    def __process_ps_list(self, ps_type, permissions, callable_func: Callable):
        for ps in permissions:
            if ServiceUtils.is_system_permission(ps.permissionName):
                self._system_permissions_count += 1
            else:
                self.__process_permission(ps, ps_type, callable_func)

    def __process_permission(self, ps: Permission, ps_type: str, callable_func: Callable):
        name = ps.permissionName
        ap = self._result.get(name)
        if not ap:
            self._result[name] = Utils.create_ap(ps, ps_type)
        else:
            ap.sources.append(ps_type)
            ap.mutable.append(ValueHolder(s=ps_type, v=ps.subPermissions))
            ap.displayNames.append(ValueHolder(s=ps_type, v=ps.subPermissions))
            ap.refPermissions.append(ValueHolder(s=ps_type, v=ps))
            callable_func(ps, ap)

    def __collect_okapi_permissions(self) -> OrdDict[str, List[Permission]]:
        okapi_permissions = OrderedDict()
        for module_desc in self._load_result.okapiPermissions:
            for permission in module_desc.permissionSets:
                if not okapi_permissions.get(permission):
                    okapi_permissions[permission] = []
                okapi_permissions[permission].append(permission)
        return okapi_permissions


class Utils:
    @staticmethod
    def create_ap(ps: Permission, ps_type) -> AnalyzedPermission:
        return AnalyzedPermission(
            sources=[ps_type],
            permissionName=ps.permissionName,
            mutable=[ValueHolder(s=ps_type, v=ps.mutable)],
            displayNames=[ValueHolder(s=ps_type, v=ps.displayName)],
            subPermissions=[ValueHolder(s=ps_type, v=ps.subPermissions)],
            parentPermissions=[ValueHolder(s=ps_type, v=ps.childOf)],
            flatSubPermissions=[],
            okapiSubPermissions=[],
            refPermissions=[ValueHolder(s=ps_type, v=ps)],
        )

    @staticmethod
    def wrap_or_empty_list(value: List[str]) -> List[List[str]]:
        if value:
            return [value]
        return []
