import json
from functools import reduce

from folio_upm.utils.ordered_set import OrderedSet


def test_test():
    assert 1 != 2


def test_ordered_set():
    ordered_set = OrderedSet(["s1", "s2", "s3"])
    ordered_set.append("s4")
    ordered_set.append(["s6", "s7", "s2"])
    ordered_set.remove("s2")
    assert json.dumps(ordered_set.to_list()) == '["s1", "s3", "s4", "s6", "s7"]'
