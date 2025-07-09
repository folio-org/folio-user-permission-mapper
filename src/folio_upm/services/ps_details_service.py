from typing import List, Dict, Optional

from pydantic import BaseModel

from folio_upm.dto.okapi import PermissionSet
from folio_upm.dto.results import OkapiLoadResult
from folio_upm.utils.ordered_set import OrderedSet


class ExplainedPermission(BaseModel):
    permissionSet: Optional[PermissionSet] = None
    subPermissions: List[PermissionSet] = []


class PermissionDetailsService:

    def __init__(self, okapi_load_rs: OkapiLoadResult):
        self._okapi_load_rs = okapi_load_rs
        self._flat_ps_by_name = self.collect_permissions_by_name(okapi_load_rs.allPermissionsExpanded)

    def explain_permission_set(self, ps_or_display_name: str):
        name_to_check = ps_or_display_name.strip()
        ps_with_flat_sub_ps = self._flat_ps_by_name.get(name_to_check)
        if ps_with_flat_sub_ps is None:
            ps_with_flat_sub_ps = self.find_by_display_name(ps_or_display_name)

        if ps_with_flat_sub_ps is None:
            return ExplainedPermission()

        flat_sub_ps = OrderedSet()

        for sub_ps in ps_with_flat_sub_ps.subPermissions:
            flat_sub_ps.add(sub_ps)

        sub_ps_explained = []
        for sub_ps in flat_sub_ps:
            found_pss = self._flat_ps_by_name.get(sub_ps)
            if found_pss is None:
                continue
            sub_ps_explained.append(found_pss)

        return ExplainedPermission(
            permissionSet=ps_with_flat_sub_ps,
            subPermissions=sub_ps_explained,
        )

    def find_by_display_name(self, display_name: str) -> Optional[PermissionSet]:
        for x in self._flat_ps_by_name.values():
            if x.displayName and display_name == x.displayName:
                return x
        return None

    def print_explained_permission_set(self, display_name: str):
        print()
        print("#" * 40)
        explained = self.explain_permission_set(display_name.strip())
        ps = explained.permissionSet
        if not ps:
            print(f"Permission not found: '{display_name.strip()}'")
            return
        print("Permission:")
        print(f"* {ps.permissionName:<72} | {ps.displayName:<80} | {len(ps.subPermissions):<5}")
        if explained.subPermissions:
            print("Sub-permissions:")
            for sub_ps in explained.subPermissions:
                print(f"  - {sub_ps.permissionName:<70} | {sub_ps.displayName:<80} | {len(sub_ps.subPermissions):<5}")

    @staticmethod
    def collect_permissions_by_name(permission_sets) -> Dict[str, PermissionSet]:
        result = dict[str, PermissionSet]()
        for ps in permission_sets:
            if ps.permissionName not in result:
                result[ps.permissionName] = ps
        return result
