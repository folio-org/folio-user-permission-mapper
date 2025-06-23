class ListUtils:

    @staticmethod
    def partition(list_value, size):
        """
        Partitions a list into chunks of a specified size.

        :param list_value: List to be partitioned
        :param size: Size of each partition
        :return: Partitioned list as a generator
        """
        for i in range(0, len(list_value), size):
            yield list_value[i: i + size]


class CqlQueryUtils:

    @staticmethod
    def any_match_by_field(field: str, values: list[str]) -> str:
        """
        Generates a query string to match any of the provided IDs for a given field.
        This is useful for constructing CQL queries where you want to filter results
        based on multiple values.

        :param field: Field name to match against
        :param values: a list of values to match
        :return: CQL query string
        """
        return f'{field}==({" or ".join(map(lambda x: f'"{x}"', values))})'
