from typing import List
from typing import OrderedDict as OrdDict
from typing import Tuple

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.errors import HttpCallResult, HttpReqErr
from folio_upm.dto.eureka import Capability, RoleUsers
from folio_upm.dto.results import AnalysisResult, AnalyzedRole, EurekaMigrationResult
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PagedDataLoader, PartitionedDataLoader


class EurekaService(metaclass=SingletonMeta):
    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("EurekaService initialized.")
        self._client = EurekaClient()

    def migrate_to_eureka(self, result: AnalysisResult) -> EurekaMigrationResult:
        self._log.info("Eureka migration started...")
        migration_result = EurekaMigrationResult(
            roleUsers=self.__create_roles(result.roles),
            # self.__assign_role_caps_by_ps(result.roleCapabilities)
            # self.__assign_role_users(result.roleUsers)
        )
        return migration_result

    def __create_roles(self, analyzed_roles: OrdDict[str, AnalyzedRole]):
        self._log.info("Creating %s role(s)...", len(analyzed_roles))
        role_names = [ar.role.name for ar in analyzed_roles.values() if ar.role.name]
        data_loader = PartitionedDataLoader(
            "roles", role_names, self._client.find_roles_by_query, self.__any_match_by_name
        )
        loaded_roles = data_loader.load()
        existing_role_names = set([role.name for role in loaded_roles])
        load_rs = []
        for ar in analyzed_roles.values():
            role = ar.role
            role_name = role.name
            if not role_name:
                self._log.error("Role name cannot be empty, skipping role creation for role: %s", role.id)
                load_rs.append(HttpCallResult.for_role(role, "skipped", "role name is empty"))
                continue
            if role_name not in existing_role_names:
                try:
                    created_role = self._client.post_role(role)
                    load_rs.append(HttpCallResult.for_role(created_role, "success"))
                    self._log.info("Role is created: id=%s, name=%s", created_role.id, role_name)
                except requests.HTTPError as e:
                    resp = e.response
                    error = HttpReqErr(message=str(e), status=resp.status_code, responseBody=resp.text)
                    request_result = HttpCallResult.for_role(role, "error", "Failed to perform request", error)
                    load_rs.append(request_result)
                    self._log.error("Failed to create role '%s': %s", role_name, e)
            else:
                self._log.info("Role '%s' already exists, skipping creation.", role_name)
                load_rs.append(HttpCallResult.for_role(role, "skipped", "already exists"))
        return load_rs

    def __assign_role_users(self, role_users: List[RoleUsers]):
        self._log.info("Assigning users to roles...")
        for role_id, user_ids in role_users:
            self._log.info("Assigning users to role: %s...", role_id)
            self._client.post_role_users(role_id, user_ids)
            self._log.info("Users assigned to role: %s...", role_id)

    def __assign_role_caps_by_ps(self, role_capabilities: List[RoleCapabilitiesHolder]):
        self._log.info("Assigning capabilities/capability-sets by permission names to roles...")
        for role_caps in role_capabilities:
            rc = role_caps.roleId
            # todo: indentify data-sets for capability assignment
            permissions = role_caps.capabilities
            self.__assign_role_capabilities()
        pass

    def __assign_role_capabilities(self, role_id: str, permissions: List[str]):
        self._log.info("Assigning capabilities to roles...")
        capabilities = self.__find_capabilities(permissions)
        all_capability_ids = [capability.id for capability in capabilities]
        capability_ids_tuple = self.__find_capability_ids_tuple(role_id, all_capability_ids)
        if capability_ids_tuple[0]:
            msg_template = "Assigning capabilities to role: %s, capabilityIds=%s..."
            self._log.info(msg_template, role_id, capability_ids_tuple[1])
            self._client.post_role_capabilities(role_id, capability_ids_tuple[0])
        else:
            msg_template = "No unassigned capabilities found for role: %s, capabilityIds=%s"
            self._log.info(msg_template, role_id, capability_ids_tuple[1])

    def __assign_role_capability_sets(self, role_id: str, permissions: List[str]):
        self._log.info("Assigning capability sets to roles...")
        capability_sets = self.__find_capability_sets(permissions)
        all_cset_ids = [capability_set.id for capability_set in capability_sets]
        cset_ids_tuple = self.__find_cset_ids_tuple(role_id, all_cset_ids)
        if cset_ids_tuple[0]:
            msg_template = "Assigning capability sets to role: %s, capabilityIds=%s..."
            self._log.info(msg_template, role_id, cset_ids_tuple[1])
            self._client.post_role_capability_sets(role_id, cset_ids_tuple[0])
        else:
            self._log.info(f"No unassigned capability sets found for role: {role_id}")

    def __find_capability_ids_tuple(self, role_id: str, capability_ids: List[str]) -> Tuple[List[str], List[str]]:
        self._log.info("Retrieving unassigned capability ids for role: %s...", role_id)
        data_loader_func = self._client.find_role_capabilities
        data_loader = PagedDataLoader("roles-capabilities", data_loader_func, f"roleId=={role_id}")
        role_capabilities = data_loader.load()
        assigned_capability_ids = set([c.capabilityId for c in role_capabilities])
        return (
            [capability_id for capability_id in capability_ids if capability_id not in assigned_capability_ids],
            [capability_id for capability_id in capability_ids if capability_id in assigned_capability_ids],
        )

    def __find_cset_ids_tuple(self, role_id: str, capability_set_ids: List[str]) -> Tuple[List[str], List[str]]:
        self._log.info("Retrieving unassigned capability set ids for role: %s...", role_id)
        data_loader_func = self._client.find_role_capability_sets
        data_loader = PagedDataLoader("roles-capability-sets", data_loader_func, f'roleId=="{role_id}"')
        role_capabilities = data_loader.load()
        assigned_capability_set_ids = set([c.capabilityId for c in role_capabilities])
        return (
            [cset_id for cset_id in capability_set_ids if cset_id not in assigned_capability_set_ids],
            [cset_id for cset_id in capability_set_ids if cset_id in assigned_capability_set_ids],
        )

    def __find_capabilities(self, ps_names: List[str]) -> List[Capability]:
        self._log.info("Retrieving capabilities by permission names: %s...", ps_names)
        loader = self.__find_capabilities_by_query
        data_loader = PartitionedDataLoader("capabilities", ps_names, loader, self.build_any_match_query)
        return data_loader.load()

    def __find_capabilities_by_query(self, query: str) -> List[Capability]:
        return self._client.find_capabilities(query)

    def __find_capability_sets(self, ps_names: List[str]) -> List[Capability]:
        self._log.info("Retrieving capability sets by permission names: %s...", ps_names)
        loader = self._client.find_capability_sets
        data_loader = PartitionedDataLoader("capability-sets", ps_names, loader, self.build_any_match_query)
        return data_loader.load()

    def __find_capability_sets_by_query(self, query: str) -> List[Capability]:
        return self._client.find_capability_sets(query)

    @staticmethod
    def __any_match_by_name(values: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("name", values)

    @staticmethod
    def build_any_match_query(permission_names: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("permission", permission_names)
