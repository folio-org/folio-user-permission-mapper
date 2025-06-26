from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.clients.base.okapi_http_client import OkapiHttpClient
from folio_upm.utils import log_factory


class PermissionsClient(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("PermissionsClient initialized.")
        self._client = OkapiHttpClient()

    def load_perms_page(self, cql_query, limit, offset, expanded=False):
        query_params = {
            "query": cql_query,
            "limit": limit,
            "offset": offset,
            "expanded": str(expanded).lower(),
        }

        response = self._client.get_json("/perms/permissions", params=query_params)
        permissions = response.get("permissions", [])
        self._log.info(f"Page loaded successfully: {len(permissions)} permission(s) found.")
        return permissions

    def load_user_permissions_by_ids(self, ids_cql_query):
        query_params = {"query": ids_cql_query, "limit": 500}
        response_json = self._client.get_json("/perms/users", params=query_params)
        return response_json.get("permissionUsers", [])
