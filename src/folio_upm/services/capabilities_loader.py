from collections import OrderedDict
from typing import OrderedDict as OrdDict

from openpyxl.compat.singleton import Singleton

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integrations.eureka_client import EurekaClient
from folio_upm.services import okapi_service, permission_service
from folio_upm.utils import log_factory

_log = log_factory.get_logger(__name__)


class CapabilitiesLoader(metaclass=SingletonMeta):

    def __init__(self):
        self._eureka_client = EurekaClient()

    def load_capabilities(self) -> OrdDict[str, any]:
        _log.info("Starting eureka capabilities loading...")

        capabilities = self.__load_capabilities_by_query('cql.allRecords=1')
        capability_sets = self.__load_capability_sets_by_query('cql.allRecords=1')


        _log.info("Capabilities and Capability Sets are loaded successfully.")
        return OrderedDict(
            {
                "capabilities": capabilities,
                "capabilitySets": capability_sets,
            }
        )

    def __load_data_by_query(self, resource:str, query: str) -> OrdDict[str, any]:
        _log.info(f"Loading all '{resource}' by query: query='{query}'")
        result = []
        limit = 500
        last_offset = 0

        while True:
            page = self._eureka_client.load_resource_page(resource, limit, last_offset, query)
            last_load_size = len(page)
            result += page
            last_offset += limit
            if last_load_size < limit:
                _log.info(f"All permissions loaded: total={len(result)}")
                break

        return result
