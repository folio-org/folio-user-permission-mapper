from enum import Enum


class StrategyType(str, Enum):
    DISTRIBUTED = "distributed"
    CONSOLIDATED = "consolidated"
    HYBRID = "hybrid"


DISTRIBUTED = StrategyType.DISTRIBUTED
CONSOLIDATED = StrategyType.CONSOLIDATED
HYBRID = StrategyType.HYBRID
