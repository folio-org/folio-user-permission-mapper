from typing import Optional

from folio_upm.model.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class SystemRolesProvider(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Initializing SystemGeneratedRolesProvider")
        self._system_roles_dict = self.__get_system_roles_mappings()

    def find_system_generated_role_name(self, permission_set: str) -> Optional[str]:
        if permission_set in self._system_roles_dict:
            return self._system_roles_dict[permission_set]
        return None

    def print_system_roles(self):
        self._log.debug("Defined system-generated roles: %s", self._system_roles_dict)

    def __get_system_roles_mappings(self):
        system_generated_roles = Env().getenv_cached("SYSTEM_GENERATED_PERM_MAPPINGS")
        if not system_generated_roles:
            self._log.warning("No system-generated roles found in environment variables.")
            return dict[str, str]()
        result_dict = {}
        for pair in system_generated_roles.split(","):
            okapi_ps_and_role = pair.strip().split(":")
            if len(okapi_ps_and_role) != 2:
                self._log.warning(f"Invalid system-generated role mapping: {pair}")
                continue
            result_dict[okapi_ps_and_role[0].strip()] = okapi_ps_and_role[1].strip()

        for okapi_ps, eureka_role_name in result_dict.items():
            self._log.debug(f"System-generated role mapping: {okapi_ps} -> {eureka_role_name}")
        return result_dict
