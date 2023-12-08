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
    dependencies,
    map_fields,
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

        try:
            if not validators[Operations.POST_CITY](body):
                raise api_utils.ValidationError(validation_error(Operations.POST_CITY))

            new_city = db_utils.insert_if_unique(
                collection,
                body,
                unique_fields[Operations.POST_CITY],
                dependencies[Operations.POST_CITY],
            )
        except (
            api_utils.ValidationError,
            api_utils.ResourceDependencyError,
            api_utils.DuplicateResourceError,
        ) as e:
            error_message = api_utils.build_error_message(
                Operations.POST_CITY, collection.name, body, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return jsonify({"id": new_city.inserted_id}), 201

    @api_cities.route("/api/cities/", methods=["GET"])
    def get_city():
        field_mappings = api_response_field_mappings[Operations.GET_CITIES]
        return (
            jsonify([map_fields(x, field_mappings) for x in list(collection.find({}))]),
            200,
        )

    @api_cities.route("/api/cities/country/<id>", methods=["GET"])
    def get_cities_by_country(id):
        try:
            id = api_utils.check_route_parameters(id=id)["id"]
            field_mappings = api_response_field_mappings[Operations.GET_CITIES]
        except api_utils.BadTypeArgumentError as e:
            error_message = api_utils.build_error_message(
                Operations.GET_CITIES, collection.name, None, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return (
            jsonify(
                [
                    map_fields(x, field_mappings)
                    for x in list(collection.find({"idTara": id}))
                ]
            ),
            200,
        )

    @api_cities.route("/api/cities/<id>", methods=["PUT"])
    def put_city(id):
        body = request.get_json(silent=False)

        try:
            id = api_utils.check_route_parameters(id=id)["id"]

            if not validators[Operations.PUT_CITY](body):
                raise api_utils.ValidationError(
                    validation_error(Operations.PUT_COUNTRY)
                )
            if body["id"] != id:
                raise api_utils.ValidationError(
                    f"id={body['id']} does not match the id from the url id={id}"
                )

            body = map_fields(body, api_request_field_mappings[Operations.PUT_CITY])
            updated_city = db_utils.update(
                collection,
                {"_id": id},
                body,
                unique_fields[Operations.POST_CITY],
                dependencies[Operations.POST_CITY],
            )

            if updated_city.modified_count == 0:
                if not collection.find_one({"_id": id}):
                    raise api_utils.ResourceNotFoundError(id, collection.name)

        except (
            api_utils.BadTypeArgumentError,
            api_utils.ValidationError,
            api_utils.ResourceNotFoundError,
            api_utils.DuplicateResourceError,
        ) as e:
            error_message = api_utils.build_error_message(
                Operations.PUT_CITY, collection.name, body, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return Response(status=200)

    @api_cities.route("/api/cities/<id>", methods=["DELETE"])
    def delete_city(id):
        try:
            id = api_utils.check_route_parameters(id=id)["id"]

            # Delete all subsequent temperatures
            db_utils.chain_delete(collection, {"_id": id}, delete_chain)

        except (api_utils.BadTypeArgumentError, api_utils.ResourceNotFoundError) as e:
            error_message = api_utils.build_error_message(
                Operations.DELETE_CITY, collection.name, None, e
            )
            return api_utils.exception_handlers[type(e)](error_message)
        return Response(status=200)
