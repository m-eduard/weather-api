from flask import Response
from validators import Operations


class ValidationError(Exception):
    pass


class BadTypeArgumentError(Exception):
    pass


class DuplicateResourceError(Exception):
    pass


class ResourceDependencyError(Exception):
    def __init__(self, dependency: dict, dependency_value: any):
        super().__init__(
            f"{dependency['destField']}={dependency_value} not found in {dependency['collection']}"
        )


class ResourceNotFoundError(Exception):
    def __init__(self, id: int, collection_name: str):
        super().__init__(f"id={id} not found in {collection_name}")


def get_error_message(
    operation: Operations, collection_name: str, body: dict, error: Exception
) -> str:
    return str(
        {
            "operation": operation.value,
            "collection": collection_name,
            "body": body,
            "error": error,
        }
    )
