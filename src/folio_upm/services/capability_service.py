from typing import Tuple

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.utils.common_utils import IterableUtils


class CapabilityService:

    def __init__(self, eureka_load_result: EurekaLoadResult):
        self._eureka_load_result = eureka_load_result
        if self._eureka_load_result is not None:
            self._capabilities_by_name = self.__get_capabilities_by_name()
            self._capability_sets_by_name = self.__get_capability_sets_by_name()
        else:
            self._capabilities_by_name = {}
            self._capability_sets_by_name = {}

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

    def get_capability_by_ps_name(self, permission_name: str) -> Capability | None:
        return IterableUtils.first(self._capabilities_by_name.get(permission_name, []))

    def get_capability_set_by_ps_name(self, permission_name: str) -> CapabilitySet | None:
        return IterableUtils.first(self._capability_sets_by_name.get(permission_name, []))

    def __get_capabilities_by_name(self):
        capabilities = self._eureka_load_result.capabilities
        capabilities_by_name = {}
        for capability in capabilities:
            if capability.name in capabilities_by_name:
                capabilities_by_name[capability.permission].append(capability)
            else:
                capabilities_by_name[capability.permission] = [capability]
        return capabilities_by_name

    def __get_capability_sets_by_name(self):
        capability_sets = self._eureka_load_result.capabilitySets
        sets_by_name = {}
        for capability_set in capability_sets:
            if capability_set.name in sets_by_name:
                sets_by_name[capability_set.permission].append(capability_set)
            else:
                sets_by_name[capability_set.permission] = [capability_set]
        return sets_by_name
