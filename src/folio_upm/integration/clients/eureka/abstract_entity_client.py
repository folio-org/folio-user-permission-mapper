from typing import Generic, List, TypeVar

E = TypeVar("E")


class AbstractEntityClient(Generic[E]):

    def find_by_query(self, cql_query: str) -> List[E]:
        """
        Finds entities by a CQL query.
        This method should be implemented by subclasses to perform the actual query.
        """
        raise NotImplementedError("Subclasses must implement this method.")
