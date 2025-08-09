from typing import List, override

from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.integration.clients.eureka.abstract_entity_client import AbstractEntityClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.role import Role
from folio_upm.utils import log_factory


class RolesClient(AbstractEntityClient[Role], metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RolesClient initialized.")
        self._http_client = EurekaHttpClient()

    @override
    def find_by_query(self, cql_query: str) -> List[Role]:
        query_params = {"query": cql_query, "limit": 500}
        response = self._http_client.get_json("/roles", params=query_params)
        if not isinstance(response, dict):
            error_msg_template = "Invalid response type for roles query(%s): %s"
            self._log.error(error_msg_template, cql_query, str(response))
            return []
        return [Role(**role_dict) for role_dict in response.get("roles", [])]

    def create_role(self, role: Role) -> Role:
        response_json = self._http_client.post_json("/roles", role.model_dump(by_alias=True))
        if not isinstance(response_json, dict):
            error_msg_template = "Invalid response type for roles query (request_role: %s): %s"
            self._log.error(error_msg_template, role, response_json)
            raise ValueError(f"Invalid response for role creation: {response_json}")
        return Role(**response_json)

    def delete_role(self, role_id) -> None:
        self._http_client.delete("/roles/" + role_id)
