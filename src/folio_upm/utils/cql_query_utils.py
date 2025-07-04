from typing import List


class CqlQueryUtils:

    @staticmethod
    def any_match_by_name(values: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("name", values)

    @staticmethod
    def any_match_by_permission(values: List[str]) -> str:
        return CqlQueryUtils.any_match_by_field("permission", values)

    @staticmethod
    def any_match_by_field(field: str, values: list[str]) -> str:
        appendable_values = [f'"{CqlQueryUtils.__cql_encode(x)}"' for x in values if x is not None and len(x) > 0]
        return f'{field}==({" or ".join(appendable_values)})'

    @staticmethod
    def __cql_encode(s: str) -> str:
        if s is None:
            return '""'
        appendable = CqlQueryUtils.__append_cql_encoded([], s)
        return "".join(appendable)

    @staticmethod
    def __append_cql_encoded(appendable: list, s: str) -> list:
        if s is not None:
            for c in s:
                if c in {"\\", "*", "?", "^", '"'}:
                    appendable.append("\\")
                appendable.append(c)
        return appendable
