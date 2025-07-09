from enum import Enum
from typing import Optional


class EurekaLoadStrategy(Enum):
    DISTRIBUTED = "distributed"
    CONSOLIDATED = "consolidated"

    def get_name(self) -> str:
        return self.value

    @staticmethod
    def from_string(value: Optional[str]) -> Optional["EurekaLoadStrategy"]:
        if value is None:
            return None
        value_to_find = value.upper()
        if value_to_find in EurekaLoadStrategy.__members__:
            return EurekaLoadStrategy[value_to_find]
        return None

    @staticmethod
    def get_names():
        return [x.lower() for x in EurekaLoadStrategy.__members__]


DISTRIBUTED = EurekaLoadStrategy.DISTRIBUTED
CONSOLIDATED = EurekaLoadStrategy.CONSOLIDATED
