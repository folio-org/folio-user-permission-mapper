from typing import List, OrderedDict

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Capability, Role
from folio_upm.dto.results import AnalysisResult
from folio_upm.integrations import eureka_client
from folio_upm.utils import common_utils, log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.service_utils import PartitionedDataLoader, PagedDataLoader
from folio_upm.utils.upm_env import Env


class EurekaService(metaclass=SingletonMeta):
    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("EurekaService initialized.")
        self._client = eureka_client.EurekaClient()

    def migrate_to_eureka(self, result: AnalysisResult):
        self.__create_roles(result.roles)
        self.__assign_role_users(result.roleUsers)
        self.__assign_role_capabilities(result.roleCapabilities)
        self.__assign_role_capability_sets(result.roleCapabilities)

    def __create_roles(self, roles: List[Role]):
        self._log.info(f"Creating {len(roles)} roles in Eureka...")
        role_names = [role.name for role in roles if role.name]
        data_loader_func = lambda role_names_query: self._client.find_roles_by_query(role_names_query)
        query_builder = lambda x: CqlQueryUtils.any_match_by_field("name", x)
        data_loader = PartitionedDataLoader("roles", role_names, data_loader_func, query_builder)
        roles = data_loader.load()
        existing_role_names = set([role.name for role in roles])
        for role in roles:
            if not role.name:
                self._log.error(f"Role name cannot be empty, skipping role creation for role: {role.id}")
                continue
            if role.name in existing_role_names:
                self._log.info(f"Creating role: '{role.name}'...")
                self._client.post_role(role)
                self._log.info(f"Role is created: id = {role.id}, name={role.name}")
            else:
                self._log.info(f"Role '{role.name}' already exists, skipping creation.")

    def __assign_role_users(self, user_roles: OrderedDict[str, List[str]]):
        self._log.info(f"Assigning users to roles...")
        for role_id, user_ids in user_roles.items():
            self._log.info(f"Assigning users to role: {role_id}...")
            self._client.post_role_users(role_id, user_ids)
            self._log.info(f"Users assigned to role: {role_id}...")

    def __assign_role_capabilities(self, role_capabilities: OrderedDict[str, List[str]]):
        self._log.info(f"Assigning capabilities to roles...")
        for role_id, permissions in role_capabilities.items():
            capabilities = self.__find_capabilities(permissions)
            all_capability_ids = [capability.id for capability in capabilities]
            capability_ids_to_assign = self.__find_unassigned_capability_ids(role_id, all_capability_ids)
            if capability_ids_to_assign:
                self._log.info(f"Assigning capabilities to role: {role_id}...")
                self._client.post_role_capabilities(role_id, capability_ids_to_assign)
            else:
                self._log.info(f"No unassigned capabilities found for role: {role_id}")

    def __assign_role_capability_sets(self, role_capability_sets: OrderedDict[str, List[str]]):
        self._log.info(f"Assigning capability sets to roles...")
        for role_id, permissions in role_capability_sets.items():
            capability_sets = self.__find_capability_sets(permissions)
            all_cset_ids = [capability_set.id for capability_set in capability_sets]
            capability_set_ids_to_assign = self.__find_unassigned_capability_set_ids(role_id, all_cset_ids)
            if capability_set_ids_to_assign:
                self._log.info(f"Assigning capability sets to role: {role_id}...")
                self._client.post_role_capability_sets(role_id, capability_set_ids_to_assign)
            else:
                self._log.info(f"No unassigned capability sets found for role: {role_id}")

    def __find_unassigned_capability_ids(self, role_id: str, capability_ids: List[str]) -> List[str]:
        self._log.info(f"Retrieving unassigned capability ids for role: {role_id}...")
        data_loader_func = lambda query, limit, offset: self._client.find_role_capabilities(query, limit, offset)
        data_loader = PagedDataLoader("roles-capabilities", data_loader_func, f"roleId=={role_id}")
        role_capabilities = data_loader.load()
        assigned_capability_ids = set([c.capabilityId for c in role_capabilities])
        return [capability_id for capability_id in capability_ids if capability_id not in assigned_capability_ids]

    def __find_unassigned_capability_set_ids(self, role_id: str, capability_set_ids: List[str]) -> List[str]:
        self._log.info(f"Retrieving unassigned capability set ids for role: {role_id}...")
        data_loader_func = lambda query, limit, offset: self._client.find_role_capability_sets(query, limit, offset)
        data_loader = PagedDataLoader("roles-capability-sets", data_loader_func, f"roleId=={role_id}")
        role_capabilities = data_loader.load()
        assigned_capability_set_ids = set([c.capabilityId for c in role_capabilities])
        return [cset_id for cset_id in capability_set_ids if cset_id not in assigned_capability_set_ids]

    def __find_capabilities(self, ps_names: List[str]) -> List[Capability]:
        self._log.info(f"Retrieving capabilities by permission names: {ps_names}...")
        data_loader_func = lambda query: self._client.find_capabilities(query)
        data_loader = PartitionedDataLoader("capabilities", ps_names, data_loader_func, self.__get_query_builder)
        return data_loader.load()

    def __find_capability_sets(self, ps_names: List[str]) -> List[Capability]:
        self._log.info(f"Retrieving capability sets by permission names: {ps_names}...")
        data_loader_func = lambda query: self._client.find_capability_sets(query)
        data_loader = PartitionedDataLoader("capability-sets", ps_names, data_loader_func, self.__get_query_builder)
        return data_loader.load()

    @staticmethod
    def __get_query_builder(permission_names: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("permission", permission_names)
