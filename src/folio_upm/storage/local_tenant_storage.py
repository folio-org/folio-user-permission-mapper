from io import BytesIO
from typing import Any, Optional

from openpyxl.workbook import Workbook
from typing_extensions import override

from folio_upm.model.cls_support import SingletonMeta
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.file_utils import FileUtils
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.xlsx_utils import XlsxUtils


class LocalTenantStorage(TenantStorage, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__()
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LocalTenantStorage initialized.")
        self._out_folder = ".temp"

    @override
    def _get_json_gz(self, object_name: str) -> Optional[Any]:
        json_bytes_buffer = self.__read_binary_data(object_name)
        return json_bytes_buffer and JsonUtils.from_json_gz(json_bytes_buffer)

    @override
    def _find_latest_object_by_name(self, prefix: str, object_ext: str) -> Optional[str]:
        return FileUtils.find_latest_key_by_prefix(self._out_folder, prefix, object_ext)

    @override
    def _save_json_gz(self, object_name: str, object_data: Any) -> None:
        data_bytes = JsonUtils.to_json_gz(object_data)
        self.__save_file_with_latest_included(object_name, data_bytes)

    @override
    def _save_xlsx(self, object_name: str, object_data: Workbook) -> None:
        data_bytes = XlsxUtils.get_bytes(object_data)
        self.__save_file_with_latest_included(object_name, data_bytes)

    @override
    def _get_xlsx(self, object_name: str) -> Optional[BytesIO]:
        return self.__read_binary_data(object_name)

    def __save_file_with_latest_included(self, file_key, object_data):
        self.__write_binary_data(file_key, object_data)

    def __write_binary_data(self, file_key, binary_data: BytesIO):
        FileUtils.create_directory_safe(self._out_folder)
        file = f"{self._out_folder}/{file_key}"
        FileUtils.write_binary_data(file, binary_data)

    def __read_binary_data(self, file_key) -> Optional[BytesIO]:
        file = f"{self._out_folder}/{file_key}"
        return FileUtils.read_binary_data(file)
