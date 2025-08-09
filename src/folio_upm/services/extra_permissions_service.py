from typing import List

from folio_upm.integration.services.extra_permission_set_data_provider import ExtraPermissionSetDataProvider
from folio_upm.model.analysis.analyzed_capability import AnalyzedCapability
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class ExtraPermissionsService(metaclass=SingletonMeta):
    """Resolver for managing permissions and capabilities mapping."""

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._github_file_service = ExtraPermissionSetDataProvider()
        self._remapping_data = self._github_file_service.load_extra_permission_set_data()
        self._extra_ps_names_to_view = self._remapping_data.viewCapabilities
        self._extra_ps_names_to_edit = self.__get_edit_capabilities()

    def find_extra_ps_names(self, analyzed_capabilities: List[AnalyzedCapability]) -> List[str]:
        """
        Add to user capabilities to edit and view other capabilities
        if user has permission to edit and view other permissions.

        Args:
            analyzed_capabilities: List of user permissions
        """
        role_ps_names = [ap.permissionName for ap in analyzed_capabilities if ap.permissionName]
        if self.__had_edit_permissions(role_ps_names):
            return self._extra_ps_names_to_edit
        if self.__had_view_permissions(role_ps_names):
            return self._extra_ps_names_to_view
        return []

    def __had_edit_permissions(self, ps_names: List[str]) -> bool:
        return any(ps_name in self._remapping_data.editPermissions for ps_name in ps_names)

    def __had_view_permissions(self, ps_names: List[str]) -> bool:
        return any(ps_name in self._remapping_data.viewPermissions for ps_name in ps_names)

    def __get_edit_capabilities(self) -> List[str]:
        return (
            OrderedSet[str](self._remapping_data.editCapabilities)
            .add_all(self._remapping_data.viewCapabilities)
            .to_list()
        )
