def partition(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def any_match_by_field_cql(field: str, values: list[str]) -> str:
    """
    Generates a query string to match any of the provided IDs for a given field.
    This is useful for constructing CQL queries where you want to filter results
    based on multiple values.

    :param field: Field name to match against
    :param values: a list of values to match
    :return: CQL query string
    """
    return f'{field}==({" or ".join(map(lambda x: f'"{x}"', values))})'
