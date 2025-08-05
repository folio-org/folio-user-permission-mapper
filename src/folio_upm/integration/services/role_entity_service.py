import re
from typing import List, Union

import requests

from folio_upm.integration.clients.eureka.absract_role_entity_client import AbstractRoleEntityClient
from folio_upm.integration.clients.eureka.abstract_entity_client import AbstractEntityClient
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.role import Role
from folio_upm.model.eureka.role_capability import RoleCapability
from folio_upm.model.eureka.role_capability_set import RoleCapabilitySet
from folio_upm.model.report.detailed_http_error import DetailedHttpError
from folio_upm.model.report.http_request_result import HttpRequestResult
from folio_upm.utils import log_factory
from folio_upm.utils.cql_query_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader
from folio_upm.utils.ordered_set import OrderedSet


class RoleEntityService(metaclass=SingletonMeta):

    def __init__(
        self,
        resource_name: str,
        entity_name: str,
        entity_client: AbstractEntityClient[Union[Capability, CapabilitySet]],
        role_entity_client: AbstractRoleEntityClient[Union[RoleCapability, RoleCapabilitySet]],
    ):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleEntityService initialized.")
        self._name = resource_name
        self._entity_name = entity_name
        self._entity_client = entity_client
        self._role_entity_client = role_entity_client
        self._client = EurekaClient()

    def find_by_ps_names(self, permission_names: List[str]) -> Union[List[Capability], List[CapabilitySet]]:
        """
        Find entities (Capabilities or CapabilitySets) by permission names.

        :param permission_names: List of permission names to search for.
        :return: List of entities (Capabilities or CapabilitySets) that match the permission names.
        """
        qb = CqlQueryUtils.any_match_by_permission
        entity_loader = self._entity_client.find_by_query
        return PartitionedDataLoader(self._name, permission_names, entity_loader, qb).load()

    def assign_to_role(
        self, role: Role, entities: Union[List[Capability], List[CapabilitySet]]
    ) -> List[HttpRequestResult]:
        """
         Assign entities to a role.

        :param role: The role to which entities will be assigned.
        :param entities: List of entities (Capabilities or CapabilitySets) to assign to the role.
        :return: List of HttpRequestResult indicating the result of the assignment operation.
        """
        if not entities:
            self._log.info("No entities provided for role '%s': %s.", role.name, self._name)
            return []

        entity_ids = [entity.id for entity in entities]
        self._log.info("Assigning '%s' to role '%s': %s", self._name, role.name, entity_ids)
        try:
            return self.__assign_entity_ids_to_role(role, entity_ids)
        except requests.HTTPError as err:
            return self.__handle_error_response(role, entity_ids, err)

    def update(self, role: Role, entity_ids: List[str]) -> List[HttpRequestResult]:
        """
        Update the role with the provided entity IDs.

        :param role: The role to update.
        :param entity_ids: List of entity IDs to update the role with.
        :return: List of HttpRequestResult indicating the result of the update operation.
        """
        try:
            self._log.debug("Updating role-%s: '%s' with: %s", self._name, role.name, entity_ids)
            self._role_entity_client.update_role_entity(role.id, entity_ids)
            self._log.debug("Successfully updated role-%s: '%s' with: %s", self._name, role.name, entity_ids)
            return self._create_success_update_results(role, entity_ids)
        except requests.HTTPError as err:
            msg_template = "Failed to update role-%s for role '%s': %s, responseBody: %s"
            self._log.warning(msg_template, self._name, role.name, err, err.response.text)
            resp = err.response
            error_rs = DetailedHttpError(message=str(err), status=resp.status_code, responseBody=resp.text)
            return [self._create_error_update_result(role, entity_ids, error_rs)]

    def __assign_entity_ids_to_role(self, role: Role, entity_ids: List[str]):
        role_id = role.id
        self._log.debug("Assigning role-%s: '%s' with: %s", self._name, role.name, entity_ids)
        assigned_resources = self._role_entity_client.create_role_entity(role_id, entity_ids)
        unassigned_ids = self.__find_unassigned_entities(entity_ids, assigned_resources)
        success_results = [self._create_success_result(role, entity_id) for entity_id in entity_ids]
        if unassigned_ids:
            self._log.warning("Unassigned %s entities for role '%s': %s", self._name, role.name, unassigned_ids)
            unassigned_ids_result = [self._create_skipped_result(role, entity_id) for entity_id in unassigned_ids]
            return unassigned_ids_result + success_results
        self._log.debug("Successfully assigned role-'%s': '%s' with: %s", self._name, role.name, entity_ids)
        return success_results

    def __handle_error_response(self, role: Role, entity_ids: List[str], err):
        role_name = role.name
        resp = err.response
        response_text = resp.text or ""
        if resp.status_code == 400 and "Relation already exists for role" in response_text:
            self._log.info("Handling existing entities in role-%s for role '%s'", self._name, role_name)
            return self.__handle_existing_entities_response(role, entity_ids, err)
        msg_template = "Failed to create role-%s for role '%s': %s, responseBody: %s"
        self._log.warning(msg_template, self._name, role_name, err, err.response.text)
        return self.__create_error_result(role, entity_ids, err)

    def __handle_existing_entities_response(self, role: Role, entity_ids: List[str], err):
        response_text = err.response.text or ""
        pattern = r"=\[([a-f0-9\- ,]+)\]"
        match = re.search(pattern, response_text)
        if match:
            assigned_ids = [cap.strip() for cap in match.group(1).split(",")]
            unassigned_ids = OrderedSet(entity_ids).remove_all(assigned_ids).to_list()
            assigned_ids_result = [self._create_skipped_result(role, i) for i in assigned_ids]
            if unassigned_ids:
                return assigned_ids_result + self.__assign_entity_ids_to_role(role, unassigned_ids)
            return assigned_ids_result
        self._log.warning("Failed to extract existing entity IDs from response: %s", response_text)
        return self.__create_error_result(role, entity_ids, err)

    def __find_unassigned_entities(
        self, entity_ids: List[str], assigned_entities_resp: List[Union[RoleCapability, RoleCapabilitySet]]
    ) -> List[str]:
        requested_ids = OrderedSet[str](entity_ids)
        resp_ids = [self._role_entity_client.get_target_entity_id(e) for e in assigned_entities_resp]
        assigned_ids = OrderedSet[str](resp_ids)
        return requested_ids.remove_all(assigned_ids).to_list()

    def __create_error_result(self, role, entity_ids, err):
        resp = err.response
        error = DetailedHttpError(message=str(err), status=resp.status_code, responseBody=resp.text)
        return [self._create_error_result(role, entity_id, error) for entity_id in entity_ids]

    def _create_success_result(self, role: Role, entity_id: str) -> HttpRequestResult:
        return HttpRequestResult(
            status="success",
            srcEntityName="role",
            srcEntityId=role.id,
            srcEntityDisplayName=role.name,
            tarEntityName=self._entity_name,
            tarEntityId=entity_id,
        )

    def _create_success_update_results(self, role: Role, entity_ids: List[str]) -> List[HttpRequestResult]:
        result = []
        for capability_id in entity_ids:
            result.append(
                HttpRequestResult(
                    status="success",
                    srcEntityName="role",
                    srcEntityId=role.id,
                    srcEntityDisplayName=role.name,
                    tarEntityName=self._entity_name,
                    tarEntityId=capability_id,
                )
            )
        return result

    def _create_skipped_result(self, role: Role, entity_id: str) -> HttpRequestResult:
        return HttpRequestResult(
            status="skipped",
            srcEntityName="role",
            srcEntityId=role.id,
            srcEntityDisplayName=role.name,
            tarEntityName=self._entity_name,
            tarEntityId=entity_id,
            reason="already exists",
        )

    def _create_error_result(self, role: Role, entity_id: str, error) -> HttpRequestResult:
        return HttpRequestResult(
            status="error",
            srcEntityName="role",
            srcEntityId=role.id,
            srcEntityDisplayName=role.name,
            tarEntityName=self._entity_name,
            tarEntityId=entity_id,
            reason="Failed to perform request",
            error=error,
        )

    def _create_error_update_result(self, role: Role, entity_ids: List[str], error) -> HttpRequestResult:
        return HttpRequestResult(
            status="error",
            srcEntityName="role",
            srcEntityId=role.id,
            srcEntityDisplayName=role.name,
            tarEntityName=self._entity_name,
            tarEntityId="\n".join(entity_ids),
            reason="Failed to perform request",
            error=error,
        )
