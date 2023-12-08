Marin Eduard-Constantin, 341C3
December 2023

# Weather API

## Components
The system is composed of 3 main components, the `API` service, written in Python using Flask, a `MongoDB` database and `MongoExpress` as a web-based database management tool.

The database and the API runs in the same network, and thanks to the Docker internal DNS which works between containers, the API can access the database using the `db` hostname, and we don't need to use the IP address to connect.

The database management tool stays in another network, but in the same network with the database, since it should be decoupled from the service running the API..

## Implementation

All the possible API operations and errors are defined in `api_utils.py`, checkers for body format and query parameters type are in `validators.py` and wrappers to interact with the database can be found in `db_utils.py`.

In order to use a sequential index for the resources, I created an additional collection, `counters`, which stores the next index that can be used for each collection, and each time a new resource is added, the index is incremented.

### Type Validation

For each type of operation, in `validators.py` there is a dictionary containing the name of all the expected fields that should be included in the body of the request, and the type of each field.

The type of each body field is checked against the expected type, and if it doesn't match, a `ValidationError` is raised.

### Dependency Check
When a new city or temperature is added via a POST request, the API checks if the city belongs to a country that exists in the database, or if the temperature is linked to an existing city, otherwise it returns a `ResourceDependencyError`.

New dependencies can be easily added by inserting a new entry in the `dependencies` dictionary from `validators`, specifying the collection where the dependency should be found, and the name of the field in that collection that should match the value associated with a `srcField` in the current document (it's the same logic how a ForeignKey would work in a SQL db).

### Unique Values
Certain fields should be unique, and in order to make sure that collections don't contain duplicate values for those fields, each time when a new resource is added, we first check if there is already a document in the collection that has the same values for the fields that should be unique.

### Delete
When a resource is deleted, a cascading approach is used. For example, if a country has to be removed, all its subsequent cities and temperatures are also deleted. 

This is accomplished by a generic function from `db_utils.py` which checks in the `delete_chain` dictionary what are the collections that depend on the current document, and recursively deletes the elements from those collections which match certain fields. The process is repeated until the document deleted last doesn't have any other dependencies.

## Response Format

To "translate" the data between the internal representation (stored in MongoDB) and the format expected by the users of the API (i.e.: showing the temperature timestamp as a `YYYY-MM-DD` string, or naming the identifier field `id` instead of `_id`), there are multiple dictionaries (`api_response_field_mappings`, `api_response_value_mappings`, `api_request_field_mappings`), used by the `map_fields` function from `validators.py` which besides mapping, also does filtering on the fields that should not be returned to the user (those field names are first mapped to an empty string, and then eliminated from the response JSON).
