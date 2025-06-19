from collections import OrderedDict

import folio_upm.integrations.okapi_client as okapi_client
from folio_upm.utils import log_factory

_log = log_factory.get_logger(__name__)


def get_okapi_defined_permissions():
    module_descriptors = okapi_client.read_module_descriptors()
    result = []
    for descriptor in module_descriptors:
        permission_sets = descriptor.get("permissionSets", [])
        module_id = descriptor.get("id")

        if not permission_sets:
            _log.debug(f"No permission sets found for module: {module_id}")
        else:
            result.append(
                OrderedDict(
                    {
                        "id": descriptor.get("id"),
                        "name": descriptor.get("name"),
                        "permissionSets": descriptor.get("permissionSets", []),
                    }
                )
            )

    return result
