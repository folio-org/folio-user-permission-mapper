from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.clients.permissions_client import PermissionsClient
from folio_upm.utils import log_factory
from folio_upm.utils.cql_query_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PagedDataLoader, PartitionedDataLoader
from folio_upm.utils.ordered_set import OrderedSet


class PermissionService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("PermissionService initialized")
        self._client = PermissionsClient()

    def load_all_permissions_by_query(self, query: str, expanded=False):
        data_loader = PagedDataLoader("permissions", self.__load_ps_page(expanded), query)
        return data_loader.load()

    def load_permission_users(self, permissions):
        self._log.info("Loading permission users...")
        all_granted_to_unique = OrderedSet()
        for permission in permissions:
            granted_to = permission.get("grantedTo", [])
            all_granted_to_unique += granted_to

        partitioned_data_loader = PartitionedDataLoader(
            "permission users",
            list(all_granted_to_unique),
            lambda q: self._client.load_user_permissions_by_ids(q),
            lambda ids: CqlQueryUtils.any_match_by_field("id", ids),
        )

        return partitioned_data_loader.load()

    def __load_ps_page(self, expanded=False):
        return lambda query, limit, offset: self._client.load_perms_page(query, limit, offset, expanded)
