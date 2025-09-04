from typing import Dict, List

from pydantic import BaseModel

from folio_upm.model.analysis.analyzed_parent_permission_set import AnalyzedParentPermSets
from folio_upm.model.analysis.analyzed_role import AnalyzedRole
from folio_upm.model.analysis.analyzed_role_capabilities import AnalyzedRoleCapabilities
from folio_upm.model.analysis.analyzed_user_permission_setresults import AnalyzedUserPermissionSet
from folio_upm.model.analysis.analyzed_user_roles import AnalyzedUserRoles
from folio_upm.model.stats.permission_set_stats import PermissionSetStats
from folio_upm.model.stats.permission_user_stats import PermissionUserStats


class RoleRelations(BaseModel):
    name: str
    userIds: List[str]
    permissionNames: List[str]
    capabilityNames: List[str]
