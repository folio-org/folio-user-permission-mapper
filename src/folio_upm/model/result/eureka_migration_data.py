from typing import List

from pydantic import BaseModel

from folio_upm.model.analysis.analyzed_role import AnalyzedRole
from folio_upm.model.analysis.analyzed_role_capabilities import AnalyzedRoleCapabilities
from folio_upm.model.analysis.analyzed_user_roles import AnalyzedUserRoles


class EurekaMigrationData(BaseModel):
    roles: List[AnalyzedRole]
    userRoles: List[AnalyzedUserRoles]
    roleCapabilities: List[AnalyzedRoleCapabilities]
