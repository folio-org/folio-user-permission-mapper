import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from click.testing import CliRunner

from assert_utils import Assert  # type: ignore[import-error]
from folio_upm.cli import cli
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils.json_utils import JsonUtils
from minio_test_helper import MinioTestHelper
from wiremock_test_helper import WireMockTestHelper  # type: ignore[import-error]

_tenant_id = "okapi_test"


class BaseTest:

    @pytest.fixture(scope="function", autouse=False)
    def okapi_permissions_s3_object(self, minio_client, test_s3_bucket) -> Generator[str, None, None]:
        file_path = Path("../resources/test-data/okapi-permissions.json")
        okapi_capabilities = JsonUtils().read_string_safe(Path(os.path.dirname(__file__)) / file_path)
        fk = f"{_tenant_id}/{_tenant_id}-okapi-permissions-{datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S%f")}.json.gz"
        yield from MinioTestHelper.with_jsongz_object(minio_client, test_s3_bucket, fk, okapi_capabilities)

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


class TestGenerateReportCommand(BaseTest):

    def test_generate_report(
        self,
        capsys: CaptureFixture,
        okapi_permissions_s3_object,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["generate-report"], color=True)
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")
            assert result.exit_code == 0

            result_object = S3TenantStorage().find_object("eureka-migration-data-distributed", "json.gz")
            file_path = Path("../resources/results/jsons/expected_eureka_migration_data.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
