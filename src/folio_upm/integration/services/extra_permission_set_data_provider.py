from pathlib import Path
from typing import Any, Dict, List

from folio_upm.integration.clients.github.github_file_client import GithubFileClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.eureka_permission_remapping_data import ExtraPermissionSetData
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env


class ExtraPermissionSetDataProvider(metaclass=SingletonMeta):
    """Service for managing GitHub file operations."""

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Initializing ExtraPermissionSetDataProvider")
        self._github_client = GithubFileClient()
        self._default_branch = "master"
        self._default_github_base_url = "https://raw.githubusercontent.com"
        self._permission_ref_data_fn = "permissions-to-view-edit-permissions.json"
        self._capability_ref_data_fn = "capabilities-to-view-edit-capabilities.json"

    def load_extra_permission_set_data(self) -> ExtraPermissionSetData:
        """
        Loads the Eureka permission remapping data from either a local file or a remote GitHub repository.

        If the environment variable `LOCAL_MOD_ROLES_KC_FILE_LOCATION` is set, the method loads the data from the
        specified local path. Otherwise, it fetches the data from the GitHub repository using the configured base URL
        and branch.

        Returns:
            ExtraPermissionSetData: An object containing the remapped permissions and capabilities data.
        """

        local_mod_roles_kc_file_Location = Env().getenv("LOCAL_MOD_ROLES_KC_FILE_LOCATION")
        if local_mod_roles_kc_file_Location:
            self._log.debug("Loading extra permission set data from filesystem...")
            self._log.debug("Using local mod-roles-keycloak files from: %s", local_mod_roles_kc_file_Location)
            extra_ps_names_dir_path = Path(local_mod_roles_kc_file_Location)
            result_object = self.__read_local_data(extra_ps_names_dir_path)
            self._log.info("Extra permission set data loaded from local path: %s", extra_ps_names_dir_path)
            return result_object

        self._log.debug("Loading extra permission set data from GitHub...")
        github_base_url = self.__get_github_base_url()
        mod_roles_kc_branch = self.__get_mod_roles_kc_branch()
        folio_repository = "folio-org/mod-roles-keycloak/"
        folder = "src/main/resources/permissions-view-edit-mapping"
        base_url = f"{github_base_url}/{folio_repository}/refs/heads/{mod_roles_kc_branch}/{folder}"
        ps_ref_data = self._github_client.load_object_safe(f"{base_url}/permissions/{self._permission_ref_data_fn}")
        cs_ref_data = self._github_client.load_object_safe(f"{base_url}/capabilities/{self._capability_ref_data_fn}")
        result_object = self.__create_result_object(ps_ref_data, cs_ref_data)
        self._log.info("Extra permission set data loaded from github: %s", base_url)
        return result_object

    def __read_local_data(self, extra_ps_names_dir_path: Path) -> ExtraPermissionSetData:
        permission_ref_data = JsonUtils().read_string_safe(extra_ps_names_dir_path / self._permission_ref_data_fn)
        capability_ref_data = JsonUtils().read_string_safe(extra_ps_names_dir_path / self._capability_ref_data_fn)
        return self.__create_result_object(permission_ref_data, capability_ref_data)

    @staticmethod
    def __create_result_object(ps_data: Dict[str, List[str]], cs_data: Dict[str, List[str]]) -> ExtraPermissionSetData:
        """
        Create a result object from the given data.

        Args:
            ps_data (Dict[str, List[str]]): Dictionary containing Okapi's permissions names
            cs_data (Dict[str, List[str]]): Dictionary containing Eureka's permissions names

        Returns:
            EurekaPermissionRemappingData object
        """
        return ExtraPermissionSetData(
            viewPermissions=ps_data.get("viewPermissions", []),
            editPermissions=ps_data.get("editPermissions", []),
            viewCapabilities=cs_data.get("viewCapabilities", []),
            editCapabilities=cs_data.get("editCapabilities", []),
        )

    def __get_validated_object(self, data: Any):
        result = {}
        for key, value in data.items():
            if not isinstance(value, list):
                error_msg = "Invalid type for key '%s': expected list (skipping it), got %s: %s"
                self._log.error(error_msg, key, type(value), value)
                continue
            result[key] = value
        return result

    def __get_github_base_url(self):
        value = Env().getenv("GITHUB_BASE_URL", self._default_github_base_url)
        return value.strip() if value else self._default_github_base_url

    def __get_mod_roles_kc_branch(self):
        value = Env().getenv("MOD_ROLES_KC_BRANCH", self._default_branch)
        return value.strip() if value else self._default_branch
