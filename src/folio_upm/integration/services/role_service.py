from typing import OrderedDict as OrdDict, Set

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.migration import EntityMigrationResult, HttpReqErr
from folio_upm.dto.results import AnalyzedRole
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader


class RoleService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")
        self._client = EurekaClient()

    def create_roles(self, analyzed_roles: OrdDict[str, AnalyzedRole]):
        self._log.info("Creating %s role(s)...", len(analyzed_roles))
        existing_role_names = self.__find_existing_roles(analyzed_roles)
        load_rs = []
        for ar in list(analyzed_roles.values()):
            load_rs.append(self.__verify_and_create_role(ar, existing_role_names))
        return load_rs

    def __find_existing_roles(self, analyzed_roles):
        role_names = [ar.role.name for ar in analyzed_roles.values() if ar.role.name]
        loader_func = self._client.find_roles_by_query
        data_loader = PartitionedDataLoader("roles", role_names, loader_func, CqlQueryUtils.any_match_by_name)
        loaded_roles = data_loader.load()
        existing_role_names = set([role.name for role in loaded_roles])
        return existing_role_names

    def __verify_and_create_role(self, ar: AnalyzedRole, existing_role_names: Set[str]) -> EntityMigrationResult:
        role = ar.role
        role_name = role.name
        if not role_name:
            self._log.error("Role name cannot be empty, skipping role creation for role: %s", role.id)
            return EntityMigrationResult.for_role(role, "skipped", "role name is empty")
        if role_name not in existing_role_names:
            return self.__create_role_safe(role)
        else:
            self._log.info("Role '%s' already exists, skipping creation.", role_name)
            return EntityMigrationResult.for_role(role, "skipped", "already exists")

    def __create_role_safe(self, role):
        role_name = role.name
        try:
            self._log.debug("Creating role: name='%s'...", role.name)
            created_role = self._client.post_role(role)
            self._log.info("Role is created: id=%s, name=%s", created_role.id, role_name)
            return EntityMigrationResult.for_role(created_role, "success", f"Role created: {created_role.id}")
        except requests.HTTPError as e:
            self._log.warn("Failed to create role '%s': %s", role_name, e)
            resp = e.response
            error = HttpReqErr(message=str(e), status=resp.status_code, responseBody=resp.text)
            status = "skipped" if resp.status_code == 409 else "error"
            return EntityMigrationResult.for_role(role, status, "Failed to perform request", error)
