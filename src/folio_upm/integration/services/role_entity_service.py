import re
from typing import Any, List

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Role
from folio_upm.dto.migration import EntityMigrationResult, HttpReqErr
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.cql_query_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader
from folio_upm.utils.ordered_set import OrderedSet


class RoleEntityService(metaclass=SingletonMeta):

    def __init__(self, resource_name: str):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleEntityService initialized.")
        self._name = resource_name
        self._client = EurekaClient()

    def find_by_ps_names(self, permission_names: List[str]) -> List[Any]:
        qb = CqlQueryUtils.any_match_by_permission
        set_loader = self._load_entities_by_ps_names
        return PartitionedDataLoader(self._name, permission_names, set_loader, qb).load()

    def assign_to_role(self, role: Role, entities: List):
        if not entities:
            self._log.info("No entities provided for role '%s': %s.", role.name, self._name)
            return []

        entity_ids = [entity.id for entity in entities]
        self._log.info("Assigning '%s' to role '%s': %s", self._name, role.name, entity_ids)
        try:
            return self.__assign_entity_ids_to_role(role, entity_ids)
        except requests.HTTPError as err:
            return self.__handle_error_response(role, entity_ids, err)

    def update(self, role: Role, entity_ids: List[str]):
        if not entity_ids:
            self._log.info("No entities provided for role '%s': %s.", role.name, self._name)
        try:
            self._update_role_entities(role.id, entity_ids)
            return self._create_update_result(role.id, entity_ids)
        except requests.HTTPError as err:
            msg_template = "Failed to update role-%s for role '%s': %s, responseBody: %s"
            self._log.warning(msg_template, self._name, role.name, err, err.response.text)
            resp = err.response
            error_rs = HttpReqErr(message=str(err), status=resp.status_code, responseBody=resp.text)
            return self._create_error_update_result(role, entity_ids, error_rs)

    def __assign_entity_ids_to_role(self, role, entity_ids):
        role_id = role.id
        assigned_resources = self._assign_entities_to_role(role_id, entity_ids)
        unassigned_ids = self.__find_unassigned_entities(entity_ids, assigned_resources)
        success_results = [self._create_success_result(role, entity_id) for entity_id in entity_ids]
        if unassigned_ids:
            self._log.warning("Unassigned %s entities for role '%s': %s", self._name, role.name, unassigned_ids)
            unassigned_ids_result = [self._create_skipped_result(role, i) for i in unassigned_ids]
            return unassigned_ids_result + success_results
        return success_results

    def __handle_error_response(self, role, entity_ids, err):
        role_name = role.name
        resp = err.response
        response_text = resp.text or ""
        if resp.status_code == 400 and "Relation already exists for role" in response_text:
            self._log.info("Handling existing entities in role-%s for role '%s'", self._name, role_name)
            return self.__handle_existing_entities_response(role, entity_ids, err)
        msg_template = "Failed to create role-%s for role '%s': %s, responseBody: %s"
        self._log.warning(msg_template, self._name, role_name, err, err.response.text)
        return self.__create_error_result(role, entity_ids, err)

    def __handle_existing_entities_response(self, role, entity_ids, err):
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

    def __find_unassigned_entities(self, entity_ids: List[str], assigned_entities_resp) -> List[str]:
        requested_ids = OrderedSet[str](entity_ids)
        assigned_ids = OrderedSet[str]([self._get_result_entity_id(e) for e in assigned_entities_resp])
        return requested_ids.remove_all(assigned_ids).to_list()

    def __create_error_result(self, role, entity_ids, err):
        resp = err.response
        error = HttpReqErr(message=str(err), status=resp.status_code, responseBody=resp.text)
        return [self._create_error_result(role, entity_id, error) for entity_id in entity_ids]

    def __create_error_result2(self, err):
        resp = err.response
        return


    def _get_result_entity_id(self, entity) -> str:
        pass

    def _load_entities_by_ps_names(self, query) -> List[Any]:
        pass

    def _assign_entities_to_role(self, role_id, entity_ids) -> List[Any]:
        pass

    def _create_success_result(self, role, entity_id) -> EntityMigrationResult:
        pass

    def _create_update_result(self, role, entity_ids) -> EntityMigrationResult:
        pass

    def _create_skipped_result(self, role, entity_id) -> EntityMigrationResult:
        pass

    def _create_error_result(self, role, entity_id, error) -> EntityMigrationResult:
        pass

    def _update_role_entities(self, role_id, entity_ids) -> None:
        pass

    def _create_error_update_result(self, role, entity_ids, error) -> EntityMigrationResult:
        pass
