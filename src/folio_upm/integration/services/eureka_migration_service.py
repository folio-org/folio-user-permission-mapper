from typing import List
from typing import OrderedDict as OrdDict
from typing import Tuple

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.migration import EntityMigrationResult, HttpReqErr
from folio_upm.dto.eureka import Capability, RoleUsers
from folio_upm.dto.results import AnalysisResult, AnalyzedRole, EurekaMigrationResult
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.integration.services.role_capability_facade import RoleCapabilityFacade
from folio_upm.integration.services.role_service import RoleService
from folio_upm.integration.services.role_users_service import RoleUsersService
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PagedDataLoader, PartitionedDataLoader


class EurekaMigrationService(metaclass=SingletonMeta):
    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("EurekaService initialized.")
        self._client = EurekaClient()

    def migrate_to_eureka(self, result: AnalysisResult) -> EurekaMigrationResult:
        self._log.info("Eureka migration started...")
        migration_result = EurekaMigrationResult(
            roles=RoleService().create_roles(result.roles),
            roleCapabilities=RoleCapabilityFacade().assign_role_capabilities(result.roleCapabilities),
            roleUsers=[]
            # roleUsers=RoleUsersService().assign_users(result.roleUsers),
        )
        return migration_result
