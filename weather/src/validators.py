from enum import Enum
from typing import Any, Dict


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
    GET_TEMPERATURES_BY_COORDS = "get_temperatures_by_coords"
    GET_TEMPERATURE_BY_CITY = "get_temperature_by_city"
    GET_TEMPERATURE_BY_COUNTRY = "get_temperature_by_country"
    PUT_TEMPERATURE = "put_temperature"
    DELETE_TEMPERATURE = "delete_temperature"


def _validate_body(body: Any, types: Dict[str, type]) -> bool:
    body_field_types = set(map(lambda entry: (entry[0], type(entry[1])), body.items()))

    return (
        not (not body or type(body) != dict)
        and len(set(types.items()) - body_field_types) == 0
        and len(body_field_types - set(types.items())) == 0
    )


validators = {
    Operations.POST_COUNTRY: lambda body: _validate_body(
        body, expected_types[Operations.POST_COUNTRY]
    ),
    Operations.POST_CITY: lambda body: _validate_body(
        body, expected_types[Operations.POST_CITY]
    ),
    Operations.POST_TEMPERATURE: lambda body: _validate_body(
        body, expected_types[Operations.POST_TEMPERATURE]
    ),
    Operations.PUT_COUNTRY: lambda body: _validate_body(
        body, expected_types[Operations.PUT_COUNTRY]
    ),
    Operations.PUT_CITY: lambda body: _validate_body(
        body, expected_types[Operations.PUT_CITY]
    ),
}

expected_types = {
    Operations.POST_COUNTRY: {"nume": str, "lat": float, "lon": float},
    Operations.POST_CITY: {"idTara": int, "nume": str, "lat": float, "lon": float},
    Operations.POST_TEMPERATURE: {"idOras": int, "valoare": float},
}
expected_types[Operations.PUT_COUNTRY] = {
    **expected_types[Operations.POST_COUNTRY],
    **{"id": int},
}
expected_types[Operations.PUT_CITY] = {
    **expected_types[Operations.POST_CITY],
    **{"id": int},
}
expected_types[Operations.PUT_TEMPERATURE] = {
    **expected_types[Operations.POST_TEMPERATURE],
    **{"id": int},
}

unique_fields = {
    Operations.POST_COUNTRY: ["nume"],
    Operations.POST_CITY: ["idTara", "nume"],
    Operations.POST_TEMPERATURE: ["idOras", "timestamp"],
}

dependencies = {
    Operations.POST_CITY: [
        {"collection": "countries", "srcField": "idTara", "destField": "_id"}
    ],
    Operations.POST_TEMPERATURE: [
        {"collection": "cities", "srcField": "idOras", "destField": "_id"}
    ],
}

# Specify first level of delete recursion for each collection
delete_chain = {
    "countries": {"collection": "cities", "srcField": "_id", "destField": "idTara"},
    "cities": {"collection": "temperatures", "srcField": "_id", "destField": "idOras"},
}

validation_error = lambda op: (
    "Expected fields: "
    + f"{', '.join(str((x[0], x[1].__name__)) for x in expected_types[op].items())}"
)

# Dict used to map the field names from the document stored in DB to the
# ones that are expected by the client from our API
api_response_field_mappings = {
    Operations.GET_COUNTRIES: {
        "_id": "id",
    },
    Operations.GET_CITIES: {
        "_id": "id",
    },
    Operations.GET_TEMPERATURES: {
        "_id": "id",
    },
}

# Dict used to map the field names from the request body to the ones used in DB
api_request_field_mappings = {
    Operations.PUT_COUNTRY: {
        "id": "_id",
    },
    Operations.PUT_CITY: {
        "id": "_id",
    },
    Operations.PUT_TEMPERATURE: {
        "id": "_id",
    },
}


def map_fields(document: dict, field_mappings: dict) -> dict:
    return {
        field_mappings[k] if k in field_mappings else k: v for k, v in document.items()
    }
