from typing import List, Set

import requests

from folio_upm.integration.clients.eureka.roles_client import RolesClient
from folio_upm.model.analysis.analyzed_role import AnalyzedRole
from folio_upm.model.cleanup.hash_role_cleanup_record import HashRoleCleanupRecord
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.role import Role
from folio_upm.model.report.detailed_http_error import DetailedHttpError
from folio_upm.model.report.http_request_result import HttpRequestResult
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import IterableUtils
from folio_upm.utils.cql_query_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader


class RoleService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleService initialized.")
        self._role_client = RolesClient()

    def find_role_by_name(self, role_name: str) -> Role | None:
        try:
            query = CqlQueryUtils.any_match_by_name([role_name])
            found_roles = self._role_client.find_by_query(query)
            return IterableUtils.first(found_roles)
        except requests.HTTPError as e:
            self._log.warning("Failed to find role by name '%s': %s", role_name, e)
            return None

    def find_roles_by_names(self, role_names: List[str]) -> List[Role]:
        qb = CqlQueryUtils.any_match_by_name
        loader = self._role_client.find_by_query
        return PartitionedDataLoader("roles", role_names, loader, qb).load()

    def create_roles(self, analyzed_roles: List[AnalyzedRole]):
        self._log.info("Creating %s role(s)...", len(analyzed_roles))
        existing_role_names = self.__find_existing_roles(analyzed_roles)
        load_rs = []
        for ar in analyzed_roles:
            load_rs.append(self.__verify_and_create_role(ar, existing_role_names))
        return load_rs

    def delete_roles(self, cleanup_records: List[HashRoleCleanupRecord]) -> List[HttpRequestResult]:
        roles_to_delete = [hash_role.role.id for hash_role in cleanup_records if self.__should_delete(hash_role)]
        self._log.debug("Removing roles: %s ...", roles_to_delete)
        remove_rs = []
        for role_id in roles_to_delete:
            remove_rs.append(self.__delete_role_safe(role_id))
        self._log.info("Roles removed successfully: %s", roles_to_delete)
        return remove_rs

    def __find_existing_roles(self, analyzed_roles):
        role_names = [ar.role.name for ar in analyzed_roles if ar.role.name]
        found_roles = self.find_roles_by_names(role_names)
        return set([role.name for role in found_roles])

    def __verify_and_create_role(self, ar: AnalyzedRole, existing_role_names: Set[str]) -> HttpRequestResult:
        role = ar.role
        role_name = role.name
        if ar.systemGenerated:
            self._log.info("Role '%s' is system-generated, skipping creation.", role_name)
            return HttpRequestResult.for_role(role, "skipped", "system generated")
        if role_name not in existing_role_names:
            return self.__create_role_safe(role)
        else:
            self._log.warning("Role '%s' already exists, skipping creation.", role_name)
            return HttpRequestResult.for_role(role, "skipped", "already exists")

    def __create_role_safe(self, role):
        role_name = role.name
        try:
            self._log.debug("Creating role: name='%s'...", role.name)
            role_to_create = Role(name=role_name, description=role.description or "")
            created_role = self._role_client.create_role(role_to_create)
            self._log.info("Role is created: id=%s, name='%s'", created_role.id, role_name)
            return HttpRequestResult.for_role(created_role, "success", "Role created successfully")
        except requests.HTTPError as e:
            resp = e.response
            error = DetailedHttpError(message=str(e), status=resp.status_code, responseBody=resp.text)
            status = "skipped" if resp.status_code == 409 else "error"
            if status == "skipped":
                self._log.info("Role '%s' already exists in 'mod-roles-keycloak'.", role_name)
            self._log.warning("Failed to create role '%s': %s, responseBody: %s", role_name, e, e.response.text)
            return HttpRequestResult.for_role(role, status, "Failed to perform request", error)

    def __delete_role_safe(self, role_id: str) -> HttpRequestResult:
        try:
            self._log.debug("Removing role: %s...", role_id)
            self._role_client.delete_role(role_id)
            self._log.info("Role is removed: %s", role_id)
            return HttpRequestResult.for_removed_role(role_id, "success", "Role removed successfully")
        except requests.HTTPError as e:
            resp = e.response
            error = DetailedHttpError(message=str(e), status=resp.status_code, responseBody=resp.text)
            status = "not_found" if resp.status_code == 404 else "error"
            self._log.warning("Failed to remove role '%s': %s, responseBody: %s", role_id, e, e.response.text)
            return HttpRequestResult.for_removed_role(role_id, status, "Failed to perform request", error)

    @staticmethod
    def __should_delete(role: HashRoleCleanupRecord) -> bool:
        return not role.capabilities and not role.capabilitySets
