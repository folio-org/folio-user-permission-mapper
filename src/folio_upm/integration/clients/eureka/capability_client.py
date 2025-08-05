from typing import List, override

from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.integration.clients.eureka.abstract_entity_client import AbstractEntityClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.capability import Capability
from folio_upm.utils import log_factory


class CapabilityClient(AbstractEntityClient[Capability], metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("CapabilityClient initialized.")
        self._http_client = EurekaHttpClient()

    @override
    def find_by_query(self, cql_query: str) -> List[Capability]:
        query_params = {"query": cql_query, "limit": 500}
        response = self._http_client.get_json("/capabilities", params=query_params)
        found_capabilities = response.get("capabilities", []) if response else []
        return [Capability(**c) for c in found_capabilities]
