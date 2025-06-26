from collections import OrderedDict
from typing import OrderedDict as OrdDict

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory


class CapabilitiesLoader(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._eureka_client = EurekaClient()

    def load_capabilities(self) -> OrdDict[str, any]:
        self._log.info("Starting eureka data loading...")
        capabilities = self.__load_data_by_query("capabilities", "cql.allRecords=1")
        capability_sets = self.__load_data_by_query("capability-sets", "cql.allRecords=1")
        role_users = self.__load_data_by_query("role-users", "cql.allRecords=1")
        role_capabilities = self.__load_data_by_query("role-capabilities", "cql.allRecords=1")
        role_capability_sets = self.__load_data_by_query("role-capability-sets", "cql.allRecords=1")

        self._log.info("Eureka data loaded successfully.")

        return OrderedDict(
            {
                "capabilities": capabilities,
                "capabilitySets": capability_sets,
                "roleUsers": role_users,
                "roleCapabilities": role_capabilities,
                "roleCapabilitySets": role_capability_sets,
            }
        )

    def __load_data_by_query(self, resource: str, query: str) -> OrdDict[str, any]:
        self._log.info(f"Loading all '{resource}' by query: query='{query}'")
        result = []
        limit = 500
        last_offset = 0

        while True:
            page = self._eureka_client.load_resource_page(resource, limit, last_offset, query)
            last_load_size = len(page)
            result += page
            last_offset += limit
            if last_load_size < limit:
                self._log.info(f"All '{resource} loaded: total={len(result)}")
                break

        return result
