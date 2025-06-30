import re
from collections import OrderedDict
from typing import List

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Role, RoleUsers, UserRoles
from folio_upm.dto.migration import EntityMigrationResult, HttpReqErr
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.integration.services.role_service import RoleService
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class RoleUsersService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")
        self._client = EurekaClient()
        self._roles_service = RoleService()

    def assign_users(self, user_roles: List[UserRoles]) -> List[EntityMigrationResult]:
        migration_result = []
        for ur in user_roles:
            migration_result += self.__assign(ur)
        return migration_result

    def __assign(self, ur: UserRoles) -> List[EntityMigrationResult]:
        user_id = ur.userId
        requested_role_names = ur.roles
        if not requested_role_names:
            self._log.warning(f"No roles provided for user: user={user_id}")
            return []

        found_roles = self._roles_service.find_roles_by_names(requested_role_names)
        found_role_names = self.__get_role_names(found_roles)
        unmatched_roles = OrderedSet[str](requested_role_names).remove_all(found_role_names).to_list()
        role_ids = [r.id for r in found_roles if r]
        roles_by_ids = self.__collect_roles_by_id(found_roles)
        if unmatched_roles:
            self._log.warning("Roles not found by name, skipping user assignment: %s", unmatched_roles)
            return [EntityMigrationResult.role_not_found_result(r) for r in unmatched_roles]
        try:
            return self.__assign_role_users(user_id, role_ids, roles_by_ids)
        except requests.HTTPError as err:
            return self.__handle_error_response(user_id, role_ids, roles_by_ids, err)

    def __assign_role_users(self, user_id: str, role_ids: list[str], roles_dict: dict[str, Role]) -> List:
        self._log.debug("Assigning user to roles '%s': %s", user_id, role_ids)
        created_ur = self._client.post_user_roles(user_id, role_ids)
        success_results = [self.__create_success_result(ur.userId, roles_dict.get(ur.roleId)) for ur in created_ur]

        unassigned_ids = self.__find_unassigned_role_ids(roles_dict, created_ur)
        if unassigned_ids:
            self._log.warning("Unassigned roles found for user '%s': %s", user_id, unassigned_ids)
            unassigned_ids_result = [self._create_skipped_result(user_id, roles_dict.get(i)) for i in unassigned_ids]
            return unassigned_ids_result + success_results

        self._log.info("User assigned to roles '%s': %s", user_id, role_ids)
        return success_results

    def __handle_error_response(self, user_id, role_ids, roles_by_id: dict[str, Role], err):
        resp = err.response
        self._log.warn("Failed to create user-roles for user '%s': %s", user_id, err)
        response_text = resp.text or ""
        if resp.status_code == 400 and "Relations between user and roles already exists" in response_text:
            self._log.info("Handling existing user-role relations for user '%s'", user_id)
            return self.__handle_existing_roles_response(user_id, role_ids, roles_by_id, err)
        return self.__create_err_result(user_id, role_ids, roles_by_id, err)

    def __handle_existing_roles_response(self, user_id, role_ids, roles_by_id, err):
        response_text = err.response.text or ""
        pattern = r"roles: \[([a-f0-9\- ,]+)]"
        match = re.search(pattern, response_text)
        if match:
            assigned_role_ids = [cap.strip() for cap in match.group(1).split(",")]
            unassigned_ids = OrderedSet(role_ids).remove_all(assigned_role_ids).to_list()
            assigned_ids_result = [self._create_skipped_result(user_id, roles_by_id.get(i)) for i in assigned_role_ids]
            if unassigned_ids:
                return assigned_ids_result + self.__assign_role_users(user_id, unassigned_ids, roles_by_id)
            return assigned_ids_result
        self._log.warn("Failed to extract existing entity IDs from response: %s", response_text)
        return self.__create_err_result(user_id, role_ids, roles_by_id, err)

    @staticmethod
    def __find_unassigned_role_ids(expected_role_ids, user_roles) -> List[str]:
        requested_ids = OrderedSet[str](expected_role_ids)
        assigned_ids = OrderedSet[str]([ur.roleId for ur in user_roles])
        return requested_ids.remove_all(assigned_ids).to_list()

    @staticmethod
    def __create_unmatched_result(rch, permission_name):
        return EntityMigrationResult(
            status="not_matched",
            entityName="role-capability(set)",
            entityId=f"Role: {rch.roleName} -> {rch.roleId}\nPS: {permission_name}",
            reason=f"Failed to find capability or capability set by PS name: {permission_name}",
        )

    @staticmethod
    def __create_err_result(user_id, role_ids, roles_by_id, err):
        response = err.response
        error = HttpReqErr(message=str(err), status=response.status_code, responseBody=response.text)
        return [RoleUsersService.__create_error_migration_result(user_id, roles_by_id.get(r), error) for r in role_ids]

    @staticmethod
    def __create_success_result(user_id, role) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_users(role, user_id, "success")

    @staticmethod
    def __create_error_migration_result(user_id, role, error) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_users(role, user_id, "error", "Failed to perform request", error)

    @staticmethod
    def _create_skipped_result(user_id, role) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_users(role, user_id, "skipped", "already exists")

    @staticmethod
    def __get_role_names(roles: List[Role]) -> List[str]:
        return [r.name for r in roles if r]

    @staticmethod
    def __collect_roles_by_id(roles: List[Role]):
        roles_by_ids = OrderedDict()
        for role in roles:
            if role.id not in roles_by_ids:
                roles_by_ids[role.id] = role
        return roles_by_ids

    # Relations between user and roles already exists
