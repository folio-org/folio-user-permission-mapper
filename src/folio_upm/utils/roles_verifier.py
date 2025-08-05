import os
from functools import cache
from typing import List

import jwt

from folio_upm.model.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env
from folio_upm.utils.utils import Utils


class RoleLengthVerifier(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        default_max_length = 4000
        env_max_jwt_length = Env().getenv("MAX_JWT_LENGTH", str(default_max_length))
        self._max_jwt_length = Utils.safe_cast(env_max_jwt_length, int, default_max_length)

    def has_invalid_amount_of_roles(self, roles: List[str]) -> bool:
        sample_key = self.read_private_key()
        sample_payload = self.read_sample_payload()
        sample_payload["realm_access"] = {"roles": roles}
        token = jwt.encode(sample_payload, key=sample_key, algorithm="RS256")
        return len(token) > self._max_jwt_length

    @cache  # noqa: B019
    def read_private_key(self):
        key_name = "test_private_key.pem"
        key_path = f"../../resources/role-length-test-data/{key_name}"
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        full_path = os.path.join(curr_dir, key_path)
        with open(full_path, "rb") as f:
            return f.read()

    @cache  # noqa: B019
    def read_sample_payload(self):
        file_name = "sample-payload.json"
        full_path = f"../../resources/role-length-test-data/{file_name}"
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(curr_dir, full_path)
        return JsonUtils.read_string(file_path)
