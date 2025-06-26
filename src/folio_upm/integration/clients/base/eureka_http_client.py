from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.clients.base.http_client import HttpClient
from folio_upm.integration.services.login_service import LoginService
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class EurekaHttpClient(HttpClient, metaclass=SingletonMeta):
    """
    A class to handle HTTP requests to the Eureka server.
    """

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("EurekaHttpClient initialized.")
        super().__init__(
            base_url=Env().get_eureka_url(),
            auth_func=LoginService().get_eureka_token,
            client_timeout=Env().get_http_client_timeout(),
        )
