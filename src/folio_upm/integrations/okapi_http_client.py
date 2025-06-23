from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integrations.http_client import HttpClient
from folio_upm.services.login_service import LoginService
from folio_upm.utils import env, log_factory

_log = log_factory.get_logger(__name__)

class OkapiHttpClient(HttpClient, metaclass=SingletonMeta):
    """
    A class to handle HTTP requests to the Okapi server.
    """

    def __init__(self):
        _log.debug('OkapiHttpClient initialized.')
        super().__init__(
            base_url=env.get_okapi_url(),
            auth_func=LoginService().get_okapi_token,
            client_timeout=env.get_http_client_timeout()
        )
