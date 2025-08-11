import pytest

from folio_upm.utils.json_utils import JsonUtils


class Assert:

    @staticmethod
    def compare_json_str(given: dict, expected: dict):
        given_json = JsonUtils().to_json(given, remove_none_values=True)
        expected_json = JsonUtils().to_json(expected, remove_none_values=True)
        if given_json != expected_json:
            message = (
                f"Comparison failed for JSON objects:\n"
                f"    Actual:   {given_json}\n"
                f"    Expected: {expected_json}"
            )
            pytest.fail(message)
