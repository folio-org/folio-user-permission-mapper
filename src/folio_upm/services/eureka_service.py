from typing import List, OrderedDict

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.results import AnalysisResult
from folio_upm.dto.eureka import Role, Capability
from folio_upm.integrations import eureka_client
from folio_upm.utils import common_utils, env, log_factory

_log = log_factory.get_logger(__name__)


class EurekaService(metaclass=SingletonMeta):
    def __init__(self):
        _log.info("EurekaService initialized.")
        self._client = eureka_client.EurekaClient()

    def migrate_to_eureka(self, result: AnalysisResult):
        self.__create_roles(result.roles)
        self.__assign_role_users(result.roleUsers)
        self.__assign_role_capabilities(result.roleCapabilities)
        self.__assign_role_capability_sets(result.roleCapabilities)

    def __create_roles(self, roles: List[Role]):
        for role in roles:
            if not role.name:
                _log.error(f"Role name cannot be empty, skipping role creation for role: {role.id}")
                continue
            _log.info(f"Creating role: '{role.name}'...")
            self._client.post_role(role)
            _log.info(f"Role is created: id = {role.id}, name={role.name}")

    def __assign_role_users(self, user_roles: OrderedDict[str, List[str]]):
        for role_id, user_ids in user_roles.items():
            _log.info(f"Assigning users to role: {role_id}...")
            self._client.post_role_users(role_id, user_ids)
            _log.info(f"Users assigned to role: {role_id}...")

    def __find_capabilities(self, permission_names: List[str]) -> List[Capability]:
        batch_size = int(env.require_env("CAPABILITY_IDS_PARTITION_SIZE", default_value=50, log_result=False))
        partitioned_permission_names = common_utils.partition(permission_names, batch_size)
        capabilities = []
        for partition in partitioned_permission_names:
            capabilities += eureka_client.get_capabilities_by_names(partition)
        return capabilities

    def __find_capability_sets(self, permission_names: List[str]) -> List[Capability]:
        batch_size = int(env.require_env("CAPABILITY_IDS_PARTITION_SIZE", default_value=50, log_result=False))
        partitioned_permission_names = common_utils.partition(permission_names, batch_size)
        capability_sets = []
        for partition in partitioned_permission_names:
            capability_sets += eureka_client.get_capabilities_by_names(partition)
        return capability_sets

    def __assign_role_capabilities(self, role_capabilities: OrderedDict[str, List[str]]):
        for role_id, permissions in role_capabilities.items():
            capabilities = __find_capabilities(permissions)
            capability_ids = [capability.id for capability in capabilities]
            if capability_ids:
                eureka_client.post_role_capabilities(role_id, capability_ids)

    def __assign_role_capability_sets(self, role_capability_sets: OrderedDict[str, List[str]]):
        for role_id, permissions in role_capability_sets.items():
            capability_sets = __find_capability_sets(permissions)
            capability_ids = [capability_set.id for capability_set in capability_sets]
            if capability_ids:
                eureka_client.post_role_capability_sets(role_id, capability_ids)
