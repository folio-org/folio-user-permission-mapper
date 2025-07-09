from folio_upm.dto.results import EurekaLoadResult, HashRoleAnalysisResult


class EurekaHashRoleAnalyzer:

    def __init__(self, eureka_load_result: EurekaLoadResult):
        self._eureka_load_result = eureka_load_result
        self.__result = self.__analyze_eureka_resources()

    def get_result(self) -> EurekaLoadResult:
        return self._eureka_load_result

    def __analyze_eureka_resources(self) -> HashRoleAnalysisResult:
        return HashRoleAnalysisResult(
            roles=[],
            roleCapabilities=[],
            roleUsers=[],
        )
