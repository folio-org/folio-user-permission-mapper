import uuid
from typing import List, OrderedDict as OrdDict
from collections import OrderedDict
from folio_upm.dto.eureka import Role, RoleUsers
from folio_upm.dto.results import EurekaLoadResult, LoadResult, PermissionAnalysisResult
from folio_upm.dto.strategy_type import DISTRIBUTED, StrategyType
from folio_upm.dto.support import RoleCapabilities, AnalyzedPermissionSet, AnalyzedRole
from folio_upm.utils import log_factory


class RolesProvider:

    def __init__(
        self,
        load_result: LoadResult,
        ps_analysis_result: PermissionAnalysisResult,
        eureka_load_result: EurekaLoadResult = None,
        strategy: StrategyType = DISTRIBUTED,
    ):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._eureka_load_result = eureka_load_result
        self._ps_analysis_result = ps_analysis_result
        self._strategy = strategy
        self.__init_roles_and_relations()

    def get_roles(self) -> OrdDict[str, AnalyzedRole]:
        return self._roles

    def get_role_users(self) -> List[RoleUsers]:
        return self._role_users

    def get_role_capabilities(self) -> List[RoleCapabilities]:
        return self._role_capabilities

    def __init_roles_and_relations(self):
        self._log.info("Generating roles and their relationships...")
        self._roles = self.__create_roles()
        self._role_users = self.__create_role_users()
        self._role_capabilities = self.__create_role_capabilities()
        self._log.info("Roles and relationships generated successfully.")

    def __create_roles(self) -> OrdDict[str, AnalyzedRole]:
        result = OrderedDict[str, AnalyzedRole]()
        for ps_name, analyzed_ps in self._ps_analysis_result.mutable.items():
            ar = RolesProvider.__create_role(analyzed_ps)
            result[ar.role.id] = ar
        return result

    @staticmethod
    def __create_role(analyzed_ps: AnalyzedPermissionSet) -> AnalyzedRole:
        name = analyzed_ps.get_first_value(lambda x: x.displayName)
        description = analyzed_ps.get_first_value(lambda x: x.description)
        role = Role(id=str(uuid.uuid4()), name=name, description=description)
        return AnalyzedRole(role=role, src=analyzed_ps.permissionName)

    def __create_role_users(self) -> List[RoleUsers]:
        pass

    def __create_role_capabilities(self) -> List[RoleCapabilities]:
        pass
