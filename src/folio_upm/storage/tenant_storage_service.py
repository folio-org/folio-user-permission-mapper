from typing import Any

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.storage.local_tenant_storage import LocalTenantStorage
from folio_upm.storage.s3_tenant_storage import S3TenantStorage
from folio_upm.storage.tenant_storage import TenantStorage
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class TenantStorageService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        storages = Env().get_enabled_storages()
        self._log.debug("Initializing TenantStorageService: storages: %s", storages)
        self._storage_names = [storage.lower() for storage in storages]
        self._storages = list[TenantStorage]()
        storages_set = set(storages)
        if "s3" in storages_set:
            self._storages.append(S3TenantStorage())
        if "local" in storages_set:
            self._storages.append(LocalTenantStorage())

    def save_object(self, object_name: str, object_ext: str, object_data: Any = None):
        for storage in self._storages:
            storage.save_object(object_name, object_ext, object_data)

    def find_object(self, object_name: str, object_ext: str):
        for storage in self._storages:
            found_object = storage.find_object(object_name, object_ext)
            if found_object is not None:
                return found_object
        return None

    def require_object(self, object_name: str, object_ext: str):
        for storage in self._storages:
            found_object = storage.find_object(object_name, object_ext)
            if found_object is not None:
                return found_object
        raise FileNotFoundError(f"File not found in storages {self._storage_names}: {object_name}.{object_ext}.")

    def find_object_by_key(self, object_key: str):
        for storage in self._storages:
            found_object = storage.find_object_by_key(object_key)
            if found_object is not None:
                return found_object
        return None
