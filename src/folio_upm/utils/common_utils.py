from typing import Any, Iterable, List, Optional, Sequence, Set, TypeVar

T = TypeVar("T")


class IterableUtils:

    @staticmethod
    def partition(data: Sequence[T], size) -> List[List[T]]:
        _data = data
        return [list(_data[i : i + size]) for i in range(0, len(_data), size)]

    @staticmethod
    def first(value: Sequence[Optional[Any]]):
        if value is not None and len(value) > 0:
            return value[0]
        return None

    @staticmethod
    def last(value: Sequence[Optional[Any]]) -> Optional[Any]:
        if value is not None and len(value) > 0:
            return value[-1]
        return None

    @staticmethod
    def unique_values(iterable):
        return list(dict.fromkeys(iterable).keys())

    @staticmethod
    def intersection(sets: Iterable[List[Any]]) -> Set[Any]:
        _sets = [set(x) for x in sets]
        return set.intersection(*_sets)
