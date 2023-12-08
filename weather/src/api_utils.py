import datetime as dt
from enum import Enum
from typing import Dict

from flask import jsonify


class Operations(Enum):
    POST_COUNTRY = "post_country"
    GET_COUNTRIES = "get_countries"
    PUT_COUNTRY = "put_country"
    DELETE_COUNTRY = "delete_country"

    POST_CITY = "post_city"
    GET_CITIES = "get_cities"
    GET_CITIES_BY_COUNTRY = "get_cities_by_country"
    PUT_CITY = "put_city"
    DELETE_CITY = "delete_city"

    POST_TEMPERATURE = "post_temperature"
    GET_TEMPERATURES = "get_temperatures"
    GET_TEMPERATURES_BY_CITY = "get_temperatures_by_city"
    GET_TEMPERATURES_BY_COUNTRY = "get_temperatures_by_country"
    PUT_TEMPERATURE = "put_temperature"
    DELETE_TEMPERATURE = "delete_temperature"


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
        super().__init__(f"_id={id} not found in {collection_name}")


exception_handlers = {
    ValidationError: lambda err_message: (jsonify(err_message), 400),
    BadTypeArgumentError: lambda err_message: (jsonify(err_message), 400),
    DuplicateResourceError: lambda err_message: (jsonify(err_message), 409),
    ResourceDependencyError: lambda err_message: (jsonify(err_message), 404),
    ResourceNotFoundError: lambda err_message: (jsonify(err_message), 404),
}


def build_error_message(
    operation: Operations, collection_name: str, body: dict, error: Exception
) -> dict:
    return {
        "operation": operation.value,
        "collection": collection_name,
        "body": body,
        "error": str(error),
    }


route_parameters_types = {"id": int}


# Returns a dictionary, where each value is the initial value,
# but casted to the corresponding type
def check_route_parameters(**kwargs) -> dict:
    casted_kwargs = {}

    # Try to cast each argument that should have a specific type
    # and if it fails, it means that the constraint is not satisfied
    for kwarg in kwargs.items():
        if kwarg[0] in route_parameters_types:
            try:
                casted_kwargs[kwarg[0]] = route_parameters_types[kwarg[0]](kwarg[1])
            except:
                raise BadTypeArgumentError(
                    f"{kwarg[0]}={kwarg[1]} must be an {route_parameters_types[kwarg[0]]}"
                )
    return casted_kwargs


date_format = "%Y-%m-%d"


def build_datetime(date: str) -> dt.datetime:
    return dt.datetime.strptime(date, date_format)


def build_date(datetime: dt.datetime) -> str:
    return datetime.strftime(date_format)


# Return functions to convert the query parameters to the corresponding types
query_params_handlers = {
    "db_filter": {
        Operations.GET_TEMPERATURES: {
            "lat": float,
            "lon": float,
        },
        Operations.GET_TEMPERATURES_BY_CITY: {},
        Operations.GET_TEMPERATURES_BY_COUNTRY: {},
    },
    "date_filter": {
        "from": build_datetime,
        "until": build_datetime,
    },
}


def date_filter(x: dt.datetime, start, end):
    if start and end:
        return (
            query_params_handlers["date_filter"]["from"](start)
            <= x
            <= query_params_handlers["date_filter"]["until"](end)
        )
    if start:
        return query_params_handlers["date_filter"]["from"](start) <= x
    if end:
        return x <= query_params_handlers["date_filter"]["until"](end)
    return True
