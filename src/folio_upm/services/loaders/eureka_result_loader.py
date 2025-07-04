from folio_upm.dto.results import EurekaLoadResult
from folio_upm.storage.tenant_storage_service import TenantStorageService
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class EurekaResultLoader:

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._tenant_storage_service = TenantStorageService()
        self._eureka_load_result = self.__load_eureka_capabilities()

    def get_load_result(self) -> EurekaLoadResult:
        return self._eureka_load_result

    def __load_eureka_capabilities(self) -> EurekaLoadResult:
        eureka_load_result_dict = self._tenant_storage_service.get_object("eureka-capabilities", "json.gz")
        if eureka_load_result_dict is not None:
            self._log.info("Tenant-related eureka capabilities found in storage.")
            return EurekaLoadResult(**eureka_load_result_dict)

        ref_capabilities_file_path = Env().get_env("REF_CAPABILITIES_FILE_KEY")
        if not ref_capabilities_file_path:
            self._log.info("Reference capabilities file path is not set, returning empty value...")
            return EurekaLoadResult()

        self._log.info("Loading reference capabilities from: '%s' ...", ref_capabilities_file_path)
        ref_eureka_load_result_dict = self._tenant_storage_service.get_ref_object_by_key(ref_capabilities_file_path)
        if ref_eureka_load_result_dict is None:
            self._log.warn("Reference capabilities file not found: '%s'", ref_capabilities_file_path)
            return EurekaLoadResult()
        return EurekaLoadResult(**ref_eureka_load_result_dict)
