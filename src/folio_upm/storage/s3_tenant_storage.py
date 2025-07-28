from typing import Any, Callable, Optional

from openpyxl.workbook import Workbook
from typing_extensions import override

from folio_upm.dto.cls_support import SingletonMeta
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
    def _get_json_gz(self, file_key) -> dict | None:
        return self.__get_s3_object(file_key, lambda body: JsonUtils.from_json_gz(body))

    @override
    def _find_latest_object_by_name(self, prefix: str, object_ext: str) -> Optional[str]:
        return self._storage.find_latest_key_by_prefix(prefix, object_ext)

    @override
    def _save_json_gz(self, file_key, object_data: dict):
        self._log.debug(f"Uploading compressed JSON to s3: {file_key}...")
        self._storage.upload_file(file_key, JsonUtils.to_json_gz(object_data))
        self._log.info(f"Compressed JSON saved to s3: {file_key}")

    @override
    def _get_xlsx(self, file_key) -> Workbook:
        return self.__get_s3_object(file_key, lambda body: body)

    @override
    def _save_xlsx(self, file_key, xlsx_bytes: Workbook):
        self._log.debug(f"Uploading xlsx file to s3: {file_key}...")
        self._storage.upload_file(file_key, XlsxUtils.get_bytes(xlsx_bytes))
        self._log.info(f"xlsx file saved to s3: {file_key}")

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
