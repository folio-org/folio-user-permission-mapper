from typing import List, OrderedDict as OrdDict, Tuple

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Capability, Role
from folio_upm.dto.results import AnalysisResult, AnalyzedRole
from folio_upm.integrations import eureka_client
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader, PagedDataLoader


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

    def __create_roles(self, ar: OrdDict[str, AnalyzedRole]):
        self._log.info("Creating %s role(s)...", len(ar))
        role_names = [ar.role.name for ar in ar.values() if ar.role.name]
        data_loader = PartitionedDataLoader("roles", role_names, self.__load_roles, self.__any_match_by_name)
        ar = data_loader.load()
        existing_role_names = set([role.n for role in ar])
        for role in ar:
            role_name = role.n
            if not role_name:
                self._log.error("Role name cannot be empty, skipping role creation for role: %s", role.id)
                continue
            if role_name in existing_role_names:
                self._log.info(f"Creating role: '{role_name}'...")
                created_role = self._client.post_role(role)
                self._log.info("Role is created: id=%s, name=%s", created_role.id, role_name)
            else:
                self._log.info("Role '%s' already exists, skipping creation.", role_name)

    def __assign_role_users(self, user_roles: OrdDict[str, List[str]]):
        self._log.info("Assigning users to roles...")
        for role_id, user_ids in user_roles.items():
            self._log.info("Assigning users to role: %s...", role_id)
            self._client.post_role_users(role_id, user_ids)
            self._log.info("Users assigned to role: %s...", role_id)

    def __assign_role_capabilities(self, role_capabilities: OrdDict[str, List[str]]):
        self._log.info("Assigning capabilities to roles...")
        for role_id, permissions in role_capabilities.items():
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

    def __assign_role_capability_sets(self, role_capability_sets: OrdDict[str, List[str]]):
        self._log.info("Assigning capability sets to roles...")
        for role_id, permissions in role_capability_sets.items():
            capability_sets = self.__find_capability_sets(permissions)
            all_cset_ids = [capability_set.id for capability_set in capability_sets]
            cset_ids_tuple = self.__find_cset_ids_tuple(role_id, all_cset_ids)
            if cset_ids_tuple[0]:
                msg_template = "Assigning capability sets to role: %s, capabilityIds=%s..."
                self._log.info(msg_template, role_id, cset_ids_tuple[1])
                self._client.post_role_capability_sets(role_id, cset_ids_tuple[0])
            else:
                self._log.info(f"No unassigned capability sets found for role: {role_id}")

    def __find_capability_ids_tuple(self, role_id: str, capability_ids: List[str]) -> Tuple[List[str], List[str]]:
        self._log.info("Retrieving unassigned capability ids for role: %s...", role_id)
        data_loader_func = lambda query, limit, offset: self._client.find_role_capabilities(query, limit, offset)
        data_loader = PagedDataLoader("roles-capabilities", data_loader_func, f"roleId=={role_id}")
        role_capabilities = data_loader.load()
        assigned_capability_ids = set([c.capabilityId for c in role_capabilities])
        return (
            [capability_id for capability_id in capability_ids if capability_id not in assigned_capability_ids],
            [capability_id for capability_id in capability_ids if capability_id in assigned_capability_ids],
        )

    def __find_cset_ids_tuple(self, role_id: str, capability_set_ids: List[str]) -> Tuple[List[str], List[str]]:
        self._log.info("Retrieving unassigned capability set ids for role: %s...", role_id)
        data_loader_func = lambda query, limit, offset: self._client.find_role_capability_sets(query, limit, offset)
        data_loader = PagedDataLoader("roles-capability-sets", data_loader_func, f'roleId=="{role_id}"')
        role_capabilities = data_loader.load()
        assigned_capability_set_ids = set([c.capabilityId for c in role_capabilities])
        return (
            [cset_id for cset_id in capability_set_ids if cset_id not in assigned_capability_set_ids],
            [cset_id for cset_id in capability_set_ids if cset_id in assigned_capability_set_ids],
        )

    def __find_capabilities(self, ps_names: List[str]) -> List[Capability]:
        self._log.info("Retrieving capabilities by permission names: %s...", ps_names)
        data_loader_func = lambda query: self._client.find_capabilities(query)
        data_loader = PartitionedDataLoader("capabilities", ps_names, data_loader_func, self.__get_query_builder)
        return data_loader.load()

    def __find_capability_sets(self, ps_names: List[str]) -> List[Capability]:
        self._log.info("Retrieving capability sets by permission names: %s...", ps_names)
        data_loader_func = lambda query: self._client.find_capability_sets(query)
        data_loader = PartitionedDataLoader("capability-sets", ps_names, data_loader_func, self.__get_query_builder)
        return data_loader.load()

    def __load_roles(self, role_names_query):
        return self._client.find_roles_by_query(role_names_query)

    @staticmethod
    def __any_match_by_name(values: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("name", values)

    @staticmethod
    def __get_query_builder(permission_names: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("permission", permission_names)
