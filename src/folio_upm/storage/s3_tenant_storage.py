from typing_extensions import override

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.s3_client import UpmS3Client
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils


class S3TenantStorage(TenantStorage, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(False)
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("S3TenantStorage initialized.")
        self._storage = UpmS3Client()

    @override
    def _get_json_gz(self, json_name) -> dict | None:
        file_key = self._get_file_key(json_name, self._json_gz_ext)
        self._log.info(f"Downloading JSON from s3: {file_key}...")
        object_body = self._storage.read_object(file_key)
        return object_body and JsonUtils.from_json_gz(object_body)

    @override
    def _save_json_gz(self, object_name, object_data: dict):
        file_key = self._get_file_key(object_name, self._json_gz_ext)
        self._log.info(f"Uploading data to s3: {file_key}...")
        if not object_data:
            self._log.warning(f"Data is empty, skipping upload for {file_key}.")
            return

        self._storage.upload_file(file_key, JsonUtils.to_json_gz(object_data))

    def upload_xlsx(self, file_name): ...

    def __download_xlsx(self, file_name): ...

    def _save_xlsx(self, object_name, object_data):
        pass
