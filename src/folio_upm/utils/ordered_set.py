from typing import Any, Dict, Generic, Iterable, Iterator, List, Optional, TypeVar, Union

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic_core.core_schema import ValidationInfo

T = TypeVar("T")


class OrderedSet(Generic[T]):

    def __init__(self, value: Optional[Union[T, Iterable[T]]] = None) -> None:
        """
        Initialize the OrderedSet. Optionally populate it with elements from an iterable.

        Args:
            value: An iterable or single item to initialize the OrderedSet with.
        """
        self._data: Dict[T, None] = {}
        if value is None:
            return

        if self.__is_iterable(value):
            for item in value:  # type: ignore
                self.add(item)  # type: ignore
        else:
            self.add(value)  # type: ignore

    def add(self, item: T) -> "OrderedSet[T]":
        self.__validate_item(item)
        self._data[item] = None
        return self

    def add_all(self, items: Iterable[T]) -> "OrderedSet[T]":
        self.__validate_iterable_items(items)
        for sub_item in items:
            self.__validate_item(sub_item)
            if sub_item not in self._data:
                self.add(sub_item)
        return self

    def remove(self, item: Optional[T]) -> "OrderedSet[T]":
        self.__validate_item(item, check_none=False)
        self._data.pop(item, None)  # type: ignore
        return self

    def remove_all(self, items: Iterable[Optional[T]]) -> "OrderedSet[T]":
        self.__validate_iterable_items(items)  # type: ignore
        for item in items:
            self.remove(item)
        return self

    def __iadd__(self, other: Iterable[T]) -> "OrderedSet[T]":
        self.add_all(other)
        return self

    def __contains__(self, item: Optional[T]) -> bool:
        """Check if an item is in the set."""
        if item is None:
            return False
        return item in self._data

    def __iter__(self) -> Iterator[T]:
        """Iterate over the items in the set."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return the number of items in the set."""
        return len(self._data)

    def __repr__(self) -> str:
        """Return a string representation of the set."""
        return f"{self.__class__.__name__}({list(self._data)})"

    def __json__(self) -> List[T]:
        return self.to_list()

    def to_list(self) -> List[T]:
        """Convert the OrderedSet to a list."""
        return list(self._data.keys())

    @classmethod
    def from_list(cls, items: List[T]) -> "OrderedSet[T]":
        """Create an OrderedSet from a list."""
        ordered_set = cls()
        for item in items:
            ordered_set.add(item)
        return ordered_set

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        if hasattr(source_type, "__args__") and source_type.__args__:
            item_type = source_type.__args__[0]
        else:
            item_type = Any
        schema = handler.generate_schema(item_type)

        def validate_ordered_set(value: Any, info: ValidationInfo) -> "OrderedSet[Any]":
            if not isinstance(value, list):
                raise TypeError(f"Expected a list, got {type(value).__name__}")
            return cls(value)

        def serialize_ordered_set(value: "OrderedSet[Any]", serializer) -> List[Any]:
            return value.to_list()

        return core_schema.with_info_after_validator_function(
            validate_ordered_set,
            core_schema.list_schema(schema),
            serialization=core_schema.wrap_serializer_function_ser_schema(
                serialize_ordered_set, return_schema=core_schema.list_schema(schema)
            ),
        )

    def __validate_iterable_items(self, items: Iterable[Any]) -> None:
        if not self.__is_iterable(items):
            raise TypeError(f"Expected an iterable, got {type(items).__name__}")

    @staticmethod
    def __is_iterable(item: Any) -> bool:
        return isinstance(item, Iterable) and not isinstance(item, str)

    @staticmethod
    def __validate_item(item: Any, check_none: bool = True) -> None:
        if check_none and item is None:
            raise ValueError("None items are not allowed in OrderedSet")
        if not hasattr(item, "__hash__") or item.__hash__ is None:
            raise TypeError(f"Item {item} is not hashable and cannot be added to OrderedSet")
