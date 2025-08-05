from typing import List

from pydantic import BaseModel

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.model.eureka.role import Role
from folio_upm.model.result.hash_roles_analysis_result import HashRolesAnalysisResult


class HashRoleCleanupRecord(BaseModel):
    role: Role
    capabilities: List[str]
    capabilitySets: List[str]

    @staticmethod
    def get_records_from_analysis_result(data: HashRolesAnalysisResult) -> List["HashRoleCleanupRecord"]:
        return [HashRoleCleanupRecord.from_clean_hash_role(x) for x in data.hashRoleCleanupRecords]

    @staticmethod
    def from_clean_hash_role(clean_hash_role: FullHashRoleCleanupRecord) -> "HashRoleCleanupRecord":
        return HashRoleCleanupRecord(
            role=clean_hash_role.role,
            capabilities=[cap.id for cap in clean_hash_role.capabilities],
            capabilitySets=[cs.id for cs in clean_hash_role.capabilitySets],
        )
