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
    collection: collection.Collection, document: dict, unique_fields: list
) -> Union[results.InsertOneResult, None]:
    if check_uniqueness(
        collection, unique_fields, [document[field] for field in unique_fields]
    ):
        document["_id"] = get_next_index(
            collection.database.get_collection("counters"), collection.name
        )
        return collection.insert_one(document)
    return None
