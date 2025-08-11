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


class TestCollectPermissionsIT:

    @pytest.fixture(autouse=True, scope="function")
    def setup_environment(self, wiremock_container, minio_container, minio_client, test_s3_bucket):
        """Setup environment variables and clean up before each test."""
        base_url = wiremock_container.get_url("")

        minio_config = minio_container.get_config()

        os.environ["OKAPI_URL"] = base_url
        os.environ["TENANT_ID"] = "okapi_test"
        os.environ["STORAGE_TYPE"] = "s3"
        os.environ["AWS_S3_ENDPOINT"] = f"http://{minio_config.get("endpoint")}"
        os.environ["AWS_S3_BUCKET"] = test_s3_bucket
        os.environ["AWS_S3_REGION"] = "us-east-1"
        os.environ["OKAPI_ADMIN_USERNAME"] = "test_okapi_admin"
        os.environ["OKAPI_ADMIN_PASSWORD"] = "test_okapi_password"
        os.environ["AWS_S3_REGION"] = "us-east-1"
        os.environ["AWS_ACCESS_KEY_ID"] = minio_config.get("access_key")
        os.environ["AWS_SECRET_ACCESS_KEY"] = minio_config.get("secret_key")

        yield
        env_vars_to_clean = [
            "OKAPI_URL",
            "TENANT_ID",
            "STORAGE_TYPE",
            "AWS_S3_ENDPOINT",
            "AWS_S3_BUCKET",
            "AWS_S3_REGION",
            "OKAPI_ADMIN_USERNAME",
            "OKAPI_ADMIN_PASSWORD",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
        ]

        for var in env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]

    @pytest.fixture(scope="function", autouse=False)
    def login_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-login/login-success.json")

    @pytest.fixture(scope="function", autouse=False)
    def okapi_desc_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("okapi/module-descriptors.json")

    @pytest.fixture(scope="function", autouse=False)
    def ps_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-permission/permissions.json")

    @pytest.fixture(scope="function", autouse=False)
    def ps_expanded_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-permission/permissions-expanded.json")

    @pytest.fixture(scope="function", autouse=False)
    def user_ps_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-permission/user-permissions.json")

    def test_load_okapi_permissions(
        self,
        minio_client: Minio,
        capsys: CaptureFixture,
        login_http_mock,
        wiremock_url,
        okapi_desc_http_mock,
        ps_http_mock,
        ps_expanded_http_mock,
        user_ps_http_mock,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["collect-permissions"], color=True)
            assert result.exit_code == 0
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")

            result_object = S3TenantStorage().find_object("okapi-permissions", "json.gz")
            file_path = Path("../resources/results/jsons/expected_okapi_load_result.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
