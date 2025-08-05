from typing import List, override

from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.integration.clients.eureka.abstract_entity_client import AbstractEntityClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.utils import log_factory


class CapabilitySetClient(AbstractEntityClient[CapabilitySet], metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("CapabilitySetClient initialized.")
        self._http_client = EurekaHttpClient()

    @override
    def find_by_query(self, cql_query: str) -> List[CapabilitySet]:
        query_params = {"query": cql_query, "limit": 500}
        response = self._http_client.get_json("/capability-sets", params=query_params)
        found_capability_sets = response.get("capabilitySets", []) if response else []
        return [CapabilitySet(**cs) for cs in found_capability_sets]
