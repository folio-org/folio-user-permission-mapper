import re
from typing import Dict, List, Optional

import requests

from folio_upm.integration.clients.eureka.user_roles_client import UserRolesClient
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.integration.services.role_service import RoleService
from folio_upm.model.analysis.analyzed_user_roles import AnalyzedUserRoles
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.role import Role
from folio_upm.model.report.detailed_http_error import DetailedHttpError
from folio_upm.model.report.http_request_result import HttpRequestResult
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class RoleUsersService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")
        self._client = EurekaClient()
        self._roles_service = RoleService()
        self._role_user_service = UserRolesClient()

    def assign_users(self, analyzed_user_role_records: List[AnalyzedUserRoles]) -> List[HttpRequestResult]:
        migration_result = list[HttpRequestResult]()
        total_user_roles = len(analyzed_user_role_records)
        self._log.info("Total user roles to assign: %s", total_user_roles)
        user_roles_counter = 1
        for ur in analyzed_user_role_records:
            migration_result += self.__assign(ur)
            self._log.info("User roles processed: %s/%s", user_roles_counter, total_user_roles)
            user_roles_counter += 1
        self._log.info("User roles to assigned: %s", user_roles_counter)
        return migration_result

    def __assign(self, analyzed_user_roles: AnalyzedUserRoles) -> List[HttpRequestResult]:
        user_id = analyzed_user_roles.userId
        role_names = analyzed_user_roles.roleNames
        if not role_names:
            self._log.warning(f"No roles provided for user: user={user_id}")
            return []

        if analyzed_user_roles.skipRoleAssignment:
            self._log.info(f"Skipping role assignment for user: {user_id}")
            _result = list[HttpRequestResult]()
            for role_name in role_names:
                role_placeholder = Role(name=role_name, id=None)
                _result.append(self._create_skipped_result(user_id, role_placeholder, "Too many roles"))
            return _result

        found_roles = self._roles_service.find_roles_by_names(role_names)
        found_role_names = self.__get_role_names(found_roles)
        unmatched_roles = OrderedSet[str](role_names).remove_all(found_role_names).to_list()
        role_ids = [r.id for r in found_roles if r if r.id]
        roles_by_ids = self.__collect_roles_by_id(found_roles)
        if unmatched_roles:
            self._log.warning("Roles not found by name, skipping user assignment %s -> %s", user_id, unmatched_roles)
            return [HttpRequestResult.user_role_not_found_result(user_id, r) for r in unmatched_roles]
        try:
            return self.__assign_role_users(user_id, role_ids, roles_by_ids)
        except requests.HTTPError as err:
            return self.__handle_error_response(user_id, role_ids, roles_by_ids, err)

    def __assign_role_users(self, user_id: str, role_ids: List[str], roles_dict: dict[str, Role]) -> List:
        self._log.debug("Assigning user to roles '%s': %s", user_id, role_ids)
        created_ur = self._role_user_service.post_user_roles(user_id, role_ids)
        success_results = [self.__create_success_result(ur.userId, roles_dict.get(ur.roleId)) for ur in created_ur]

        unassigned_ids = self.__find_unassigned_role_ids(roles_dict, created_ur)
        if unassigned_ids:
            self._log.warning("Unassigned roles found for user '%s': %s", user_id, unassigned_ids)
            unassigned_ids_result = [self._create_skipped_result(user_id, roles_dict.get(i)) for i in unassigned_ids]
            return unassigned_ids_result + success_results

        self._log.info("User assigned to roles '%s': %s", user_id, role_ids)
        return success_results

    def __handle_error_response(
        self, user_id: str, role_ids: List[str], roles_by_id: Dict[str, Role], err: requests.HTTPError
    ) -> List[HttpRequestResult]:
        resp = err.response
        response_text = resp.text or ""
        if resp.status_code == 400 and "Relations between user and roles already exists" in response_text:
            self._log.info("Handling existing user-role relations for user '%s'", user_id)
            return self.__handle_existing_roles_response(user_id, role_ids, roles_by_id, err)
        msg_template = "Failed to create user-roles for user '%s': %s, responseBody: %s"
        self._log.warning(msg_template, user_id, err, err.response.text)
        return self.__create_error_results(user_id, role_ids, roles_by_id, err)

    def __handle_existing_roles_response(
        self, user_id: str, role_ids: List[str], roles_by_id: Dict[str, Role], err: requests.HTTPError
    ) -> List[HttpRequestResult]:
        response_text = err.response.text or ""
        pattern = r"roles: \[([a-f0-9\- ,]+)]"
        match = re.search(pattern, response_text)
        if match:
            assigned_role_ids = [cap.strip() for cap in match.group(1).split(",")]
            unassigned_ids = OrderedSet[str](role_ids).remove_all(assigned_role_ids).to_list()
            assigned_ids_result = [
                self._create_skipped_result(user_id, roles_by_id.get(role_id)) for role_id in assigned_role_ids
            ]
            if unassigned_ids:
                return assigned_ids_result + self.__assign_role_users(user_id, unassigned_ids, roles_by_id)
            return assigned_ids_result
        self._log.warning("Failed to extract existing entity IDs from response: %s", response_text)
        return self.__create_error_results(user_id, role_ids, roles_by_id, err)

    @staticmethod
    def __find_unassigned_role_ids(expected_role_ids, user_roles) -> List[str]:
        requested_ids = OrderedSet[str](expected_role_ids)
        assigned_ids = OrderedSet[str]([ur.roleId for ur in user_roles])
        return requested_ids.remove_all(assigned_ids).to_list()

    @staticmethod
    def __create_unmatched_result(rch, permission_name):
        return HttpRequestResult(
            status="not_matched",
            srcEntityName="role-capability(set)",
            srcEntityId=f"Role: {rch.roleName} -> {rch.roleId}\nPS: {permission_name}",
            reason=f"Failed to find capability or capability set by PS name: {permission_name}",
        )

    @staticmethod
    def __create_error_result(user_id, role: Optional[Role], error: DetailedHttpError) -> HttpRequestResult:
        return HttpRequestResult.for_user_role(role, user_id, "error", "Failed to perform request", error)

    @staticmethod
    def __create_error_results(
        user_id: str, role_ids: List[str], roles_by_id: Dict[str, Role], err: requests.HTTPError
    ) -> List[HttpRequestResult]:
        response = err.response
        error = DetailedHttpError(message=str(err), status=response.status_code, responseBody=response.text)
        return [RoleUsersService.__create_error_result(user_id, roles_by_id.get(r), error) for r in role_ids]

    @staticmethod
    def __create_success_result(user_id: str, role: Optional[Role]) -> HttpRequestResult:
        return HttpRequestResult.for_user_role(role, user_id, "success")

    @staticmethod
    def _create_skipped_result(user_id, role: Optional[Role], reason: str = "already exists") -> HttpRequestResult:
        return HttpRequestResult.for_user_role(role, user_id, "skipped", reason)

    @staticmethod
    def __get_role_names(roles: List[Role]) -> List[str]:
        return [r.name for r in roles if r]

    def __collect_roles_by_id(self, roles: List[Role]) -> Dict[str, Role]:
        roles_by_ids = {}
        for role in roles:
            role_id = role.id
            if role_id is None:
                self._log.warning("Failed to find role ID for role: %s", role.name)
                continue
            if role_id not in roles_by_ids:
                roles_by_ids[role_id] = role
        return roles_by_ids
