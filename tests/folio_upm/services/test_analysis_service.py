import json

from folio_upm.dto.eureka import Capability
from folio_upm.dto.results import EurekaLoadResult
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.ordered_set import OrderedSet


def test_test():
    assert 1 != 2


def test_deserialization():
    json_value ="""
{
  "capabilities": [
    {
      "id": "769ed9e7-4d73-4317-aa83-f9872be2538f",
      "name": "acquisitions-units-storage_memberships_item.delete",
      "description": "Delete an acquisitions unit membership",
      "resource": "Acquisitions-Units-Storage Memberships Item",
      "action": "delete",
      "applicationId": "app-acquisitions-1.0.19",
      "moduleId": "mod-orders-13.0.5",
      "permission": "acquisitions-units-storage.memberships.item.delete",
      "endpoints": [
        {
          "path": "/acquisitions-units-storage/memberships/{id}",
          "method": "DELETE"
        }
      ],
      "dummyCapability": false,
      "type": "data",
      "metadata": {
        "createdDate": "2025-02-28T10:56:54.826+00:00",
        "updatedDate": "2025-06-19T15:19:32.476+00:00"
      }
    }
  ],
  "capabilitySets": [
    {
      "id": "0ed247fc-04cc-490a-9238-28942a8d2ae8",
      "name": "orders_acquisition-methods.manage",
      "description": "All permissions for the acquisition method",
      "resource": "Orders Acquisition-Methods",
      "action": "manage",
      "applicationId": "app-acquisitions-1.0.19",
      "moduleId": "mod-orders-13.0.5",
      "type": "data",
      "permission": "orders.acquisition-methods.all",
      "capabilities": [
        "316f2837-1c99-4850-904d-04478652d4e8",
        "18cdb904-2a21-4bdc-a10b-e812834677e8",
        "40b70d73-fbeb-46ac-924f-10344694ee09",
        "014bbd2c-f63b-470c-8150-f9e5cb47b5a1",
        "9eb360c9-1225-4ade-b18e-dbf21df82f13",
        "5dc84d7d-c2d2-40cc-90d2-a7bedacf94fd"
      ],
      "metadata": {
        "createdDate": "2025-02-28T10:57:21.161+00:00",
        "updatedDate": "2025-06-19T15:20:21.253+00:00"
      }
    }
  ],
  "roles": [
    {
      "id": "ca7004f6-b46f-426e-9b15-6dd6f8deac6e",
      "name": "Acquisition Administrator",
      "description": "Role for Acquisition Administrator",
      "type": "DEFAULT",
      "metadata": {
        "createdDate": "2025-02-28T10:55:40.750+00:00",
        "updatedDate": "2025-02-28T10:55:42.917+00:00"
      }
    }
  ]
}
    """
    dict_caps=JsonUtils.from_json(json_value)
    json_str = '{"name": "test", "description": "test description"}'
    capability = EurekaLoadResult(**dict_caps)
    print(capability)

def test_ordered_set():
    ordered_set = OrderedSet[str](["s1", "s2", "s3"])
    ordered_set.append("s4")
    ordered_set.append(["s6", "s7", "s2"])
    ordered_set.remove("s2")
    assert json.dumps(ordered_set.to_list()) == '["s1", "s3", "s4", "s6", "s7"]'
