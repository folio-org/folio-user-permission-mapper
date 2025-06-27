from typing import List

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.support import RoleCapabilitiesHolder, CapabilityPlaceholder
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class RoleCapabilityService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")
        self._client = EurekaClient()

    def assign_role_capabilities(self, role_capabilities: List[RoleCapabilitiesHolder]):
        for rch in role_capabilities:
            [x.permissionName for x in rch.capabilities]
            self.__assign_role_capabilities(rch.role_id, rch.permissions)

    def __assign_role_capabilities(self, role_id: str, permissions: List[str]):
        self._log.info("Assigning capabilities to role: %s, capabilityIds=%s", role_id, capability_ids)
        if not capability_ids:
            self._log.warning("No capabilities provided, skipping assignment for role: %s", role_id)
            return []

        assigned_capabilities = self._client.post_role_capabilities(role_id, capability_ids)
        self._log.info("Capabilities assigned to role: %s, count=%d", role_id, len(assigned_capabilities))
        return assigned_capabilities


    def __assign_role_capability_sets(self, role_id: str, permissions: List[str]):
        self._log.info("Assigning capability sets to roles...")
        capability_sets = self.__find_capability_sets(permissions)
        all_cset_ids = [capability_set.id for capability_set in capability_sets]
        cset_ids_tuple = self.__find_cset_ids_tuple(role_id, all_cset_ids)
        if cset_ids_tuple[0]:
            msg_template = "Assigning capability sets to role: %s, capabilityIds=%s..."
            self._log.info(msg_template, role_id, cset_ids_tuple[1])
            self._client.post_role_capability_sets(role_id, cset_ids_tuple[0])
        else:
            self._log.info(f"No unassigned capability sets found for role: {role_id}")

    def __assign_role_capabilities(self, role_id: str, permissions: List[str]):
        self._log.info("Assigning capabilities to roles...")
        capabilities = self.__find_capabilities(permissions)
        all_capability_ids = [capability.id for capability in capabilities]
        capability_ids_tuple = self.__find_capability_ids_tuple(role_id, all_capability_ids)
        if capability_ids_tuple[0]:
            msg_template = "Assigning capabilities to role: %s, capabilityIds=%s..."
            self._log.info(msg_template, role_id, capability_ids_tuple[1])
            self._client.post_role_capabilities(role_id, capability_ids_tuple[0])
        else:
            msg_template = "No unassigned capabilities found for role: %s, capabilityIds=%s"
            self._log.info(msg_template, role_id, capability_ids_tuple[1])

    def __get_permission_names_to_assign(self, capabilities: List[CapabilityPlaceholder]):
        strategy = Env().get_migration_strategy()
        if strategy == "capabilities":
            return [x.permissionName for x in capabilities]
        elif strategy == "capability-sets":
            return [x.name for x in capabilities]
        else:
            raise ValueError(f"Unknown migration strategy: {strategy}")
