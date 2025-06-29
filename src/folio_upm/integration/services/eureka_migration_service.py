from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.results import AnalysisResult, EurekaMigrationResult
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.integration.services.role_capability_facade import RoleCapabilityFacade
from folio_upm.integration.services.role_service import RoleService
from folio_upm.integration.services.role_users_service import RoleUsersService
from folio_upm.utils import log_factory


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
            roleUsers=RoleUsersService().assign_users(result.roleUsers),
        )
        return migration_result
