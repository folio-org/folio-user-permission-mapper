from pydantic import BaseModel

from folio_upm.model.okapi.permission_set import PermissionSet
from folio_upm.model.types.source_type import SourceType


class SourcedPermissionSet(BaseModel):
    src: SourceType
    val: PermissionSet
