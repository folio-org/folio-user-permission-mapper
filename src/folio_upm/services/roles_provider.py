from typing import List

from folio_upm.dto.eureka import Role, UserRoles, RoleUsers
from folio_upm.dto.results import LoadResult, PermissionAnalysisResult, EurekaLoadResult
from folio_upm.dto.strategy_type import StrategyType, DISTRIBUTED
from folio_upm.dto.support import RoleCapabilities
from folio_upm.utils import log_factory

_log = log_factory.get_logger(__name__)


class RolesProvider:

    def __init__(
        self,
        load_result: LoadResult,
        ps_analysis_result: PermissionAnalysisResult,
        eureka_load_result: EurekaLoadResult = None,
        strategy: StrategyType = DISTRIBUTED,
    ):
        self._load_result = load_result
        self._eureka_load_result = eureka_load_result
        self._ps_analysis_result = ps_analysis_result
        self._strategy = strategy
        self.__init_roles_and_relations()

    def get_roles(self) -> List[Role]:
        return self._roles

    def get_role_users(self) -> List[RoleUsers]:
        return self._role_users

    def get_role_capabilities(self) -> List[RoleCapabilities]:
        return self._role_capabilities

    def __init_roles_and_relations(self):
        _log.info("Generating roles and their relationships...")
        self._roles = self.__create_roles()
        self._role_users = self.__create_role_users()
        self._role_capabilities = self.__create_role_capabilities()
        _log.info("Roles and relationships generated successfully.")

    def __create_roles(self) -> List[Role]:
        pass

    def __create_role_users(self) -> List[RoleUsers]:
        pass

    def __create_role_capabilities(self) -> List[RoleCapabilities]:
        pass
