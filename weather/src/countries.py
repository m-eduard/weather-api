import os

import db_utils
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import (
    Operations,
    api_request_field_mappings,
    api_response_field_mappings,
    map_fields,
    unique_fields,
    validation_error,
    validators,
)

# TODO:
# - create a method that creates a JSON with the error message from
#   the exception instead of just sending a string in Response
# - optimize put operation so it doesn't do a find before the update
#   (check if possible to do similarly to delete)
# - add type checking for url parameters (don't do it manually for each
#   endpoint)

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
                    f"Another country with the same {unique_fields[Operations.POST_COUNTRY]} already exists in {collection.name}"
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

    @api_countries.route("/api/countries/", methods=["GET"])
    def get_country():
        field_mappings = api_response_field_mappings[Operations.GET_COUNTRIES]

        response = jsonify(
            [map_fields(x, field_mappings) for x in list(collection.find({}))]
        )
        response.status_code = 200

        return response

    @api_countries.route("/api/countries/<int:id>", methods=["PUT"])
    def put_country(id):
        if type(id) != int:
            return Response("Id must be an integer", status=400)

        body = request.get_json(silent=False)

        if not validators[Operations.POST_COUNTRY](body):
            return Response(validation_error(Operations.POST_COUNTRY), status=400)

        if body["id"] != id:
            return Response(
                f"Id in the body (id={body['id']}) does not match the one in the url (id={id})",
                status=400,
            )

        if not collection.find_one({"_id": id}):
            return Response(f"Country with id {id} not found", status=404)

        body = map_fields(
            body,
            api_request_field_mappings[Operations.PUT_COUNTRY],
        )

        updated_country = db_utils.update(
            collection, {"_id": id}, body, unique_fields[Operations.POST_COUNTRY]
        )

        try:
            if not updated_country:
                raise Exception(
                    f"Another country with the same {unique_fields[Operations.POST_COUNTRY]} already exists in {collection.name}"
                )
        except Exception as e:
            return Response(
                str(
                    {
                        "operation": Operations.PUT_COUNTRY.value,
                        "collection": collection.name,
                        "body": body,
                        "error": e,
                    }
                ),
                status=409,
            )

        return Response(status=200)

    @api_countries.route("/api/countries/<int:id>", methods=["DELETE"])
    def delete_country(id):
        if type(id) != int:
            return Response("Id must be an integer", status=400)

        res = collection.delete_one({"_id": id})

        if res.deleted_count == 0:
            return Response(f"Country with id {id} not found", status=404)
        return Response(status=200)
