from io import BytesIO
from typing import Optional

from openpyxl.workbook import Workbook
from typing_extensions import override

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.file_utils import FileUtils
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
        return json_bytes_buffer and JsonUtils.from_json_gz(json_bytes_buffer)

    @override
    def _find_latest_object_by_name(self, prefix: str) -> Optional[str]:
        return FileUtils.find_latest_key_by_prefix(self._out_folder, prefix)

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
        FileUtils.create_directory_safe(self._out_folder)
        file = f"{self._out_folder}/{file_key}"
        FileUtils.write_binary_data(file, binary_data)

    def __read_binary_data(self, file_key) -> BytesIO | None:
        file = f"{self._out_folder}/{file_key}"
        return FileUtils.read_binary_data(file)
