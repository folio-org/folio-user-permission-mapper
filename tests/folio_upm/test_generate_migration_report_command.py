import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from click.testing import CliRunner
from minio_test_helper import MinioTestHelper  # type: ignore[import-error]

from folio_upm.cli import cli
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils.json_utils import JsonUtils


class BaseTest:

    @pytest.fixture(scope="function")
    def migration_report_s3_object(self, minio_client, test_tenant_id, test_s3_bucket) -> Generator[str, None, None]:
        file_path = Path("../resources/test-data/eureka-migration-report.json")
        migration_data = JsonUtils().read_string_safe(Path(os.path.dirname(__file__)) / file_path)
        curr_datetime = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S%f")
        object_name = f"{test_tenant_id}/{test_tenant_id}-migration-report-distributed-{curr_datetime}.json.gz"
        yield from MinioTestHelper.put_jsongz_object(minio_client, test_s3_bucket, object_name, migration_data)


class TestGenerateMigrationReportCommand(BaseTest):

    def test_generate_migration_report(
        self,
        capsys: CaptureFixture,
        s3_environment,
        test_tenant_env,
        migration_report_s3_object,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["generate-migration-report"], color=True)
            assert result.exit_code == 0
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")

            result_object = S3TenantStorage().find_object("migration-report-distributed", "xlsx")
            assert result_object is not None
