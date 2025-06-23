from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integrations.permissions_client import PermissionsClient
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.service_utils import PagedDataLoader, PartitionedDataLoader
from folio_upm.utils.upm_env import Env


class PermissionService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("PermissionService initialized")
        self._client = PermissionsClient()

    def load_all_permissions_by_query(self, query: str, expanded=False):
        permissions_loader = lambda q, l, o: self._client.load_perms_page(q, l, o, expanded)
        data_loader = PagedDataLoader("permissions", permissions_loader, query)
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
            int(Env().require_env("PERMISSION_IDS_PARTITION_SIZE", default_value=50)),
        )

        return partitioned_data_loader.load()
