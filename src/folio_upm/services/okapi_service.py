from collections import OrderedDict

import folio_upm.integrations.okapi_client as okapi_client
from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.utils import log_factory


class OkapiService(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("OkapiService initialized")
        self._client = okapi_client.OkapiClient()

    def get_okapi_defined_permissions(self):
        module_descriptors = self._client.read_module_descriptors()
        result = []
        for descriptor in module_descriptors:
            permission_sets = descriptor.get("permissionSets", [])
            module_id = descriptor.get("id")

            if not permission_sets:
                self._log.debug(f"No permission sets found for module: {module_id}")
            value = OrderedDict(
                {
                    "id": descriptor.get("id"),
                    "name": descriptor.get("name"),
                    "permissionSets": descriptor.get("permissionSets", []),
                }
            )
            result.append(value)

        return result
