from typing import Union

from pymongo import ReturnDocument, collection, results


def get_next_index(counters: collection.Collection, counter_type: str) -> int:
    counter = counters.find_one_and_update(
        filter={"_id": counter_type},
        update={"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["seq"]


def check_uniqueness(
    collection: collection.Collection, fields: list, values: list
) -> bool:
    return (
        collection.find_one({field: value for (field, value) in zip(fields, values)})
        is None
    )


def insert_if_unique(
    collection: collection.Collection,
    document: dict,
    unique_fields: list,
    dependencies: list = [],
) -> Union[results.InsertOneResult, None]:
    if check_uniqueness(
        collection, unique_fields, [document[field] for field in unique_fields]
    ):
        valid_insert = True

        for dependency in dependencies:
            # Check that for all the fields in the dependency, the value associated
            # with each field can be found in the dependency collection
            dependency_solved = collection.database.get_collection(
                dependency["collection"]
            ).find_one(
                filter={dependency["destField"]: document[dependency["srcField"]]},
            )

            if not dependency_solved:
                valid_insert = False
                break

        if valid_insert:
            document["_id"] = get_next_index(
                collection.database.get_collection("counters"), collection.name
            )
            return collection.insert_one(document)
        else:
            raise Exception(f"Dependency {dependency} could not be solved")
    return None
