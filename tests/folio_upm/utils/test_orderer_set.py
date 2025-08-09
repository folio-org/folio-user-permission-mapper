import pytest
from pydantic import BaseModel, ValidationError

from folio_upm.utils.ordered_set import OrderedSet


class TestOrderedSetBasics:
    def test_init_empty(self):
        os = OrderedSet[int]()
        assert len(os) == 0
        assert list(os) == []

    def test_init_with_single_item(self):
        os = OrderedSet[int](5)
        assert len(os) == 1
        assert 5 in os
        assert list(os) == [5]

    def test_init_with_iterable(self):
        os = OrderedSet[int]([1, 2, 3, 2, 1])
        assert len(os) == 3
        assert list(os) == [1, 2, 3]

    def test_init_with_none(self):
        os = OrderedSet[int](None)
        assert len(os) == 0

    def test_add_single_item(self):
        os = OrderedSet[int]()
        os.add(1)
        assert 1 in os
        assert len(os) == 1

    def test_add_duplicate_item(self):
        os = OrderedSet[int]()
        os.add(1)
        os.add(1)
        assert len(os) == 1
        assert list(os) == [1]

    def test_add_returns_self(self):
        os = OrderedSet[int]()
        result = os.add(1)
        assert result is os

    def test_add_none_raises_error(self):
        os = OrderedSet[int]()
        with pytest.raises(ValueError, match="None items are not allowed"):
            os.add(None)  # type: ignore

    def test_add_unhashable_raises_error(self):
        os = OrderedSet[dict]()
        with pytest.raises(TypeError, match="not hashable"):
            os.add({})


class TestOrderedSetBulkOperations:
    def test_add_all(self):
        os = OrderedSet[int]()
        os.add_all([1, 2, 3])
        assert len(os) == 3
        assert list(os) == [1, 2, 3]

    def test_add_all_with_duplicates(self):
        os = OrderedSet[int]([1, 2])
        os.add_all([2, 3, 4])
        assert len(os) == 4
        assert list(os) == [1, 2, 3, 4]

    def test_add_all_returns_self(self):
        os = OrderedSet[int]()
        result = os.add_all([1, 2, 3])
        assert result is os

    def test_iadd_operator(self):
        os = OrderedSet[int]([1, 2])
        os += [3, 4]
        assert list(os) == [1, 2, 3, 4]

    def test_remove_existing_item(self):
        os = OrderedSet[int]([1, 2, 3])
        os.remove(2)
        assert 2 not in os
        assert list(os) == [1, 3]

    def test_remove_nonexistent_item(self):
        os = OrderedSet[int]([1, 2, 3])
        os.remove(5)  # Should not raise error
        assert list(os) == [1, 2, 3]

    def test_remove_none(self):
        os = OrderedSet[int]([1, 2, 3])
        os.remove(None)  # Should not raise error
        assert list(os) == [1, 2, 3]

    def test_remove_returns_self(self):
        os = OrderedSet[int]([1, 2, 3])
        result = os.remove(2)
        assert result is os

    def test_remove_all(self):
        os = OrderedSet[int]([1, 2, 3, 4, 5])
        os.remove_all([2, 4, 6])
        assert list(os) == [1, 3, 5]

    def test_remove_all_returns_self(self):
        os = OrderedSet[int]([1, 2, 3])
        result = os.remove_all([2])
        assert result is os


class TestOrderedSetMagicMethods:
    def test_contains(self):
        os = OrderedSet[int]([1, 2, 3])
        assert 2 in os
        assert 5 not in os

    def test_len(self):
        os = OrderedSet[int]([1, 2, 3])
        assert len(os) == 3

    def test_iter(self):
        os = OrderedSet[int]([1, 2, 3])
        items = list(os)
        assert items == [1, 2, 3]

    def test_repr(self):
        os = OrderedSet[int]([1, 2, 3])
        assert repr(os) == "OrderedSet([1, 2, 3])"

    def test_json(self):
        os = OrderedSet[int]([1, 2, 3])
        assert os.__json__() == [1, 2, 3]


class TestOrderedSetConversions:
    def test_to_list(self):
        os = OrderedSet[int]([1, 2, 3])
        assert os.to_list() == [1, 2, 3]

    def test_from_list(self):
        os = OrderedSet.from_list([1, 2, 3, 2, 1])
        assert list(os) == [1, 2, 3]

    def test_from_list_empty(self):
        os = OrderedSet.from_list([])
        assert len(os) == 0


class TestOrderedSetPydantic:

    def test_pydantic_validation_success(self):
        class TestModel(BaseModel):
            items: OrderedSet[int]

        items = OrderedSet[int]([1, 2, 3])
        model = TestModel(items=items)
        assert isinstance(model.items, OrderedSet)
        assert list(model.items) == [1, 2, 3]

    def test_pydantic_validation_error(self):
        class Model(BaseModel):
            items: OrderedSet[int]

        with pytest.raises(ValidationError):
            Model(items="not a list")  # type: ignore

    def test_pydantic_serialization(self):
        class Model(BaseModel):
            items: OrderedSet[int]

        items = OrderedSet[int]([1, 2, 3])
        model = Model(items=items)
        data = model.model_dump()
        assert data == {"items": [1, 2, 3]}

    def test_pydantic_json_schema(self):
        class Model(BaseModel):
            items: OrderedSet[int]

        schema = Model.model_json_schema()
        assert "items" in schema["properties"]


class TestOrderedSetEdgeCases:
    def test_empty_string_as_item(self):
        os = OrderedSet[str]()
        os.add("")
        assert "" in os
        assert len(os) == 1

    def test_string_items(self):
        os = OrderedSet[str](["a", "b", "c", "b"])
        assert list(os) == ["a", "b", "c"]

    def test_mixed_hashable_types(self):
        os = OrderedSet[object]()
        os.add(1)
        os.add("string")
        os.add((1, 2))
        assert len(os) == 3

    def test_order_preservation(self):
        items = [5, 1, 3, 2, 4, 1, 5]
        os = OrderedSet[int](items)
        assert list(os) == [5, 1, 3, 2, 4]

    def test_add_all_non_iterable_raises_error(self):
        os = OrderedSet[int]()
        with pytest.raises(TypeError, match="Expected an iterable"):
            os.add_all(42)  # type: ignore

    def test_string_not_treated_as_iterable_in_init(self):
        os = OrderedSet[str]("hello")
        assert len(os) == 1
        assert "hello" in os


class TestOrderedSetPerformance:
    def test_large_dataset(self):
        items = list(range(1000)) + list(range(500))  # 1500 items, 1000 unique
        os = OrderedSet[int](items)
        assert len(os) == 1000
        assert list(os) == list(range(1000))
