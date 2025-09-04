from folio_upm.integration.clients.eureka.capability_set_client import CapabilitySetClient
from folio_upm.integration.clients.eureka.role_capability_set_client import RoleCapabilitySetClient
from folio_upm.integration.services.role_entity_service import RoleEntityService
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.role_capability_set import RoleCapabilitySet
from folio_upm.utils import log_factory


class RoleCapabilitySetService(RoleEntityService[CapabilitySet, RoleCapabilitySet], metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(
            resource_name="capability-sets",
            entity_name="capability-set",
            entity_client=CapabilitySetClient(),
            role_entity_client=RoleCapabilitySetClient(),
        )
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleService initialized.")
