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

    @pytest.fixture(autouse=True, scope="function")
    def setup_environment(self, minio_container, minio_client, test_s3_bucket):
        """Setup environment variables and clean up before each test."""
        minio_config = minio_container.get_config()

        os.environ["TENANT_ID"] = "okapi_test"
        os.environ["STORAGE_TYPE"] = "s3"
        os.environ["AWS_S3_ENDPOINT"] = f"http://{minio_config.get("endpoint")}"
        os.environ["AWS_S3_BUCKET"] = test_s3_bucket
        os.environ["AWS_S3_REGION"] = "us-east-1"
        os.environ["AWS_S3_REGION"] = "us-east-1"
        os.environ["AWS_ACCESS_KEY_ID"] = minio_config.get("access_key")
        os.environ["AWS_SECRET_ACCESS_KEY"] = minio_config.get("secret_key")

        yield
        env_vars_to_clean = [
            "EUREKA_URL",
            "EUREKA_ADMIN_USERNAME",
            "EUREKA_ADMIN_PASSWORD",
            "TENANT_ID",
            "STORAGE_TYPE",
            "AWS_S3_ENDPOINT",
            "AWS_S3_BUCKET",
            "AWS_S3_REGION",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
        ]

        for var in env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]


class TestRunEurekaMigrationCommand(BaseTest):

    def test_load_okapi_permissions(self, capsys: CaptureFixture):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["run-eureka-migration"], color=True)
            assert result.exit_code == 0
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")

            result_object = S3TenantStorage().find_object("generate-report", "json.gz")
            file_path = Path("../resources/results/jsons/expected_okapi_load_result.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
