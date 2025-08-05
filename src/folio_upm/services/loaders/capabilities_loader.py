from typing import Dict, Any, List

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.loading_utils import PagedDataLoader


class CapabilitiesLoader(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._eureka_client = EurekaClient()

    def load_capabilities(self) -> Dict[str, any]:
        self._log.info("Starting eureka data loading...")
        cql_all_query = "cql.allRecords=1"
        roles = self.__load_data_by_query("roles", "/roles", cql_all_query)
        capabilities = self.__load_data_by_query("capabilities", "/capabilities", cql_all_query)
        capability_sets = self.__load_data_by_query("capabilitySets", "/capability-sets", cql_all_query)
        role_users = self.__load_data_by_query("userRoles", "/roles/users", cql_all_query)
        role_capabilities = self.__load_data_by_query("roleCapabilities", "/roles/capabilities", cql_all_query)
        role_capability_sets = self.__load_data_by_query("roleCapabilitySets", "/roles/capability-sets", cql_all_query)
        user_capabilities = self.__load_data_by_query("userCapabilities", "/users/capability-sets", cql_all_query)
        user_capability_sets = self.__load_data_by_query("userCapabilitySets", "/users/capability-sets", cql_all_query)

        self._log.info("Eureka data loaded successfully.")

        return {
            "roles": roles,
            "capabilities": capabilities,
            "capabilitySets": capability_sets,
            "roleUsers": role_users,
            "roleCapabilities": role_capabilities,
            "userCapabilities": user_capabilities,
            "roleCapabilitySets": role_capability_sets,
            "userCapabilitySets": user_capability_sets,
        }

    def __load_data_by_query(self, resource: str, path: str, query: str):
        return PagedDataLoader(resource, self.__load_resource_page(resource, path), query).load()

    def __load_resource_page(self, resource: str, path: str):
        return lambda query, limit, offset: self._eureka_client.load_page(resource, path, query, limit, offset)
