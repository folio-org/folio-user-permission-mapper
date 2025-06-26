from typing import Optional

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class SystemGeneratedRolesProvider(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Initializing SystemGeneratedRolesProvider")
        self._system_roles_dict = self.__get_system_roles_mappings()

    def has_system_generated_ps(self, permission_set: str) -> bool:
        return permission_set in self._system_roles_dict

    def get_eureka_role_name(self, role_name: str) -> Optional[str]:
        return self._system_roles_dict.get(role_name)

    def __get_system_roles_mappings(self):
        system_generated_roles = Env().get_env("SYSTEM_GENERATED_PERM_MAPPINGS")
        if not system_generated_roles:
            self._log.warning("No system-generated roles found in environment variables.")
            return dict[str, str]()
        result_dict = {}
        for pair in system_generated_roles.split(","):
            pairs = pair.strip().split(":")
            if len(pairs) != 2:
                self._log.warning(f"Invalid system-generated role mapping: {pair}")
                continue
            result_dict[pair[0].strip()] = pair[1].strip()

        for okapi_ps, eureka_role_name in result_dict.items():
            self._log.info(f"System-generated role mapping: {okapi_ps} -> {eureka_role_name}")
        return result_dict
