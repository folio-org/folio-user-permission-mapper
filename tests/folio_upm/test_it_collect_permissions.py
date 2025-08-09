# tests/integration/test_collect_permissions_integration.py
from unittest.mock import patch

import pytest
import responses

from folio_upm.cli import collect_permissions
from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.storage.tenant_storage_service import TenantStorageService


class TestCollectPermissionsIntegration:

    @pytest.fixture
    def mock_module_descriptor(self):
        return {
            "id": "test-module-1.0.0",
            "name": "Test Module",
            "provides": [
                {
                    "id": "test-interface",
                    "version": "1.0",
                    "handlers": [
                        {
                            "methods": ["GET"],
                            "pathPattern": "/test",
                            "permissionsRequired": ["test.read"]
                        }
                    ]
                }
            ],
            "permissionSets": [
                {
                    "permissionName": "test.read",
                    "displayName": "Test Read Permission",
                    "description": "Permission to read test data"
                },
                {
                    "permissionName": "test.write",
                    "displayName": "Test Write Permission",
                    "description": "Permission to write test data",
                    "subPermissions": ["test.read"]
                }
            ]
        }

    @pytest.fixture
    def mock_permission_sets(self):
        return [
            {
                "id": "perm-set-1",
                "permissionName": "users.collection.get",
                "displayName": "Users Collection Get",
                "description": "Get users collection"
            },
            {
                "id": "perm-set-2",
                "permissionName": "users.item.post",
                "displayName": "Users Item Post",
                "description": "Create user",
                "subPermissions": ["users.collection.get"]
            }
        ]

    @responses.activate
    @patch.object(TenantStorageService, 'save_object')
    def test_collect_permissions_success(self, mock_save, mock_module_descriptor, mock_permission_sets):
        # Mock Okapi responses
        responses.add(
            responses.GET,
            "http://okapi-url/_/proxy/modules",
            json=[mock_module_descriptor],
            status=200
        )

        responses.add(
            responses.GET,
            "http://okapi-url/perms/permissions",
            json={"permissions": mock_permission_sets},
            status=200
        )

        # Execute the command
        collect_permissions()

        # Verify save_object was called with correct parameters
        mock_save.assert_called_once()
        call_args = mock_save.call_args

        assert call_args[0][0] == "okapi-permissions"  # filename
        assert call_args[0][1] == "json.gz"  # extension

        # Verify the saved data structure
        saved_data = call_args[0][2]
        assert isinstance(saved_data, OkapiLoadResult)
        assert len(saved_data.module_descriptors) == 1
        assert len(saved_data.permission_sets) == 2

    @responses.activate
    def test_collect_permissions_okapi_error(self):
        # Mock failed Okapi response
        responses.add(
            responses.GET,
            "http://okapi-url/_/proxy/modules",
            json={"error": "Unauthorized"},
            status=401
        )

        # Should raise appropriate exception
        with pytest.raises(Exception):
            collect_permissions()

    @responses.activate
    @patch.object(TenantStorageService, 'save_object')
    def test_collect_permissions_empty_response(self, mock_save):
        # Mock empty responses
        responses.add(
            responses.GET,
            "http://okapi-url/_/proxy/modules",
            json=[],
            status=200
        )

        responses.add(
            responses.GET,
            "http://okapi-url/perms/permissions",
            json={"permissions": []},
            status=200
        )

        collect_permissions()

        # Verify empty data is handled correctly
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][2]
        assert len(saved_data.module_descriptors) == 0
        assert len(saved_data.permission_sets) == 0
