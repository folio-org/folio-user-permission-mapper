import io
from datetime import UTC, datetime
from typing import Any, Optional

from openpyxl import Workbook

from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class TenantStorage:

    _xlsx_ext = "xlsx"
    _json_ext = "json"
    _json_gz_ext = "json.gz"

    def __init__(self):
        self._tenant_id = Env().get_tenant_id()
        self._log = log_factory.get_logger(self.__class__.__name__)

    def save_object(self, object_name: str, object_ext: str, object_data: Any = None):
        file_key = self._get_file_key(object_name, object_ext, include_ts=True)
        if object_ext == "json.gz":
            self._save_json_gz(file_key, object_data)
        elif object_ext == "json":
            self._save_json(file_key, object_data)
        elif object_ext == "xlsx":
            self._save_xlsx(file_key, object_data)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, object_name)

    def find_object(self, object_name: str, object_ext: str) -> Optional[Any]:
        object_key_prefix = self._get_file_prefix(object_name)
        object_key = self._find_latest_object_by_name(object_key_prefix, object_ext)
        if object_key is None:
            self._log.warning("Object not found by prefix: %s", object_key_prefix)
            return None
        if object_ext == "json.gz":
            return self._get_json_gz(object_key)
        elif object_ext == "json":
            return self._get_json(object_key)
        elif object_ext == "xlsx":
            return self._get_xlsx(object_key)
        else:
            self._log.error("Unsupported object type: %s, file=%s", object_ext, object_name)
            return None

    def find_object_by_key(self, ref_key) -> Optional[Any]:
        if ref_key.endswith("json.gz"):
            return self._get_json_gz(ref_key)
        elif ref_key.endswith("json"):
            return self._get_json(ref_key)
        else:
            self._log.error("Unsupported object type: %s, file=%s", ref_key, ref_key)
        return None

    def _find_latest_object_by_name(self, prefix: str, object_ext: str) -> Optional[str]:
        return None

    def _get_json(self, file_key: str):
        pass

    def _save_json(self, file_key: str, object_data: Any):
        pass

    def _get_json_gz(self, object_name: str) -> Optional[Any]:
        pass

    def _save_json_gz(self, object_name: str, object_data: Any) -> None:
        pass

    def _get_xlsx(self, object_name: str) -> Optional[io.BytesIO]:
        pass

    def _save_xlsx(self, object_name: str, object_data: Workbook) -> None:
        pass

    def _get_file_key(self, file_name, extension, include_ts: bool = False) -> str:
        _file_name = f"{self._tenant_id}-{file_name}"
        if include_ts:
            now = datetime.now(tz=UTC)
            _file_name += f"-{now.strftime("%Y%m%d-%H%M%S%f")}"
        return f"{self._tenant_id}/{_file_name}.{extension}"

    def _get_file_prefix(self, file_name) -> str:
        return f"{self._tenant_id}/{self._tenant_id}-{file_name}"
