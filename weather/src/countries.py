import os

import api_utils
import db_utils
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import (
    Operations,
    api_request_field_mappings,
    api_response_field_mappings,
    delete_chain,
    map_fields,
    unique_fields,
    validation_error,
    validators,
)

with current_app.app_context():
    mongo_client = MongoClient(current_app.config["mongo_uri"])
    db = mongo_client[os.environ.get("DB_NAME")]
    collection = db.get_collection("countries")

    api_countries = Blueprint("api_countries", __name__)

    @api_countries.route("/api/countries/", methods=["POST"])
    def post_country():
        body = request.get_json(silent=False)

        try:
            if not validators[Operations.POST_COUNTRY](body):
                raise api_utils.ValidationError(
                    validation_error(Operations.POST_COUNTRY)
                )
            new_country = db_utils.insert_if_unique(
                collection, body, unique_fields[Operations.POST_COUNTRY]
            )
        except Exception as e:
            error_message = api_utils.get_error_message(
                Operations.POST_COUNTRY, collection.name, body, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return jsonify({"id": new_country.inserted_id}), 201

    @api_countries.route("/api/countries/", methods=["GET"])
    def get_country():
        field_mappings = api_response_field_mappings[Operations.GET_COUNTRIES]

        return (
            jsonify([map_fields(x, field_mappings) for x in list(collection.find({}))]),
            200,
        )

    @api_countries.route("/api/countries/<id>", methods=["PUT"])
    def put_country(id):
        body = request.get_json(silent=False)

        try:
            id = api_utils.check_route_parameters(id=id)["id"]

            if not validators[Operations.PUT_COUNTRY](body):
                raise api_utils.ValidationError(
                    validation_error(Operations.PUT_COUNTRY)
                )
            if body["id"] != id:
                raise api_utils.ValidationError(
                    f"id={body['id']} does not match the id from the url id={id}"
                )

            body = map_fields(body, api_request_field_mappings[Operations.PUT_COUNTRY])
            updated_country = db_utils.update(
                collection, {"_id": id}, body, unique_fields[Operations.POST_COUNTRY]
            )

            # There are two scenarios in which the update operation won't update anything:
            # if the _id was not found OR if the new values are the same as the old ones
            if updated_country.modified_count == 0:
                if not collection.find_one({"_id": id}):
                    raise api_utils.ResourceNotFoundError(id, collection.name)

        except Exception as e:
            error_message = api_utils.get_error_message(
                Operations.PUT_COUNTRY, collection.name, body, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return Response(status=200)

    @api_countries.route("/api/countries/<id>", methods=["DELETE"])
    def delete_country(id):
        try:
            id = api_utils.check_route_parameters(id=id)["id"]

            # Delete all subsequent cities and temperatures
            db_utils.chain_delete(collection, {"_id": id}, delete_chain)

        except Exception as e:
            error_message = api_utils.get_error_message(
                Operations.DELETE_COUNTRY, collection.name, None, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return Response(status=200)
