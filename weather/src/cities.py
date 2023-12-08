import os

import api_utils
import db_utils
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import (
    Operations,
    api_request_field_mappings,
    api_response_field_mappings,
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
                        "collection": collection.name,
                        "body": body,
                        "error": e,
                    }
                ),
                status=409,
            )

        response = jsonify({"id": new_city.inserted_id})
        response.status_code = 201

        return response

    @api_cities.route("/api/cities", methods=["GET"])
    def get_city():
        field_mappings = api_response_field_mappings[Operations.GET_CITIES]

        response = jsonify(
            [map_fields(x, field_mappings) for x in list(collection.find({}))]
        )
        response.status_code = 200
        return response

    @api_cities.route("/api/cities/country/<int:id>", methods=["GET"])
    def get_cities_by_country(id):
        if type(id) != int:
            return Response("Id must be an integer", status=400)

        field_mappings = api_response_field_mappings[Operations.GET_CITIES]

        response = jsonify(
            [
                map_fields(x, field_mappings)
                for x in list(collection.find({"idTara": id}))
            ]
        )
        response.status_code = 200
        return response

    @api_cities.route("/api/cities/<int:id>", methods=["PUT"])
    def put_city(id):
        body = request.get_json(silent=False)

        try:
            if type(id) != int:
                raise api_utils.BadTypeArgumentError(f"id={id} must be an integer")
            if not validators[Operations.POST_CITY](body):
                raise api_utils.ValidationError(validation_error(Operations.POST_CITY))
            if body["id"] != id:
                raise api_utils.ValidationError(
                    f"id={body['id']}) does not match the id from the url id={id}"
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
                raise api_utils.ResourceNotFoundError(id, collection.name)

        except Exception as e:
            error_message = api_utils.get_error_message(
                Operations.PUT_CITY, collection.name, body, e
            )

            try:
                raise e
            except (api_utils.ValidationError, api_utils.BadTypeArgumentError):
                return Response(error_message, status=400)
            except (api_utils.ResourceNotFoundError, api_utils.ResourceDependencyError):
                return Response(error_message, status=404)
            except api_utils.DuplicateResourceError:
                return Response(error_message, status=409)
        return Response(status=200)
