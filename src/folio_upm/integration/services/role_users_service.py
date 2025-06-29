from typing import List

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import RoleUsers
from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class RoleUsersService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")
        self._client = EurekaClient()

    def assign_users(self, role_users: List[RoleUsers]) -> List[EntityMigrationResult]:
        migration_result = []
        for ru in role_users:
            migration_result += self.__assign_to_role(ru)
        return migration_result

    def __assign_to_role(self, role_users: RoleUsers) -> List[EntityMigrationResult]:
        try:
            return self.__assign_role_users(role_users)
        except requests.HTTPError:
            return self.handle_error_response(role_users)

    def __assign_role_users(self, ru: RoleUsers) -> List:
        if not ru.userIds:
            self._log.warning(f"No users provided, skipping role-users assigment: roleId={ru.roleName}")
            return []

        self._log.debug("Assigning users to role '%s': %s", ru.roleName, ru.userIds)
        assignment_response = self._client.post_role_users(ru.roleId, ru.userIds)
        success_results = [self._create_success_result(ru, ur.userId) for ur in assignment_response]

        unassigned_user_ids = self.__find_unassigned_users(ru.userIds, assignment_response)
        if unassigned_user_ids:
            self._log.warning("Unassigned users found for role '%s': %s", ru.roleName, unassigned_user_ids)
            unassigned_ids_result = [self._create_skipped_result(ru, i) for i in unassigned_user_ids]
            return unassigned_ids_result + success_results

        self._log.info("Users assigned to role '%s': %s", ru.roleName, ru.userIds)
        return success_results

    def handle_error_response(self, role_users):
        pass

    @staticmethod
    def __find_unassigned_users(user_ids, user_roles) -> List[str]:
        requested_ids = OrderedSet[str](user_ids)
        assigned_ids = OrderedSet[str]([ru.userId for ru in user_roles])
        return requested_ids.remove_all(assigned_ids).to_list()

    @staticmethod
    def __create_unmatched_result(rch, permission_name):
        return EntityMigrationResult(
            status="not matched",
            entityName="role-capability(set)",
            entityId=f"Role: {rch.roleName} -> {rch.roleId}\nPS: {permission_name}",
            reason=f"Failed to find capability or capability set by PS name: {permission_name}",
        )

    @staticmethod
    def _create_success_result(ru, user_id) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability_set(ru, user_id, "success")

    @staticmethod
    def _create_skipped_result(ru, user_id) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_users(ru, user_id, "skipped")
