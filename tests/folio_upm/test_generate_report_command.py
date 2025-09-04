import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from assert_utils import Assert  # type: ignore[import-error]
from click.testing import CliRunner
from minio_test_helper import MinioTestHelper  # type: ignore[import-error]

from folio_upm.cli import cli
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils.json_utils import JsonUtils


class BaseTest:

    @pytest.fixture(scope="function", autouse=False)
    def okapi_permissions_s3_object(self, minio_client, test_tenant_id, test_s3_bucket) -> Generator[str, None, None]:
        file_path = Path("../resources/test-data/okapi-permissions.json")
        okapi_capabilities = JsonUtils().read_string_safe(Path(os.path.dirname(__file__)) / file_path)
        curr_datetime = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S%f")
        fk = f"{test_tenant_id}/{test_tenant_id}-okapi-permissions-{curr_datetime}.json.gz"
        yield from MinioTestHelper.put_jsongz_object(minio_client, test_s3_bucket, fk, okapi_capabilities)


class TestGenerateReportCommand(BaseTest):

    def test_generate_report(
        self,
        capsys: CaptureFixture,
        s3_environment,
        test_tenant_env,
        eureka_role_load_strategy_env,
        okapi_permissions_s3_object,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["generate-report"], color=True)
            if result.exception:
                print(f"CLI failed as expected: {result.exception}")
            assert result.exit_code == 0

            result_object = S3TenantStorage().find_object("eureka-migration-data-distributed", "json.gz")
            file_path = Path("../resources/results/jsons/eureka-migration-data.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
