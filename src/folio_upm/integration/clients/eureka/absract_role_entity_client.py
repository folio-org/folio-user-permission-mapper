from typing import Generic, List, TypeVar

T = TypeVar("T")


class AbstractRoleEntityClient(Generic[T]):

    def find_by_query(self, query: str, limit: int, offset: int) -> List[T]:
        """
        Finds role-entities by query, limit, and offset.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def create_role_entity(self, role_id: str, entity_ids: List[str]) -> List[T]:
        """
        Creates a role entity with the given role ID and entity IDs.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def update_role_entity(self, role_id: str, entity_ids: List[str]) -> None:
        """
        Updates the role entity with the given role ID and entity IDs.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_target_entity_id(self, entity: T) -> str:
        """
        Returns the target ID of the entity.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
