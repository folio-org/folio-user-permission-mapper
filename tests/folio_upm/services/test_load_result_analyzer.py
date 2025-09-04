import os
from pathlib import Path

import pytest
from assert_utils import Assert  # type: ignore[import-error]

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
            pytest.param("0--1user-1ps.json", id="0. Single role assignment"),
            pytest.param("1--1user-nested-ps.json", id="1. Single role assignment with nested okapi permission set"),
            pytest.param("2--2user-1ps.json", id="2. 2 users share a simple role"),
            pytest.param("3--2user-2ps.json", id="3. 2 users share 2 same permission sets"),
            pytest.param("4--3user-many-ps+shared-ps.json", id="4. shared between 3 users + individual permissions"),
            pytest.param("5--simple-nesting.json", id="5. Simple nesting (assignments on diff levels)"),
            pytest.param("6--deep-nesting.json", id="6. Deep nesting"),
            pytest.param("7--mixed-role-feature-assignment.json", id="7. Mixed role/feature assignments"),
            pytest.param("8--circular-references.json", id="8. Circular references (A in B in C in A)"),
            pytest.param("9--duplicates-at-different-levels.json", id="9. Duplicate permissions at different levels"),
            pytest.param("10--empty-ps-in-middle.json", id="10. Empty permission sets"),
            pytest.param("11--permission+permission-sets.json", id="11. Permission set + permissions"),
            pytest.param("12--0users-permission-set.json", id="12. Permission set without user"),
            pytest.param("13--1user-1ps-extra-view-permissions.json", id="13. Single role (extra view permissions)"),
            pytest.param("14--1user-1ps-extra-edit-permissions.json", id="14. Single role (extra edit permissions)"),
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
    def __get_role_capabilities(rs: OkapiAnalysisResult):
        role_values_dict = {}
        for rch in rs.roleCapabilities:
            role_name = rch.roleName
            for ch in rch.capabilities:
                if role_name not in role_values_dict:
                    role_values_dict[role_name] = []
                if ch.permissionName is None:
                    role_values_dict[role_name].append({"type": "capability", "value": ch.name})
                else:
                    role_values_dict[role_name].append({"type": "permission", "value": ch.permissionName})

        return [
            {
                "roleName": role_name,
                "ps": [x.get("value") for x in entities if x.get("type") == "permission"],
                "capabilities": [x.get("value") for x in entities if x.get("type") == "capability"] or None,
            }
            for role_name, entities in role_values_dict.items()
        ]
