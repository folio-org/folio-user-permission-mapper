from typing import List

from pydantic import BaseModel

from folio_upm.model.analysis.analyzed_capability import AnalyzedCapability


class AnalyzedRoleCapabilities(BaseModel):
    roleName: str
    capabilities: List[AnalyzedCapability]
