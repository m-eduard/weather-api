from typing import Any, Dict

from api_utils import Operations, build_date


def _validate_body(body: Any, types: Dict[str, type]) -> bool:
    if not body or type(body) != dict:
        return False

    body_field_types = set(map(lambda entry: (entry[0], type(entry[1])), body.items()))

    return (
        len(set(types.items()) - body_field_types) == 0
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
    Operations.PUT_TEMPERATURE: lambda body: _validate_body(
        body, expected_types[Operations.PUT_TEMPERATURE]
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
        "idOras": "",
    },
}

# Dict storing functions which map the field values from the document stored
# in DB to the ones that are expected by the client from our API (i.e. convert ISODate
# to string YYYY-MM-DD)
api_response_value_mappings = {
    Operations.GET_TEMPERATURES: {
        "timestamp": build_date,
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


def map_fields(document: dict, field_mappings: dict, value_mappings: dict = {}) -> dict:
    mapped_document = {
        (field_mappings.get(k, k)): (value_mappings[k](v) if k in value_mappings else v)
        for k, v in document.items()
    }

    # Erase the empty string key (bedcause all the unwanted
    # keys were previously mapped to empty string)
    mapped_document.pop("", None)

    return mapped_document
