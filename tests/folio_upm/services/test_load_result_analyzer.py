import os
from pathlib import Path

import pytest

from assert_utils import Assert
from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.model.result.okapi_analysis_result import OkapiAnalysisResult
from folio_upm.model.types.eureka_load_strategy import CONSOLIDATED, DISTRIBUTED, EurekaLoadStrategy
from folio_upm.services.load_result_analyzer import LoadResultAnalyzer
from folio_upm.utils import log_factory
from folio_upm.utils.file_utils import FileUtils
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env

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
            pytest.param("1user-1ps-extra-view-permissions.json", id="Single role (extra view permissions)"),
            pytest.param("1user-1ps-extra-edit-permissions.json", id="Single role (extra edit permissions)"),
        ]


class TestLoadResultAnalyzer:

    @pytest.fixture(autouse=True, scope="class")
    def setup_clss(self, clear_singletons) -> None:
        pass

    @pytest.fixture(autouse=True)
    def set_environment_variables(self):
        os.environ["TENANT_ID"] = "test_tenant"
        yield
        del os.environ["TENANT_ID"]
        Env().getenv_cached.cache_clear()
        Env().require_env_cached.cache_clear()

    @pytest.fixture(autouse=True)
    def set_extra_ps_set_location(self):
        extra_ps_dir = _Utils.get_path_related_to_curr_dir(Path("../../resources/extra_ps"))
        os.environ["LOCAL_MOD_ROLES_KC_FILE_LOCATION"] = str(extra_ps_dir.resolve())
        yield
        del os.environ["LOCAL_MOD_ROLES_KC_FILE_LOCATION"]
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
        relative_path = Path(f"../../resources/okapi/{filename}")
        okapi_load_rs = OkapiLoadResult(**_Utils.read_file(relative_path))
        analyzer = LoadResultAnalyzer(okapi_load_rs, None)
        actual = analyzer.get_results()
        expected_file_key = Path(f"../../resources/results/{strategy.get_name()}/{filename}")
        expected_dict = JsonUtils().read_string_safe(_Utils.get_path_related_to_curr_dir(expected_file_key))
        Assert.compare_json_str(_Utils.to_comparable_json(actual), expected_dict)


class _Utils:

    @staticmethod
    def to_comparable_json(rs: OkapiAnalysisResult) -> dict:
        role_capabilities = _Utils.__get_role_capabilities(rs)

        return {
            "roles": [{"name": r.role.name, "description": r.role.description} for r in rs.roles.values()],
            "userRoles": [x.model_dump(by_alias=True) for x in rs.userRoles],
            "roleCapabilities": role_capabilities,
        }

    @staticmethod
    def read_file(filename: Path):
        full_file_path = _Utils.get_path_related_to_curr_dir(filename)
        if not FileUtils.exists(full_file_path):
            pytest.fail(f"Failed to find required file: {filename}")
        json_dict = JsonUtils().read_string_safe(full_file_path)
        return json_dict

    @staticmethod
    def get_path_related_to_curr_dir(filename: Path) -> Path:
        _current_dir = Path(os.path.dirname(__file__))
        return _current_dir / filename

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
