import os
from datetime import datetime, UTC
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


class BaseTest:

    @pytest.fixture(scope="function")
    def migration_report_s3_object(self, minio_client, test_tenant_id, test_s3_bucket) -> Generator[str, None, None]:
        file_path = Path("../resources/test-data/eureka-cleanup-report.json")
        migration_data = JsonUtils().read_string_safe(Path(os.path.dirname(__file__)) / file_path)
        curr_datetime = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S%f")
        object_name = f"{test_tenant_id}/{test_tenant_id}-eureka-migration-report-distributed-{curr_datetime}.json.gz"
        yield from MinioTestHelper.put_jsongz_object(minio_client, test_s3_bucket, object_name, migration_data)

class TestGenerateCleanupReportCommand:

    def test_generate_cleanup_report(
        self,
        capsys: CaptureFixture,
        test_tenant_env,
        s3_environment,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["generate-cleanup-report"], color=True)
            assert result.exit_code == 0
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")

            result_object = S3TenantStorage().find_object("generate-report", "json.gz")
            file_path = Path("../resources/results/jsons/okapi-permissions.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
