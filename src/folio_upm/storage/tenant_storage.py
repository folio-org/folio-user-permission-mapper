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

    def save_object(self, object_name: str, object_ext: str = "json.gz", object_data: Any = None):
        if object_ext == "json.gz":
            self._save_json_gz(object_name, object_data)
        elif object_ext == "json":
            self._save_json(object_name, object_data)
        elif object_ext == "xlsx":
            self._save_xlsx(object_name, object_data)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, object_name)

    def get_object(self, object_name: str, object_ext: str = "json.gz"):
        if object_ext == "json.gz":
            return self._get_json_gz(object_name)
        elif object_ext == "json":
            return self._get_json(object_name)
        elif object_ext == "xlsx":
            return self._get_xlsx(object_name)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, object_name)
            return None

    def _get_json(self, object_name: str):
        pass

    def _save_json(self, object_name: str, object_data: Any):
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
