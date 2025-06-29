from typing import List, Any

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.migration import HttpReqErr, EntityMigrationResult
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader
from folio_upm.utils.ordered_set import OrderedSet


class RoleEntityService(metaclass=SingletonMeta):

    def __init__(self, resource_name: str):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleEntityService initialized.")
        self._name = resource_name
        self._client = EurekaClient()

    def find_by_ps_names(self, permission_names):
        qb = CqlQueryUtils.any_match_by_name
        set_loader = self._load_entities_by_ps_names
        return PartitionedDataLoader(self._name, permission_names, set_loader, qb).load()

    def assign_to_role(self, rch: RoleCapabilitiesHolder, entities: List):
        if not entities:
            self._log.info("No entities provided for role '%s': %s.", rch.roleName, self._name)
            return []

        entity_ids = [entity.id for entity in entities]
        self._log.debug("Assigning entities to role '%s': %s: %s", self._name, rch.roleName, len(entity_ids))
        try:
            return self.__assign_entity_ids_to_role(rch, entity_ids)
        except requests.HTTPError as err:
            return self.__handle_error_response(rch, entity_ids, err)

    def __assign_entity_ids_to_role(self, rch, entity_ids):
        assigned_resources = self._assign_entities_to_role(rch.roleId, entity_ids)
        unassigned_ids = self.__find_unassigned_entities(entity_ids, assigned_resources)
        success_results = [self._create_success_result(rch, entity_id) for entity_id in entity_ids]
        if unassigned_ids:
            self._log.warning("Unassigned %s entities for role '%s': %s", self._name, rch.roleName, unassigned_ids)
            unassigned_ids_result = [self._create_skipped_result(rch, i) for i in unassigned_ids]
            return unassigned_ids_result + success_results
        return success_results

    def __handle_error_response(self, rch, entity_ids, err):
        self._log.warn("Failed to create role-%s '%s': %s: %s", self._name, rch.roleName, err)
        resp = err.response
        error = HttpReqErr(message=str(err), status=resp.status_code, responseBody=resp.text)
        return [self._create_error_result(rch, entity_id, error) for entity_id in entity_ids]

    def __find_unassigned_entities(self, entity_ids: List[str], assigned_entities_resp) -> List[str]:
        requested_ids = OrderedSet[str](entity_ids)
        assigned_ids = OrderedSet[str]([self._get_result_entity_id(e) for e in assigned_entities_resp])
        return requested_ids.remove_all(assigned_ids).to_list()

    def _get_result_entity_id(self, entity) -> str:
        pass

    def _load_entities_by_ps_names(self, query) -> List[Any]:
        pass

    def _assign_entities_to_role(self, role_id, entity_ids) -> List[Any]:
        pass

    def _create_success_result(self, rch, entity_id) -> EntityMigrationResult:
        pass

    def _create_skipped_result(self, rch, entity_id) -> EntityMigrationResult:
        pass

    def _create_error_result(self, rch, entity_id, error) -> EntityMigrationResult:
        pass
