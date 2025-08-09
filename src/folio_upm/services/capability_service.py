from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import IterableUtils

T = TypeVar("T", Capability, CapabilitySet)


class CapabilityService:

    def __init__(self, eureka_load_result: Optional[EurekaLoadResult]):
        self._eureka_load_result = eureka_load_result
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._capabilities_by_name = self.__get_values_by_ps_name(lambda x: x.capabilities)
        self._capability_sets_by_name = self.__get_values_by_ps_name(lambda x: x.capabilitySets)

    def find_by_ps_name(self, ps_name: str) -> Tuple[Capability | CapabilitySet | None, str]:
        if self._eureka_load_result is None:
            return None, "unknown"
        capability_set_by_name = self.get_capability_set_by_ps_name(ps_name)
        if capability_set_by_name is not None:
            return capability_set_by_name, "capability-set"
        capability_by_name = self.get_capability_by_ps_name(ps_name)
        if capability_by_name is not None:
            return capability_by_name, "capability"
        return None, "not_found"

    def get_capability_by_ps_name(self, permission_name: str) -> Optional[Capability]:
        return IterableUtils.first(self._capabilities_by_name.get(permission_name, []))

    def get_capability_set_by_ps_name(self, permission_name: str) -> Optional[CapabilitySet]:
        return IterableUtils.first(self._capability_sets_by_name.get(permission_name, []))

    def __get_values_by_ps_name(
        self,
        mapper: Callable[[EurekaLoadResult], List[T]],
    ) -> Dict[str, List[Any]]:
        capabilities_or_sets = mapper(self._eureka_load_result) if self._eureka_load_result else []
        if not capabilities_or_sets:
            return {}
        sets_by_name = {}
        for capability_or_set in capabilities_or_sets:
            ps_name = capability_or_set.permission
            if not ps_name:
                self._log.warning("Capability or set without permission name found: %s", capability_or_set.id)
            if capability_or_set.permission in sets_by_name:
                sets_by_name[capability_or_set.permission].append(capability_or_set)
            else:
                sets_by_name[capability_or_set.permission] = [capability_or_set]
        return sets_by_name
