from flask import jsonify
from validators import Operations


class ValidationError(Exception):
    pass


class BadTypeArgumentError(Exception):
    pass


class DuplicateResourceError(Exception):
    def __init__(self, unique_fields: list, collection_name: str):
        super().__init__(
            f"Another resource with the same {unique_fields} already exists in {collection_name}"
        )


class ResourceDependencyError(Exception):
    def __init__(self, dependency: dict, dependency_value: any):
        super().__init__(
            f"{dependency['destField']}={dependency_value} not found in {dependency['collection']}"
        )


class ResourceNotFoundError(Exception):
    def __init__(self, id: int, collection_name: str):
        super().__init__(f"id={id} not found in {collection_name}")


exception_handlers = {
    ValidationError: lambda err_message: (jsonify(err_message), 400),
    BadTypeArgumentError: lambda err_message: (jsonify(err_message), 400),
    DuplicateResourceError: lambda err_message: (jsonify(err_message), 409),
    ResourceDependencyError: lambda err_message: (jsonify(err_message), 404),
    ResourceNotFoundError: lambda err_message: (jsonify(err_message), 404),
}


def get_error_message(
    operation: Operations, collection_name: str, body: dict, error: Exception
) -> dict:
    return {
        "operation": operation.value,
        "collection": collection_name,
        "body": body,
        "error": str(error),
    }
