import os

import db_utils
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import (
    Operations,
    dependencies,
    unique_fields,
    validation_error,
    validators,
)

with current_app.app_context():
    mongo_client = MongoClient(current_app.config["mongo_uri"])
    db = mongo_client[os.environ.get("DB_NAME")]
    collection = db.get_collection("cities")

    api_cities = Blueprint("api_cities", __name__)

    @api_cities.route("/api/cities/", methods=["POST"])
    def post_city():
        body = request.get_json(silent=False)
        if not validators[Operations.POST_CITY](body):
            return Response(validation_error(Operations.POST_CITY), status=400)

        try:
            new_city = db_utils.insert_if_unique(
                collection,
                body,
                unique_fields[Operations.POST_CITY],
                dependencies[Operations.POST_CITY],
            )

            # Throw an error if a city with the same name and country id already exists
            if not new_city:
                raise Exception(
                    f"Another city with the same {unique_fields[Operations.POST_CITY]} already exists in {collection.name}"
                )
        except Exception as e:
            return Response(
                str(
                    {
                        "operation": Operations.POST_CITY.value,
                        "collection": "cities",
                        "body": body,
                        "error": e,
                    }
                ),
                status=409,
            )

        response = jsonify({"id": new_city.inserted_id})
        response.status_code = 201

        return response
