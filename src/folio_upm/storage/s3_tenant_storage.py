from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.s3_client import UpmS3Client
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env


class S3TenantStorage(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("TenantStorageService initialized.")
        self._storage = UpmS3Client()
        self._tenant_id = Env().get_tenant_id()

    def save_object(self, object_name, object_data, object_type="json.gz"):
        if object_type == "json.gz":
            self.save_json_gz(object_name, object_data)
        elif object_type == "xlsx":
            self.save_xlsx(object_name, object_data)
        else:
            self._log.warn("Unsupported object type: %s, file=%s", object_type, object_name)

    def download_json_gz(self, json_name):
        file_key = self.__get_file_key(json_name, "json.gz")
        self._log.info(f"Downloading JSON from s3: {file_key}...")
        object_body = self._storage.read_object(file_key)
        return JsonUtils.from_json_gz(object_body)

    def save_json_gz(self, object_name, object_data: dict):
        extension = "json.gz"
        file_key = self.__get_file_key(object_name, extension)
        self._log.info(f"Uploading data to s3: {file_key}...")
        if not object_data:
            self._log.warning(f"Data is empty, skipping upload for {file_key}.")
            return

        compressed_json = JsonUtils.to_json_gz(object_data)
        self._storage.upload_file(file_key, compressed_json)

    def upload_xlsx(self, file_name): ...

    def download_xlsx(self, file_name): ...

    def __get_file_key(self, file_name, extension):
        return f"{self._tenant_id}/{self._tenant_id}-{file_name}.{extension}"

    def save_xlsx(self, object_name, object_data):
        pass
