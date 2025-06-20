import json

from folio_upm.utils.ordered_set import OrderedSet


def test_test():
    assert len([1, 2, 3]) == 3
    assert {3, 2, 1} == {1, 2, 3}


def test_ordered_set():
    ordered_set = OrderedSet(["s1", "s2", "s3"])
    ordered_set.add("s4")
    ordered_set.add(["s6", "s7", "s2"])
    ordered_set.remove("s2")
    assert json.dumps(ordered_set.to_list()) == '["s1", "s3", "s4", "s6", "s7"]'
