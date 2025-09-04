import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from assert_utils import Assert  # type: ignore[import-error]
from click.testing import CliRunner
from minio_test_helper import MinioTestHelper  # type: ignore[import-error]
from wiremock.resources.mappings import Mapping
from wiremock_test_helper import WireMockTestHelper  # type: ignore[import-error]

from folio_upm.cli import cli
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils.json_utils import JsonUtils


class BaseTest:

    @pytest.fixture(scope="function")
    def migration_data_s3_object(self, minio_client, test_tenant_id, test_s3_bucket) -> Generator[str, None, None]:
        file_path = Path("../resources/test-data/eureka-migration-data.json")
        migration_data = JsonUtils().read_string_safe(Path(os.path.dirname(__file__)) / file_path)
        curr_datetime = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S%f")
        object_name = f"{test_tenant_id}/{test_tenant_id}-eureka-migration-data-distributed-{curr_datetime}.json.gz"
        yield from MinioTestHelper.put_jsongz_object(minio_client, test_s3_bucket, object_name, migration_data)

    @pytest.fixture(scope="function")
    def get_roles_by_names_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-roles-by-names.json")

    @pytest.fixture(scope="function")
    def get_roles_by_names_empty_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-roles-by-names-empty.json")

    @pytest.fixture(scope="function")
    def get_capabilities_by_permission(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-capabilities-by-permission.json")

    @pytest.fixture(scope="function")
    def get_capabilities_by_name(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-capabilities-by-name.json")

    @pytest.fixture(scope="function")
    def get_capability_sets_by_permission(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-capability-sets-by-permission.json")

    @pytest.fixture(scope="function")
    def get_capability_sets_by_name(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/200-get-capability-sets-by-name.json")

    @pytest.fixture(scope="function")
    def post_role_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/201-post-test-role.json")

    @pytest.fixture(scope="function")
    def post_user_roles_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/201-post-roles-users.json")

    @pytest.fixture(scope="function")
    def post_role_capabilities_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/201-post-role-capabilities.json")

    @pytest.fixture(scope="function")
    def post_role_capability_sets_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/201-post-role-capability-sets.json")


class TestRunEurekaMigrationCommand(BaseTest):

    def test_run_eureka_migration(
        self,
        capsys: CaptureFixture,
        test_tenant_env,
        s3_environment,
        eureka_wiremock_env,
        migration_data_s3_object,
        eureka_login_http_mock,
        eureka_role_load_strategy_env,
        get_roles_by_names_http_mock,
        get_roles_by_names_empty_http_mock,
        get_capabilities_by_name,
        get_capabilities_by_permission,
        get_capability_sets_by_name,
        get_capability_sets_by_permission,
        post_role_http_mock,
        post_user_roles_http_mock,
        post_role_capabilities_http_mock,
        post_role_capability_sets_http_mock,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["run-eureka-migration"], color=True)
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")

            assert result.exit_code == 0

            result_object = S3TenantStorage().find_object("migration-report", "json.gz")
            file_path = Path("../resources/results/jsons/eureka-migration-report.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
