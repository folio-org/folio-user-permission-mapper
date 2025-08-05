from typing import Dict, List, Optional

from pydantic import BaseModel

from folio_upm.model.analysis.analyzed_permission_set import AnalyzedPermissionSet
from folio_upm.model.types.permission_type import SUPPORTED_PS_TYPES, PermissionType
from folio_upm.utils.ordered_set import OrderedSet


class PermissionAnalysisResult(BaseModel):
    mutable: Dict[str, AnalyzedPermissionSet] = {}
    okapi: Dict[str, AnalyzedPermissionSet] = {}
    invalid: Dict[str, AnalyzedPermissionSet] = {}
    deprecated: Dict[str, AnalyzedPermissionSet] = {}
    questionable: Dict[str, AnalyzedPermissionSet] = {}
    unprocessed: Dict[str, AnalyzedPermissionSet] = {}
    systemPermissionNames: OrderedSet[str] = []

    def __getitem__(self, ps_type: PermissionType) -> Optional[Dict[str, "AnalyzedPermissionSet"]]:
        if ps_type not in SUPPORTED_PS_TYPES:
            return {}
        return getattr(self, ps_type.get_name())

    def identify_permission_type(self, ps_name: str) -> PermissionType:
        for ps_type in SUPPORTED_PS_TYPES:
            key = ps_type.get_name()
            if ps_name in getattr(self, key):
                return PermissionType.from_string(key)
        return PermissionType.UNKNOWN

    @staticmethod
    def get_supported_types() -> List[PermissionType]:
        return SUPPORTED_PS_TYPES
