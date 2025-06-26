from datetime import UTC, datetime
from typing import Any

from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class TenantStorage:

    _xlsx_ext = "xlsx"
    _json_ext = "json"
    _json_gz_ext = "json.gz"

    def __init__(self, override_reports: bool = False):
        self._tenant_id = Env().get_tenant_id()
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._override_reports = override_reports

    def save_object(self, object_name: str, object_ext: str, object_data: Any = None):
        file_key = self._get_file_key(object_name, object_ext)
        if object_ext == "json.gz":
            self._save_json_gz(file_key, object_data)
        elif object_ext == "json":
            self._save_json(file_key, object_data)
        elif object_ext == "xlsx":
            self._save_xlsx(file_key, object_data)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, object_name)

    def get_object(self, object_name: str, object_ext: str):
        file_key = self._get_file_key(object_name, object_ext)
        if object_ext == "json.gz":
            return self._get_json_gz(file_key)
        elif object_ext == "json":
            return self._get_json(file_key)
        elif object_ext == "xlsx":
            return self._get_xlsx(file_key)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, object_name)
            return None

    def get_ref_object_by_key(self, ref_key, object_ext):
        if object_ext.endswith("json.gz"):
            return self._get_json_gz(ref_key)
        elif object_ext.endswith("json"):
            return self._get_json(ref_key)
        elif object_ext.endswith("xlsx"):
            return self._get_xlsx(ref_key)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, ref_key)
        return None

    def _get_json(self, file_key: str):
        pass

    def _save_json(self, file_key: str, object_data: Any):
        pass

    def _get_json_gz(self, object_name: str):
        pass

    def _save_json_gz(self, object_name: str, object_data: Any):
        pass

    def _get_xlsx(self, object_name: str):
        pass

    def _save_xlsx(self, object_name: str, object_data: Any):
        pass

    def _get_file_key(self, file_name, extension, include_ts=True) -> str:
        file_name = f"{self._tenant_id}-{file_name}"
        if include_ts and self._override_reports:
            now = datetime.now(tz=UTC)
            file_name += f"-{now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"}"
        return f"{self._tenant_id}/{file_name}.{extension}"
