import os
from pathlib import Path
from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from click.testing import CliRunner
from wiremock.resources.mappings import Mapping

from assert_utils import Assert  # type: ignore[import-error]
from folio_upm.cli import cli
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.utils.json_utils import JsonUtils
from wiremock_test_helper import WireMockTestHelper  # type: ignore[import-error]


class BaseTest:

    @pytest.fixture(scope="function", autouse=False)
    def okapi_desc_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("okapi/200-get-module-descriptors.json")

    @pytest.fixture(scope="function", autouse=False)
    def ps_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-permission/200-get-permissions.json")

    @pytest.fixture(scope="function", autouse=False)
    def ps_expanded_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-permission/200-get-permissions-expanded.json")

    @pytest.fixture(scope="function", autouse=False)
    def user_ps_http_mock(self) -> Generator[Mapping, None, None]:
        yield from WireMockTestHelper.set_mapping("mod-permission/200-get-user-permissions.json")


class TestCollectPermissionsCommand(BaseTest):

    def test_collect_permissions(
        self,
        capsys: CaptureFixture,
        test_tenant_env,
        okapi_wiremock_env,
        s3_environment,
        okapi_login_http_mock,
        okapi_desc_http_mock,
        ps_http_mock,
        ps_expanded_http_mock,
        user_ps_http_mock,
    ):
        runner = CliRunner()
        with capsys.disabled() as _:
            result = runner.invoke(cli, ["collect-permissions"], color=True)

            if result.exception:
                print(f"CLI failed as expected: {result.exception}")
            assert result.exit_code == 0

            result_object = S3TenantStorage().find_object("okapi-permissions", "json.gz")
            file_path = Path("../resources/results/jsons/okapi-permissions.json")
            expected_fp = Path(os.path.dirname(__file__)) / file_path
            expected_object = JsonUtils().read_string_safe(expected_fp)
            Assert.compare_json_str(result_object, expected_object)
