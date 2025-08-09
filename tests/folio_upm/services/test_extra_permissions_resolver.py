from unittest.mock import patch

import pytest

from folio_upm.model.analysis.analyzed_capability import AnalyzedCapability
from folio_upm.model.eureka.eureka_permission_remapping_data import ExtraPermissionSetData
from folio_upm.services.extra_permissions_service import ExtraPermissionsService


class TestExtraPermissionsProvider:

    expected_extra_ps_names_to_view = ["roles.item.get", "roles.collection.get"]
    expected_extra_ps_names_to_edit = [
        "roles.item.get",
        "roles.item.post",
        "roles.item.put",
        "roles.item.delete",
        "roles.collection.get",
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        service_name = "folio_upm.services.extra_permissions_service.ExtraPermissionSetDataProvider"
        with patch(service_name) as mocked_service:
            mocked_service.return_value.load_extra_permission_set_data.return_value = self.extra_permission_set_data()
            self.service = ExtraPermissionsService()

    def test_init_loads_remapping_data(self):
        assert self.service._extra_ps_names_to_view == self.expected_extra_ps_names_to_view
        assert self.service._extra_ps_names_to_edit == self.expected_extra_ps_names_to_edit

    def test_find_extra_ps_names_with_edit_permissions(self):
        """Test finding extra permissions when user has edit permissions."""
        capabilities = [self.analyzed_capability("ps.item.get"), self.analyzed_capability("ps.item.post")]
        result = self.service.find_extra_ps_names(capabilities)
        assert result == self.service._extra_ps_names_to_edit

    def test_find_extra_ps_names_with_view_permissions_only(self):
        """Test finding extra permissions when user has edit permissions."""
        capabilities = [self.analyzed_capability("ps.item.get"), self.analyzed_capability("other.item.post")]
        result = self.service.find_extra_ps_names(capabilities)
        assert result == self.service._extra_ps_names_to_view

    def test_find_extra_ps_names_with_no_permissions(self):
        capabilities = [self.analyzed_capability("other.item.post")]
        result = self.service.find_extra_ps_names(capabilities)
        assert result == []

    def test_find_extra_ps_names_with_empty_capabilities(self):
        result = self.service.find_extra_ps_names([])
        assert result == []

    @staticmethod
    def analyzed_capability(name: str) -> AnalyzedCapability:
        return AnalyzedCapability(permissionName=name, resolvedType="unknown")

    @staticmethod
    def extra_permission_set_data() -> ExtraPermissionSetData:
        return ExtraPermissionSetData(
            viewPermissions=["ps.item.get", "ps.collection.get"],
            editPermissions=["ps.item.post", "ps.item.delete", "ps.item.put"],
            viewCapabilities=["roles.item.get", "roles.collection.get"],
            editCapabilities=["roles.item.get", "roles.item.post", "roles.item.put", "roles.item.delete"],
        )
