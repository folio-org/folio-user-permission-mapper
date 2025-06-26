import uuid
from collections import OrderedDict
from typing import List
from typing import OrderedDict as OrdDict

from folio_upm.dto.eureka import Role, RoleUsers
from folio_upm.dto.results import AnalyzedRole, EurekaLoadResult, LoadResult, PermissionAnalysisResult
from folio_upm.dto.strategy_type import DISTRIBUTED, StrategyType
from folio_upm.dto.support import AnalyzedPermissionSet, RoleCapabilities
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
        for analyzed_ps in self._ps_analysis_result.mutable.values():
            ar = RolesProvider.__create_role(analyzed_ps)
            result[ar.role.id] = ar
        return result

    @staticmethod
    def __create_role(analyzed_ps: AnalyzedPermissionSet) -> AnalyzedRole:
        name = analyzed_ps.get_first_value(lambda x: x.displayName)
        description = analyzed_ps.get_first_value(lambda x: x.description)
        role = Role(id=str(uuid.uuid4()), name=name, description=description)
        return AnalyzedRole(
            role=role,
            source=analyzed_ps.permissionName,
            excluded=False,
            # todo: This should be calculated based on role_users
            assignedUsersCount=0,
            # todo: This should be calculated based on role_capabilities
            permissionsCount=0,
            # todo: This should be calculated based on role_capabilities
            flatPermissionsCount=0,
            # todo: This should be calculated based on role_capabilities
            totalPermissionsCount=0,
        )

    def __create_role_users(self) -> List[RoleUsers]:
        pass

    def __create_role_capabilities(self) -> List[RoleCapabilities]:
        pass
