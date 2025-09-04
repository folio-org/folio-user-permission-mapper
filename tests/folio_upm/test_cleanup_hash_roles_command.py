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
    def cleanup_data_s3_object(self, minio_client, test_tenant_id, test_s3_bucket) -> Generator[str, None, None]:
        file_path = Path("../resources/test-data/hash-roles-cleanup-data.json")
        migration_data = JsonUtils().read_string_safe(Path(os.path.dirname(__file__)) / file_path)
        curr_datetime = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S%f")
        object_name = f"{test_tenant_id}/{test_tenant_id}-hash-roles-cleanup-data-distributed-{curr_datetime}.json.gz"
        yield from MinioTestHelper.put_jsongz_object(minio_client, test_s3_bucket, object_name, migration_data)

    @pytest.fixture(scope="function")
    def put_role_capabilities_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/204-put-hash-role-capabilities.json")

    @pytest.fixture(scope="function")
    def put_role_capability_sets_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/204-put-hash-role-capability-sets.json")

    @pytest.fixture(scope="function")
    def put_role2_capabilities_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/204-put-hash-role2-capabilities.json")

    @pytest.fixture(scope="function")
    def put_role2_capability_sets_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/204-put-hash-role2-capability-sets.json")

    @pytest.fixture(scope="function")
    def delete_hash_role2_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-roles-keycloak/204-delete-hash-role2.json")


class TestCleanupHashRolesCommand(BaseTest):

    def test_cleanup_hash_roles(
        self,
        capsys: CaptureFixture,
        test_tenant_env,
        s3_environment,
        cleanup_data_s3_object,
        eureka_wiremock_env,
        eureka_login_http_mock,
        put_role_capabilities_http_mock,
        put_role2_capabilities_http_mock,
        put_role_capability_sets_http_mock,
        put_role2_capability_sets_http_mock,
        delete_hash_role2_http_mock,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["cleanup-hash-roles"], color=True)
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")
            assert result.exit_code == 0

            result_object = S3TenantStorage().find_object("hash-roles-cleanup-report", "json.gz")
            file_path = Path("../resources/results/jsons/cleanup-report.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
