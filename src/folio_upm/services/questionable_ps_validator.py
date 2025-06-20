from typing import List, Tuple

from folio_upm.dto.source_type import FLAT_PS
from folio_upm.dto.support import AnalyzedPermission


class QuestionablePermissionValidator:

    def __init__(self, ps: AnalyzedPermission):
        self._ps = ps
        self._reasons = list[str]()
        self._verifiers = [
            self.__check_multiple_mutable_values,
            self.__check_multiple_deprecated_values,
            self.__has_multiple_display_names,
            self.__has_multiple_descriptors,
            self.__check_different_sub_permissions,
        ]
        self.__perform_analysis()

    def is_questionable(self) -> bool:
        return len(self._reasons) == 1

    def get_reasons(self) -> List[str]:
        return self._reasons

    def __perform_analysis(self):
        for verifier in self._verifiers:
            verification_result = verifier()
            if verification_result[0]:
                self.__add_reason(verification_result[1])

    def __add_reason(self, field: str):
        self._reasons.append(field)

    def __check_multiple_mutable_values(self) -> Tuple[bool, str]:
        return len(set([sp.val.mutable for sp in self._ps.values])) > 1, "mutable"

    def __check_multiple_deprecated_values(self):
        return len(set([vh.val.deprecated for vh in self._ps.values])) > 1, "deprecated"

    def __has_multiple_display_names(self):
        return len(set([ps.val.displayName for ps in self._ps.values])) > 1, "displayName"

    def __has_multiple_descriptors(self):
        return len(set([ps.val.description for ps in self._ps.values if ps.val.description])) > 1, "description"

    def __check_different_sub_permissions(self) -> Tuple[bool, str]:
        values = self._ps.values
        sub_permissions_sets = [frozenset(sp.val.subPermissions) for sp in values if sp.src != FLAT_PS]
        f_sub_perms_sets = [x for x in sub_permissions_sets if len(x) > 0]
        flat_sub_permissions_sets = [frozenset(sp.val.subPermissions) for sp in values if sp.src == FLAT_PS]
        f_flat_sub_perm_sets = [x for x in flat_sub_permissions_sets if len(x) > 0]
        field_name = "subPermissions"

        if len(f_sub_perms_sets) == 0 and len(f_sub_perms_sets) == len(f_flat_sub_perm_sets):
            return False, field_name

        unique_sub_permissions = set(sub_permissions_sets)
        unique_flat_sub_permissions = set(flat_sub_permissions_sets)
        if len(unique_sub_permissions) == 1:
            if len(unique_flat_sub_permissions) != 1:
                return False, field_name
            sub_permissions = next(iter(unique_sub_permissions))
            flat_sub_permissions = next(iter(unique_flat_sub_permissions))
            return not sub_permissions.issubset(flat_sub_permissions), field_name

        return True, field_name
