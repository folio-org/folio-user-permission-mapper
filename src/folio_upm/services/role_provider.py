from typing import List

from folio_upm.dto.eureka import Role, UserRoles, RoleUsers
from folio_upm.dto.results import LoadResult, PermissionAnalysisResult
from folio_upm.dto.strategy_type import StrategyType, DISTRIBUTED
from folio_upm.dto.support import RoleCapabilityHolder


class RoleGenerator:
    """
    Provides methods to manage roles and their relationships with users, permissions, and capabilities.
    """

    def __init__(
        self,
        load_result: LoadResult,
        perms_analysis_result: PermissionAnalysisResult,
        strategy: StrategyType = DISTRIBUTED,
    ):
        self._load_result = load_result
        self._ps_analysis_result = perms_analysis_result
        self._roles = self.__create_roles()
        self._strategy = strategy
        self._role_users = self.__create_role_users()
        self._role_capabilities = self.__create_role_capabilities()

    def get_roles(self) -> List[Role]:
        return self._roles

    def get_role_users(self) -> List[RoleUsers]:
        return self._role_users

    def get_role_capabilities(self) -> List[RoleCapabilityHolder]:
        return self._role_capabilities

    def get_permission_sets(self):
        return self.analysis_result.permissionSets

    def get_permission_permission_sets(self):
        return self.analysis_result.permissionPermissionSets

    def __create_roles(self) -> List[Role]:
        pass

    def __create_role_users(self) -> List[RoleUsers]:
        pass

    def __create_role_capabilities(self):
        pass
