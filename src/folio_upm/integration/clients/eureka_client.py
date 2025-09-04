from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.utils import log_factory


class EurekaClient(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("EurekaClient initialized.")
        self._client = EurekaHttpClient()

    def load_page_by_query(self, resource: str, path: str, query: str, limit: int, offset: int):
        query_params = {"query": query, "limit": limit, "offset": offset}
        response_json = self._client.get_json(path, params=query_params)
        if not isinstance(response_json, dict):
            error_msg_template = "Invalid response type for roles query(%s, %s, %s, %s, %s): %s"
            self._log.error(error_msg_template, resource, path, query, limit, offset, str(response_json))
            return []
        return response_json.get(resource, [])
