from folio_upm.utils.common_utils import IterableUtils
from folio_upm.utils.cql_query_utils import CqlQueryUtils
from folio_upm.utils.ordered_set import OrderedSet


class TestListUtils:

    def test_partition(self):
        given = [0] * 20
        partition_result = IterableUtils.partition(given, 5)
        expected_result = [[0] * 5] * 4
        assert partition_result == expected_result

    def test_partition_ordered_set(self):
        given = list(OrderedSet([i for i in range(20)]))
        partition_result = IterableUtils.partition(given, 5)
        expected_result = [[i for i in range(j * 5, (j + 1) * 5)] for j in range(4)]
        assert partition_result == expected_result

    def test_partition_single_chunk(self):
        given = [0] * 5
        partition_result = IterableUtils.partition(given, 5)
        expected_result = [[0] * 5]
        assert partition_result == expected_result

    def test_partition_small_chunk(self):
        given = [0] * 2
        partition_result = IterableUtils.partition(given, 5)
        expected_result = [[0] * 2]
        assert partition_result == expected_result

    def test_partition_empty_list(self):
        given = []
        partition_result = IterableUtils.partition(given, 5)
        expected_result = []
        assert partition_result == expected_result


class TestCqlQueryUtils:

    def test_any_match_by_field(self):
        field = "id"
        values = ["id1", "id2", "id3"]
        expected_query = 'id==("id1" or "id2" or "id3")'
        query_result = CqlQueryUtils.any_match_by_field(field, values)
        assert query_result == expected_query

    def test_any_match_by_field_empty_values(self):
        field = "id"
        values = []
        query_result = CqlQueryUtils.any_match_by_field(field, values)
        assert query_result == "id==()"
