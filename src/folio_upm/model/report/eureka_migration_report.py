from typing import List

from pydantic import BaseModel

from folio_upm.model.report.http_request_result import HttpRequestResult


class EurekaMigrationReport(BaseModel):
    roles: List[HttpRequestResult]
    roleUsers: List[HttpRequestResult]
    roleCapabilities: List[HttpRequestResult]
