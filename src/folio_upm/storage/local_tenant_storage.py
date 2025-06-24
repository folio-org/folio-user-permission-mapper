import os
from typing import Any

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.service_utils import ServiceUtils
from folio_upm.utils.upm_env import Env


class LocalTenantStorage(TenantStorage, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(Env().get_bool("OVERRIDE_LOCAL_DATA", default_value=False))
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LocalTenantStorage initialized.")
        self._tmp_folder = ".temp"

    def _get_json_gz(self, json_name):
        return None

    def _save_json_gz(self, object_name, object_data: dict):
        extension = "json.gz"
        file_key = self._get_file_key(object_name, extension)
        self._log.info(f"Uploading data to s3: {file_key}...")
        if not object_data:
            self._log.warning(f"Data is empty, skipping upload for {file_key}.")
            return

        compressed_json = JsonUtils.to_json_gz(object_data)
        self._storage.upload_file(file_key, compressed_json)

    def _save_xlsx(self, file_name, object_data: Any):
        file_key = self._get_file_key(file_name, self._xlsx_ext)
        with open(f"{self._tmp_folder}/{file_key}", "wb") as f:
            object_data.seek(0)
            f.write(object_data.getbuffer())
            object_data.seek(0)

    def _get_xlsx(self, file_name):
        return None

    def __create_temp_directory(self):
        directory = f"{self._tmp_folder}/{self._tenant_id}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def write_local_data(analysis_report, store_locally, xlsx_report):
        tenant_id = Env().get_tenant_id()
        directory = f".temp/{tenant_id}"
        with open(f"{directory}/{tenant_id}-analysis-report-{report_time}.xlsx", "wb") as f:
            f.write(xlsx_report.getbuffer())
            xlsx_report.seek(0)

    def _save_xlsx(self, object_name, object_data):
        pass
