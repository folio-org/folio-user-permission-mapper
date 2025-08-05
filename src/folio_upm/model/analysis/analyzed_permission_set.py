from typing import Callable, List, Optional

from pydantic import BaseModel

from folio_upm.model.okapi.permission_set import PermissionSet
from folio_upm.model.support.sourced_permission_set import SourcedPermissionSet
from folio_upm.model.types.source_type import SourceType
from folio_upm.utils.ordered_set import OrderedSet


class AnalyzedPermissionSet(BaseModel):

    note: Optional[str] = None
    reasons: List[str] = []
    permissionName: str = None
    sourcePermSets: List[SourcedPermissionSet] = []

    def get_first_value(self, value_extractor: Callable[[PermissionSet], str]) -> Optional[str]:
        extracted_values = [value_extractor(i.val) for i in self.sourcePermSets]
        return extracted_values[0] if len(extracted_values) > 1 else None

    def get_parent_permission_names(self) -> OrderedSet[str]:
        parent_permissions = OrderedSet[str]()
        for source_perm_set in self.sourcePermSets:
            if source_perm_set.val.childOf:
                parent_permissions.add_all(source_perm_set.val.childOf)
        return parent_permissions

    def get_sub_permissions(self, include_flat: bool = False) -> OrderedSet[str]:
        sub_permissions = OrderedSet()
        for source_perm_set in self.sourcePermSets:
            if source_perm_set.src == SourceType.FLAT_PS:
                sub_permissions += source_perm_set.val.subPermissions if include_flat else []
                continue
            sub_permissions += source_perm_set.val.subPermissions
        return sub_permissions

    def get_uq_display_names_str(self) -> str:
        names = OrderedSet[str]([x.val.displayName for x in self.sourcePermSets if x.val.displayName]).to_list()
        return "\n".join(sorted(names))
