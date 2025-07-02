from collections import OrderedDict
from typing import Any, Sequence


class IterableUtils:

    @staticmethod
    def partition(data: Sequence, size):
        _data = data
        return [_data[i : i + size] for i in range(0, len(_data), size)]

    @staticmethod
    def first(value: Sequence[Any | None]):
        if value is not None and len(value) > 0:
            return value[0]
        return None

    @staticmethod
    def last(value: Sequence[Any | None]):
        if value is not None and len(value) > 0:
            return value[-1]
        return None

    @staticmethod
    def unique_values(iterable):
        return list(OrderedDict.fromkeys(iterable).keys())
