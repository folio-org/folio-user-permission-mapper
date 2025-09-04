from typing import Callable, Dict, List, Optional, Tuple, TypeVar

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.utils import log_factory
from folio_upm.utils.iterable_utils import IterableUtils

T = TypeVar("T", Capability, CapabilitySet)


class CapabilityService:

    def __init__(self, eureka_load_result: Optional[EurekaLoadResult]):
        self._eureka_load_result = eureka_load_result
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._capabilities_by_name = self.__get_values_by_key(lambda x: x.capabilities, lambda v: v.name)
        self._capabilities_by_ps_name = self.__get_values_by_key(lambda x: x.capabilities, lambda v: v.permission)
        self._capability_sets_by_name = self.__get_values_by_key(lambda x: x.capabilities, lambda v: v.name)
        self._capability_sets_by_ps_name = self.__get_values_by_key(lambda x: x.capabilitySets, lambda v: v.permission)

    def find_by_ps_name(self, ps_name: str) -> Tuple[Capability | CapabilitySet | None, str]:
        return self.find_by_value(
            ps_name,
            lambda: self._capabilities_by_ps_name,
            lambda: self._capability_sets_by_ps_name,
        )

    def find_by_name(self, capability_name: str) -> Tuple[Capability | CapabilitySet | None, str]:
        return self.find_by_value(
            capability_name,
            lambda: self._capabilities_by_name,
            lambda: self._capability_sets_by_name,
        )

    def find_by_value(
        self,
        value: str,
        capability_dict_provider: Callable[[], Dict[str, List[Capability | CapabilitySet]]],
        capability_set_dict_provider: Callable[[], Dict[str, List[Capability | CapabilitySet]]],
    ) -> Tuple[Capability | CapabilitySet | None, str]:
        if self._eureka_load_result is None:
            return None, "unknown"
        capability_set_by_name = IterableUtils.first(capability_set_dict_provider().get(value, []))
        if capability_set_by_name is not None:
            return capability_set_by_name, "capability-set"
        capability_by_name = IterableUtils.first(capability_dict_provider().get(value, []))
        if capability_by_name is not None:
            return capability_by_name, "capability"
        return None, "not_found"

    def __get_values_by_key(
        self, mapper: Callable[[EurekaLoadResult], List[T]], keyMapper: Callable[[Capability | CapabilitySet], str]
    ) -> Dict[str, List[Capability | CapabilitySet]]:
        capabilities_or_sets = mapper(self._eureka_load_result) if self._eureka_load_result else []
        if not capabilities_or_sets:
            return {}
        values_by_key = {}
        for capability_or_set in capabilities_or_sets:
            if not capability_or_set:
                continue
            ps_name = keyMapper(capability_or_set)
            if not ps_name:
                self._log.warning("Capability or set without permission name found: %s", capability_or_set.id)
            if capability_or_set.permission in values_by_key:
                values_by_key[capability_or_set.permission].append(capability_or_set)
            else:
                values_by_key[capability_or_set.permission] = [capability_or_set]
        return values_by_key
