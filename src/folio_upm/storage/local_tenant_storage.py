import os
from io import BytesIO

from openpyxl.workbook import Workbook
from typing_extensions import override

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env
from folio_upm.utils.xlsx_utils import XlsxUtils


class LocalTenantStorage(TenantStorage, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(Env().get_bool("OVERRIDE_LOCAL_DATA", default_value=False))
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LocalTenantStorage initialized.")
        self._out_folder = ".temp"
        self._skip_json_gz = True

    @override
    def _get_json_gz(self, json_name):
        file_key = self._get_file_key(json_name, self._json_gz_ext, include_ts=False)
        if not self.__file_exists(file_key):
            self._log.warn("File '%s/%s' does not exist.", self._out_folder, file_key)
            return None

        with open(f"{self._out_folder}/{file_key}", "rb") as f:
            return JsonUtils.from_json_gz(f)

    @override
    def _save_json_gz(self, file_name, object_data: dict):
        if self._skip_json_gz:
            return
        data_bytes = JsonUtils.to_json_gz(object_data)
        self.__save_file_with_latest_included(file_name, data_bytes, self._json_gz_ext)

    @override
    def _save_xlsx(self, file_name, object_data: Workbook):
        data_bytes = XlsxUtils.get_bytes(object_data)
        self.__save_file_with_latest_included(file_name, data_bytes, self._xlsx_ext)

    @override
    def _get_xlsx(self, file_name):
        return None

    def __save_file_with_latest_included(self, file_name, object_data, file_ext: str):
        file_key = self._get_file_key(file_name, file_ext)
        self.__write_binary_data(file_key, object_data)

    def __write_binary_data(self, file_key, binary_data: BytesIO):
        self.__create_temp_directory()
        file = f"{self._out_folder}/{file_key}"
        self._log.debug("Saving file: '%s' ...", file)

        if self.__file_exists(file_key):
            self._log.debug("File '%s' already exists, overriding it", file)

        with open(file, "wb") as f:
            binary_data.seek(0)
            f.write(binary_data.getbuffer())
            self._log.debug("Data saved to file '%s'", file)

    def __create_temp_directory(self):
        directory = f"{self._out_folder}/{self._tenant_id}"
        if not os.path.exists(directory):
            self._log.debug("Creating directory: %s", directory)
            os.makedirs(directory)
        return directory

    def __file_exists(self, file_name):
        return os.path.exists(f"{self._out_folder}/{file_name}")
