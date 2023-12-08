import datetime as dt
from typing import Tuple, Union

import api_utils
from bson.timestamp import Timestamp
from pymongo import ReturnDocument, collection, database, results


def get_next_index(counters: collection.Collection, counter_type: str) -> int:
    counter = counters.find_one_and_update(
        filter={"_id": counter_type},
        update={"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["seq"]


def check_uniqueness(
    collection: collection.Collection,
    unique_entries: dict,
    update: Tuple[bool, int] = (False, 0),
) -> bool:
    query_res = collection.find_one(unique_entries)

    # When we want to update the document with the specified _id,
    # then we should ignore its old data when checking for uniqueness
    if update[0]:
        return query_res is None or query_res["_id"] == update[1]
    return query_res is None


# Function that tries to solve all the dependencies
# for a subset of fields for a given document, and stops
# at the first unsolvable dependency
def solve_dependencies(
    database: database.Database,
    document: dict,
    dependencies: list = [],
) -> Tuple[bool, dict]:
    for dependency in dependencies:
        # Check that for all the fields in the dependency, the value associated
        # with each field can be found in the dependency collection
        dependency_solved = database.get_collection(dependency["collection"]).find_one(
            filter={dependency["destField"]: document[dependency["srcField"]]},
        )

        if not dependency_solved:
            return False, dependency
    return True, {}


def insert_if_unique(
    collection: collection.Collection,
    document: dict,
    unique_fields: list,
    dependencies: list = [],
    timestamp: bool = False,
) -> Union[results.InsertOneResult, None]:
    if timestamp:
        document["timestamp"] = Timestamp(int(dt.datetime.utcnow().timestamp()), 1)

    if check_uniqueness(collection, {x: document[x] for x in unique_fields}):
        valid_insert, unsolved_dependency = solve_dependencies(
            collection.database, document, dependencies
        )

        if valid_insert:
            counters = collection.database.get_collection("counters")
            document["_id"] = get_next_index(counters, collection.name)
            return collection.insert_one(document)
        else:
            raise api_utils.ResourceDependencyError(
                unsolved_dependency, document[unsolved_dependency["srcField"]]
            )
    raise api_utils.DuplicateResourceError(unique_fields, collection.name)


def update(
    collection: collection.Collection,
    filter: dict,
    document: dict,
    unique_fields: list,
    dependencies: list = [],
    timestamp: bool = False,
) -> Union[results.UpdateResult, None]:
    if timestamp:
        document["timestamp"] = Timestamp(int(dt.datetime.utcnow().timestamp()), 1)

    if check_uniqueness(
        collection,
        {x: document[x] for x in unique_fields},
        update=(True, document["_id"]),
    ):
        valid_insert, unsolved_dependency = solve_dependencies(
            collection.database, document, dependencies
        )

        if valid_insert:
            return collection.update_one(filter, {"$set": document})
        else:
            raise api_utils.ResourceDependencyError(
                unsolved_dependency, document[unsolved_dependency["srcField"]]
            )
    raise api_utils.DuplicateResourceError(unique_fields, collection.name)
