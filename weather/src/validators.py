from enum import Enum
from typing import Any, Dict


class Operations(Enum):
    POST_COUNTRY = "post_country"


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
    )
}

expected_types = {Operations.POST_COUNTRY: {"nume": str, "lat": float, "lon": float}}
unique_fields = {Operations.POST_COUNTRY: ["nume"]}


validation_error = lambda op: (
    "Expected fields: "
    + f"{', '.join(str((x[0], x[1].__name__)) for x in expected_types[op].items())}"
)
