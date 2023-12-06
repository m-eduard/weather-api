import os

import db_utils
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import Operations, unique_fields, validation_error, validators

with current_app.app_context():
    mongo_client = MongoClient(current_app.config["mongo_uri"])
    db = mongo_client[os.environ.get("DB_NAME")]
    collection = db.get_collection("countries")

    api_countries = Blueprint("api_countries", __name__)

    @api_countries.route("/api/countries/", methods=["POST"])
    def post_country():
        body = request.get_json(silent=False)
        if not validators[Operations.POST_COUNTRY](body):
            return Response(validation_error(Operations.POST_COUNTRY), status=400)

        try:
            new_country = db_utils.insert_if_unique(
                collection, body, unique_fields[Operations.POST_COUNTRY]
            )

            # Throw an error if a country with the same name already exists
            if not new_country:
                raise Exception(
                    f"Another country with the same {unique_fields[Operations.POST_CITY]} already exists in {collection.name}"
                )
        except Exception as e:
            return Response(
                str(
                    {
                        "operation": Operations.POST_COUNTRY.value,
                        "collection": collection.name,
                        "body": body,
                        "error": e,
                    }
                ),
                status=409,
            )

        response = jsonify({"id": new_country.inserted_id})
        response.status_code = 201

        return response
