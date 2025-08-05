from typing import List

from pydantic import BaseModel

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.model.eureka.eureka_role_capability import FullRoleCapabilityOrSet
from folio_upm.model.eureka.user_roles import UserRoles
from folio_upm.model.stats.eureka_role_stats import EurekaRoleStats
from folio_upm.model.stats.eureka_user_stats import EurekaUserStats


class HashRolesAnalysisResult(BaseModel):
    userStats: List[EurekaUserStats]
    roleStats: List[EurekaRoleStats]
    userRoles: List[UserRoles]
    roleCapabilities: List[FullRoleCapabilityOrSet]
    hashRoleCleanupRecords: List[FullHashRoleCleanupRecord]
