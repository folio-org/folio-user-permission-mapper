import glob
import os
import re
from io import BytesIO
from typing import Optional

from folio_upm.utils import log_factory

_log = log_factory.get_logger("FileUtils")
_timestamp_pattern = r"-(\d{4}\d{2}\d{2}-\d{2}\d{2}\d{2}\d{6})"


class FileUtils:

    @staticmethod
    def read_binary_data(file_key) -> BytesIO | None:
        if not os.path.exists(file_key):
            _log.warn("File '%s' not found", file_key)
            return None

        with open(file_key, "rb") as f:
            file_bytes_buffer = BytesIO(f.read())
            file_bytes_buffer.seek(0)
            _log.debug("Returning file: '%s'", file_key)
            return file_bytes_buffer

    @staticmethod
    def write_binary_data(file_key, binary_data: BytesIO):
        _log.debug("Saving file: '%s' ...", file_key)

        if FileUtils.exists(file_key):
            _log.debug("File '%s' already exists, overriding it", file_key)

        with open(file_key, "wb") as f:
            binary_data.seek(0)
            f.write(binary_data.getbuffer())
            _log.debug("Data saved to file '%s'", file_key)

    @staticmethod
    def exists(file_key):
        _log.debug("Checking if file exists: '%s'", file_key)
        return os.path.exists(file_key)

    @staticmethod
    def create_directory_safe(directory_path):
        if not os.path.exists(directory_path):
            _log.debug("Creating directory: %s", directory_path)
            os.makedirs(directory_path)
        return directory_path

    @staticmethod
    def find_latest_key_by_prefix(out_folder: str, prefix: str) -> Optional[str]:
        try:
            search_pattern = os.path.join(out_folder, f"{prefix}*")
            matching_files = glob.glob(search_pattern)

            if not matching_files:
                _log.debug(f"No files found with prefix: {prefix}")
                return None

            matching_keys = []
            for file_path in matching_files:
                relative_key = os.path.relpath(file_path, out_folder)
                matching_keys.append(relative_key)

            latest_key = FileUtils.get_latest_file_key(matching_keys)
            _log.debug(f"Found files with prefix '{prefix}', latest: {latest_key}, files: {matching_keys}")
            return latest_key

        except Exception as e:
            _log.error("Error finding latest file with prefix '%s/%s'", out_folder, prefix, e)
            return None

    @staticmethod
    def get_latest_file_key(matching_object_keys: list[str]) -> Optional[str]:
        if not matching_object_keys:
            _log.debug("No matching keys found")
            return None

        latest_key = max(matching_object_keys, key=FileUtils.get_file_sort_key)
        _log.debug(f"Latest file key found: {latest_key}")
        return latest_key

    @staticmethod
    def get_file_sort_key(key) -> tuple[int, str]:
        has_timestamp = 1 if re.search(_timestamp_pattern, key) else 0
        return has_timestamp, key
