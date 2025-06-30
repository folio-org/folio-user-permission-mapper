from collections import OrderedDict
from typing import Tuple, Optional

from folio_upm.dto.eureka import CapabilitySet, Capability
from folio_upm.dto.results import EurekaLoadResult
from folio_upm.utils.common_utils import IterableUtils


class CapabilityService:

    def __init__(self, eureka_load_result: EurekaLoadResult):
        self._eureka_load_result = eureka_load_result
        self._capabilities_by_name = self.__get_capabilities_by_name()
        self._capability_sets_by_name = self.__get_capability_sets_by_name()

    def find_by_ps_name(self, ps_name: str) -> Tuple[Capability | CapabilitySet | None, str]:
        capability_set_by_name = self.get_capability_set_by_ps_name(ps_name)
        if capability_set_by_name is not None:
            return capability_set_by_name, "capability-set"
        capability_by_name = self.get_capability_by_ps_name(ps_name)
        if capability_by_name is not None:
            return capability_by_name, "capability"
        return None, "unknown"

    def get_capability_by_ps_name(self, permission_name: str) -> Capability | None:
        return IterableUtils.first(self._capabilities_by_name.get(permission_name, []))

    def get_capability_set_by_ps_name(self, permission_name: str) -> CapabilitySet | None:
        return IterableUtils.first(self._capabilities_by_name.get(permission_name, []))

    def __get_capabilities_by_name(self):
        capabilities = self._eureka_load_result.capabilities
        capabilities_by_name = OrderedDict()
        for capability in capabilities:
            if capability.name in capabilities_by_name:
                capabilities_by_name[capability.permission].append(capability)
            else:
                capabilities_by_name[capability.permission] = [capability]
        return capabilities_by_name

    def __get_capability_sets_by_name(self):
        capabilities = self._eureka_load_result.capabilitySets
        capabilities_by_name = OrderedDict()
        for capability_set in capabilities:
            if capability_set.name in capabilities_by_name:
                capabilities_by_name[capability_set.permission].append(capability_set)
            else:
                capabilities_by_name[capability_set.permission] = [capability_set]
        return capabilities_by_name
