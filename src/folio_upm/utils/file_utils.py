import os
from io import BytesIO

from folio_upm.utils import log_factory

_log = log_factory.get_logger("FileUtils")


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
