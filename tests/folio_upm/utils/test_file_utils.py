from folio_upm.utils.file_utils import FileUtils


class TestFileUtils:

    def test_get_file_sort_key(self):
        key_wo_prefix = "fs123/fs123-eureka-capabilities.json.gz"
        key_with_prefix1 = "fs123/fs123-eureka-capabilities-20250722-095555039609.json.gz"
        key_with_prefix2 = "fs123/fs123-eureka-capabilities-20250721-095555039609.json.gz"
        keys = [key_wo_prefix, key_with_prefix1, key_with_prefix2]

        assert FileUtils.get_latest_file_key(keys) == key_with_prefix1
