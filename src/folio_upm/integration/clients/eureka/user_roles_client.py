from typing import List

from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.user_role import UserRole
from folio_upm.utils import log_factory


class UserRolesClient(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("UserRolesClient initialized.")
        self._base_client = EurekaHttpClient()

    def post_user_roles(self, user_id: str, role_ids: list[str]) -> List[UserRole]:
        body = {"userId": user_id, "roleIds": role_ids}
        response = self._base_client.post_json("/roles/users", request_body=body)
        user_roles = response.get("userRoles", []) if response else []
        return [UserRole(**ur) for ur in user_roles]
