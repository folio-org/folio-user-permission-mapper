import os
from pathlib import Path
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from assert_utils import Assert  # type: ignore[import-error]
from click.testing import CliRunner
from minio import Minio
from wiremock.resources.mappings import Mapping
from wiremock_test_helper import WireMockTestHelper  # type: ignore[import-error]

from folio_upm.cli import cli
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils.json_utils import JsonUtils


class BaseTest:

    @pytest.fixture(scope="function")
    def eureka_roles_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-roles.json")

    @pytest.fixture(scope="function")
    def eureka_capabilities_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-capabilities.json")

    @pytest.fixture(scope="function")
    def eureka_capability_sets_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-capability-sets.json")

    @pytest.fixture(scope="function")
    def eureka_roles_users_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-roles-users.json")

    @pytest.fixture(scope="function")
    def eureka_role_capabilities_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-roles-capabilities.json")

    @pytest.fixture(scope="function")
    def eureka_role_capability_sets_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-roles-capability-sets.json")

    @pytest.fixture(scope="function")
    def eureka_users_capabilities_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-users-capabilities.json")

    @pytest.fixture(scope="function")
    def eureka_users_capability_sets_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-users-capability-sets.json")


class TestCollectCapabilitiesCommand(BaseTest):

    def test_collect_capabilities(
        self,
        capsys: CaptureFixture,
        test_tenant_env,
        s3_environment,
        eureka_wiremock_env,
        eureka_login_http_mock,
        eureka_capabilities_http_mock,
        eureka_capability_sets_http_mock,
        eureka_roles_http_mock,
        eureka_roles_users_http_mock,
        eureka_role_capabilities_http_mock,
        eureka_role_capability_sets_http_mock,
        eureka_users_capabilities_http_mock,
        eureka_users_capability_sets_http_mock,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["collect-capabilities"], color=True)
            assert result.exit_code == 0
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")

            result_object = S3TenantStorage().find_object("eureka-capabilities", "json.gz")
            file_path = Path("../resources/results/jsons/eureka-capabilities.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
