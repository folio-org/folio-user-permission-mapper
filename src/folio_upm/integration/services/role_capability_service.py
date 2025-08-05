from folio_upm.integration.clients.eureka.capability_client import CapabilityClient
from folio_upm.integration.clients.eureka.role_capabilities_client import RoleCapabilitiesClient
from folio_upm.integration.services.role_entity_service import RoleEntityService
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.utils import log_factory


class RoleCapabilityService(RoleEntityService, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(
            resource_name="capabilities",
            entity_name="capability",
            entity_client=CapabilityClient(),
            role_entity_client=RoleCapabilitiesClient(),
        )
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")
