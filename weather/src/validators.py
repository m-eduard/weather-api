from enum import Enum
from typing import Any, Dict


class Operations(Enum):
    POST_COUNTRY = "post_country"
    POST_CITY = "post_city"
    POST_TEMPERATURE = "post_temperature"


def _validate_body(body: Any, types: Dict[str, type]) -> bool:
    return (
        not (not body or type(body) != dict)
        and len(
            set(types.items())
            - set(map(lambda entry: (entry[0], type(entry[1])), body.items()))
        )
        == 0
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
}

expected_types = {
    Operations.POST_COUNTRY: {"nume": str, "lat": float, "lon": float},
    Operations.POST_CITY: {"idTara": int, "nume": str, "lat": float, "lon": float},
    Operations.POST_TEMPERATURE: {"idOras": int, "valoare": float},
}

unique_fields = {
    Operations.POST_COUNTRY: ["nume"],
    Operations.POST_CITY: ["idTara", "nume"],
    Operations.POST_TEMPERATURE: ["idOras", "timestamp"],
}

dependencies = {
    Operations.POST_CITY: [
        {"collection": "countries", "srcField": "idTara", "destField": "_id"}
    ]
}


validation_error = lambda op: (
    "Expected fields: "
    + f"{', '.join(str((x[0], x[1].__name__)) for x in expected_types[op].items())}"
)
