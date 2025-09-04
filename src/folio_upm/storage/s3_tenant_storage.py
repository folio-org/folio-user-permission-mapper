import io
from typing import Any, Callable, Optional

from openpyxl.workbook import Workbook
from typing_extensions import override

from folio_upm.model.cls_support import SingletonMeta
from folio_upm.storage.s3_storage import S3Storage
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.xlsx_utils import XlsxUtils


class S3TenantStorage(TenantStorage, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__()
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("S3TenantStorage initialized.")
        self._storage = S3Storage()

    @override
    def _get_json_gz(self, object_name: str) -> Optional[Any]:
        return self.__get_s3_object(object_name, lambda body: JsonUtils.from_json_gz(body))

    @override
    def _find_latest_object_by_name(self, prefix: str, object_ext: str) -> Optional[str]:
        return self._storage.find_latest_key_by_prefix(prefix, object_ext)

    @override
    def _save_json_gz(self, object_name: str, object_data: Any) -> None:
        self._log.debug(f"Uploading compressed JSON to s3: {object_name}...")
        self._storage.upload_file(object_name, JsonUtils.to_json_gz(object_data))
        self._log.info(f"Compressed JSON saved to s3: {object_name}")

    @override
    def _get_xlsx(self, object_name: str) -> Optional[io.BytesIO]:
        return self.__get_s3_object(object_name, lambda body: body)

    @override
    def _save_xlsx(self, object_name: str, object_data: Workbook) -> None:
        self._log.debug(f"Uploading xlsx file to s3: {object_name}...")
        self._storage.upload_file(object_name, XlsxUtils.get_bytes(object_data))
        self._log.info(f"xlsx file saved to s3: {object_name}")

    def __get_s3_object(self, file_key: str, mapper_func: Callable[[Any], Any]) -> Any:
        self._log.debug(f"Downloading file from s3: {file_key}...")
        object_body = self._storage.read_object(file_key)
        if object_body is not None:
            try:
                return mapper_func(object_body)
            finally:
                object_body.close()
        self._log.warning("Object is not found in S3 bucket: '%s'", file_key)
        return None
