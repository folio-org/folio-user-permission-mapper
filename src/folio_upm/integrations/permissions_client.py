from idlelib.query import Query

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integrations.okapi_http_client import OkapiHttpClient
from folio_upm.utils import common_utils, log_factory
from folio_upm.utils.common_utils import CqlQueryUtils

_log = log_factory.get_logger(__name__)


class PermissionsClient(metaclass=SingletonMeta):

    def __init__(self):
        _log.debug("PermissionsClient initialized.")
        self._client = OkapiHttpClient()

    def load_perms_page(self, limit, offset, query, expanded=False):
        """
        Load user permissions from Okapi.

        @:param limit: Number of permissions to load.
        @:param offset: Offset for pagination.
        @:param query: CQL query to filter permissions.
        @:param expanded: Whether to expand the permissions.

        @:return: List of permissions.
        """
        _log.info(f"Loading permissions page: query='{query}', limit={limit}, offset={offset}")

        query_params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "expanded": str(expanded).lower(),
        }

        response = self._client.get_json("/perms/permissions", params=query_params)
        permissions = response.get("permissions", [])
        _log.info(f"Page loaded successfully: {len(permissions)} permission(s) found.")
        return permissions

    def load_user_permissions_by_ids(self, ids):
        """
        Load user permissions from Okapi.

        @:param ids: List of user ids.
        @return: List of user permissions.
        """
        query = CqlQueryUtils.any_match_by_field("id", ids)
        _log.info(f"Loading permissions page: query='{query}'")
        query_params = {"query": query, "limit": 500}
        response_json = self._client.get_json("/perms/users", params=query_params)
        return response_json.get("permissionUsers", [])
