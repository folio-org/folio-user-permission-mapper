import os

import pytest

from folio_upm.dto.eureka_load_strategy import CONSOLIDATED, DISTRIBUTED, EurekaLoadStrategy
from folio_upm.dto.results import AnalysisResult, EurekaLoadResult, OkapiLoadResult
from folio_upm.services.load_result_analyzer import LoadResultAnalyzer
from folio_upm.utils import log_factory
from folio_upm.utils.file_utils import FileUtils
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env

_dir_name = os.path.dirname(__file__)
_log = log_factory.get_logger("TestDistributedLoadResultAnalyzer")


class TestDataProvider:

    @staticmethod
    def get_data():
        return [
            pytest.param("1user-1ps.json", id="Single role assignment"),
            pytest.param("1user-nested-ps.json", id="Single role assignment with nested okapi permission set"),
            pytest.param("2user-1ps.json", id="2 users share a simple role"),
            pytest.param("2user-2ps.json", id="2 users share 2 same permission sets => 2 users with 2 same roles"),
            pytest.param("3user-many-ps+shared-ps.json", id="shared ps between 3 users + individual permissions"),
            pytest.param("simple-nesting.json", id="Simple nesting (assignments on diff levels)"),
            pytest.param("deep-nesting.json", id="Deep nesting"),
            pytest.param("mixed-role-feature-assignment.json", id="Mixed role/feature assignments"),
            pytest.param("circular-references.json", id="Circular references (A contains B contains C contains A)"),
            pytest.param("duplicates-at-different-levels.json", id="Duplicate permissions at different nesting levels"),
            pytest.param("empty-ps-in-middle.json", id="Empty permission sets"),
            pytest.param("permission+permission-sets.json", id="Permission set + permissions"),
            pytest.param("0users-permission-set.json", id="Permission set without user"),
        ]


class TestDistributedLoadResultAnalyzer:

    @pytest.fixture(autouse=True)
    def set_environment_variables(self):
        os.environ["TENANT_ID"] = "test_tenant"
        yield
        del os.environ["TENANT_ID"]
        Env().getenv_cached.cache_clear()
        Env().require_env_cached.cache_clear()

    @pytest.mark.parametrize("filename", TestDataProvider.get_data())
    def test_consolidated_strategy(self, filename):
        os.environ["EUREKA_ROLE_LOAD_STRATEGY"] = CONSOLIDATED.get_name()
        self.perform_test(filename, CONSOLIDATED)
        del os.environ["EUREKA_ROLE_LOAD_STRATEGY"]

    @pytest.mark.parametrize("filename", TestDataProvider.get_data())
    def test_distributed_strategy(self, filename):
        os.environ["EUREKA_ROLE_LOAD_STRATEGY"] = DISTRIBUTED.get_name()
        self.perform_test(filename, DISTRIBUTED)
        del os.environ["EUREKA_ROLE_LOAD_STRATEGY"]

    @staticmethod
    def perform_test(filename: str, strategy: EurekaLoadStrategy):
        okapi_load_rs = _Utils.okapi_load_result(f"../../resources/okapi/{filename}")
        analyzer = LoadResultAnalyzer(okapi_load_rs, None)
        actual = analyzer.get_results()
        expected_file_key = f"../../resources/results/{strategy.get_name()}/{filename}"
        expected_dict = JsonUtils.read_file(_Utils.get_file_key(expected_file_key))
        Assert.compare_json_str(expected_dict, _Utils.to_comparable_json(actual))


class Assert:

    @staticmethod
    def compare_json_str(given: dict, expected: dict):
        given_json = JsonUtils.to_json(given, remove_none_values=True)
        expected_json = JsonUtils.to_json(expected, remove_none_values=True)
        if given_json != expected_json:
            message = (
                f"Comparison failed for JSON objects:\n"
                f"    Actual:   {given_json}\n"
                f"    Expected: {expected_json}"
            )
            pytest.fail(message)


class _Utils:

    @staticmethod
    def to_comparable_json(rs: AnalysisResult) -> dict:
        role_capabilities = _Utils.__get_role_capabilities(rs)

        return {
            "roles": [{"name": r.role.name, "description": r.role.description} for r in rs.roles.values()],
            "roleUsers": [x.model_dump(by_alias=True) for x in rs.roleUsers],
            "roleCapabilities": role_capabilities,
        }

    @staticmethod
    def eureka_load_result(filename) -> EurekaLoadResult:
        json_dict = JsonUtils.read_file(filename)
        return EurekaLoadResult(**json_dict)

    @staticmethod
    def okapi_load_result(filename) -> OkapiLoadResult:
        json_dict = _Utils.read_file(filename)
        return OkapiLoadResult(**json_dict)

    @staticmethod
    def read_file(filename):
        full_file_path = _Utils.get_file_key(filename)
        if not FileUtils.exists(full_file_path):
            pytest.fail(f"Failed to find required file: {filename}")
        json_dict = JsonUtils.read_file(full_file_path)
        return json_dict

    @staticmethod
    def get_file_key(filename: str) -> str:
        return str(os.path.join(_dir_name, filename))

    @staticmethod
    def __get_role_capabilities(rs):
        role_capabilities = {}
        for rch in rs.roleCapabilities:
            role_name = rch.roleName
            for ch in rch.capabilities:
                if role_name not in role_capabilities:
                    role_capabilities[role_name] = []
                role_capabilities[role_name].append(ch.permissionName)
        role_capabilities = [{"roleName": role_name, "ps": pss} for role_name, pss in role_capabilities.items()]
        return role_capabilities
