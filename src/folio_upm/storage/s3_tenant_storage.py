from io import BytesIO
from typing import Any, Callable

from openpyxl.workbook import Workbook
from typing_extensions import override

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.s3_storage import S3Storage
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils


class S3TenantStorage(TenantStorage, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(False)
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("S3TenantStorage initialized.")
        self._storage = S3Storage()

    @override
    def _get_json_gz(self, object_name) -> dict | None:
        file_key = self._get_file_key(object_name, self._json_gz_ext)
        return self.__get_s3_object(file_key, lambda body: JsonUtils.from_json_gz(body))

    @override
    def _save_json_gz(self, object_name, object_data: dict):
        file_key = self._get_file_key(object_name, self._json_gz_ext)
        self._log.info(f"Uploading data to s3: {file_key}...")
        self._storage.upload_file(file_key, JsonUtils.to_json_gz(object_data))
        self._log.info(f"Data saved to s3: {file_key}")

    @override
    def _get_xlsx(self, object_name) -> Workbook:
        file_key = self._get_file_key(object_name, self._json_gz_ext)
        return self.__get_s3_object(file_key, lambda body: body)

    @override
    def _save_xlsx(self, object_name, xlsx_bytes: BytesIO):
        xlsx_bytes.seek(0)
        self._storage.upload_file(object_name, xlsx_bytes)

    def __get_s3_object(self, file_key: str, mapper_func: Callable[[Any], Any]) -> Any:
        self._log.info(f"Downloading file from s3: {file_key}...")
        object_body = self._storage.read_object(file_key)
        if object_body is not None:
            try:
                return mapper_func(object_body)
            finally:
                object_body.close()
        self._log.warn(f"Object is not found in S3 bucket: '%s'", file_key)
        return None
