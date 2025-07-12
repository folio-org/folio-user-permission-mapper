from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.results import AnalysisResult, EurekaMigrationResult, PreparedEurekaData
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.integration.services.role_capability_facade import RoleCapabilityFacade
from folio_upm.integration.services.role_service import RoleService
from folio_upm.integration.services.role_users_service import RoleUsersService
from folio_upm.utils import log_factory


class EurekaMigrationService(metaclass=SingletonMeta):
    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("EurekaService initialized.")
        self._role_service = RoleService()
        self._role_users_service = RoleUsersService()
        self._role_capability_facade = RoleCapabilityFacade()

    def migrate_to_eureka(self, eureka_data: PreparedEurekaData) -> EurekaMigrationResult:
        self._log.info("Eureka migration started...")
        return EurekaMigrationResult(
            roles=self._role_service.create_roles(eureka_data.roles),
            roleCapabilities=self._role_capability_facade.assign_role_capabilities(eureka_data.roleCapabilities),
            roleUsers=self._role_users_service.assign_users(eureka_data.roleUsers),
        )
