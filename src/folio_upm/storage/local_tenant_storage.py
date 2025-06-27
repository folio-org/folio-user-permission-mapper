import logging
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

    @override
    def _get_json_gz(self, file_key):
        json_bytes_buffer = self.__read_binary_data(file_key)
        return JsonUtils.from_json_gz(json_bytes_buffer)

    @override
    def _save_json_gz(self, file_key, object_data: dict):
        data_bytes = JsonUtils.to_json_gz(object_data)
        self.__save_file_with_latest_included(file_key, data_bytes)

    @override
    def _save_xlsx(self, file_key, object_data: Workbook):
        data_bytes = XlsxUtils.get_bytes(object_data)
        self.__save_file_with_latest_included(file_key, data_bytes)

    @override
    def _get_xlsx(self, file_key):
        self._log.debug("LocalTenantStorage._get_xlsx is not available.")
        return None

    def __save_file_with_latest_included(self, file_key, object_data):
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

    def __read_binary_data(self, file_key) -> BytesIO | None:
        file = f"{self._out_folder}/{file_key}"
        if not os.path.exists(file):
            self._log.warn("File '%s' not found", file)
            return None

        with open(file, "rb") as f:
            file_bytes_buffer = BytesIO(f.read())
            file_bytes_buffer.seek(0)
            self._log.debug("Returning file: '%s'", file)
            return file_bytes_buffer

    def __create_temp_directory(self):
        directory = f"{self._out_folder}/{self._tenant_id}"
        if not os.path.exists(directory):
            self._log.debug("Creating directory: %s", directory)
            os.makedirs(directory)
        return directory

    def __file_exists(self, file_key):
        return os.path.exists(f"{self._out_folder}/{file_key}")
