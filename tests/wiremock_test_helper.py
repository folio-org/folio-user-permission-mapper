import logging
import os
from pathlib import Path
from typing import Dict, Generator

from wiremock.constants import Config
from wiremock.resources.mappings import Mapping
from wiremock.resources.mappings.resource import Mappings
from wiremock.resources.requests.resource import Requests
from wiremock.testing.testcontainer import WireMockContainer

from folio_upm.utils.json_utils import JsonUtils

_log = logging.getLogger(__name__)


class WireMockTestHelper:

    @staticmethod
    def get_container(secure=False, verbose=True):
        container = WireMockContainer(secure=secure)
        if verbose:
            container = container.with_cli_arg("--verbose", "")
        return container

    @staticmethod
    def set_base_url(wiremock):
        Config.base_url = wiremock.get_url("__admin")

    @staticmethod
    def set_mapping(file_path: str) -> Generator[Mapping, None, None]:
        mapping = WireMockTestHelper.create_mapping(file_path)
        yield mapping  # type: ignore[invalid-yield]
        WireMockTestHelper.delete_mapping(mapping)  # type: ignore[bad-argument-type]

    @staticmethod
    def create_mapping(file_path: str) -> Mapping:
        _log.info("Adding mapping from file: %s", file_path)
        json_mapping = WireMockTestHelper.get_json_mapping(Path(file_path))
        try:
            mapping_to_create = Mapping.from_dict(json_mapping)
            mapping = Mappings.create_mapping(mapping_to_create)
            return mapping  # type: ignore[bad-return]
        except Exception as error:
            raise AssertionError("Failed to create mapping from file %s: %s" % (file_path, error))

    @staticmethod
    def delete_mapping(mapping: Mapping):
        _log.info("Deleting mapping: %s ...", mapping.id)
        query_params = {"matchingStub": mapping.id}
        received_requests_pet_stub = Requests.get_all_received_requests(limit=100, parameters=query_params)
        if received_requests_pet_stub.meta.total < 1:  # type: ignore[missing-attribute]
            raise AssertionError(f"No matching requests were found for mapping: {mapping.request.to_json()}")  # type: ignore[missing-attribute]
        Mappings.delete_mapping(mapping.id)

    @staticmethod
    def delete_all_mappings() -> None:
        try:
            Mappings.delete_all_mappings()
        except Exception as error:
            _log.error("Failed to delete all mappings:  %s", error)
            raise error

    @staticmethod
    def get_json_mapping(file_path: Path) -> Dict:
        resources_path = Path(os.path.dirname(__file__)) / Path(f"./resources/stubs/{file_path}")
        file_content_json = JsonUtils().read_string_safe(resources_path)
        if not isinstance(file_content_json, dict):
            raise ValueError(f"File {resources_path} is empty or has invalid content type.")
        return file_content_json
