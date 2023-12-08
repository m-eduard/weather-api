import datetime as dt
import json
import os

import api_utils
import db_utils
from bson.json_util import dumps
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import (
    Operations,
    api_request_field_mappings,
    api_response_field_mappings,
    api_response_value_mappings,
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
    collection = db.get_collection("temperatures")

    api_temperatures = Blueprint("api_temperatures", __name__)

    @api_temperatures.route("/api/temperatures/", methods=["POST"])
    def post_temperature():
        body = request.get_json(silent=False)

        try:
            if not validators[Operations.POST_TEMPERATURE](body):
                raise api_utils.ValidationError(
                    validation_error(Operations.POST_TEMPERATURE)
                )

            new_temperature = db_utils.insert_if_unique(
                collection,
                body,
                unique_fields[Operations.POST_TEMPERATURE],
                dependencies[Operations.POST_TEMPERATURE],
                timestamp=True,
            )
        except (
            api_utils.ValidationError,
            api_utils.ResourceDependencyError,
            api_utils.DuplicateResourceError,
        ) as e:
            error_message = api_utils.build_error_message(
                Operations.POST_TEMPERATURE, collection.name, body, e
            )
            # Use dumps from BSON first to serialize the ISODate object
            return api_utils.exception_handlers[type(e)](
                json.loads(dumps(error_message))
            )

        return jsonify({"id": new_temperature.inserted_id}), 201

    @api_temperatures.route("/api/temperatures/", methods=["GET"])
    def get_temperatures():
        filter_query = {}

        for param_name, convert_function in api_utils.query_params_handlers[
            "db_filter"
        ][Operations.GET_TEMPERATURES].items():
            param_value = request.args.get(param_name)

            if param_value:
                try:
                    filter_query[param_name] = convert_function(param_value)
                except:
                    # Don't throw an error if the parameter is not valid
                    pass

        # Get all cities located at the given coordinated
        cities = [
            x["_id"]
            for x in collection.database.get_collection("cities").find(filter_query)
        ]

        values = [
            map_fields(
                x,
                api_response_field_mappings[Operations.GET_TEMPERATURES],
                api_response_value_mappings[Operations.GET_TEMPERATURES],
            )
            for x in collection.find({"idOras": {"$in": cities}})
            if api_utils.date_filter(
                x["timestamp"], request.args.get("from"), request.args.get("until")
            )
        ]
        return jsonify(values), 200

    @api_temperatures.route("/api/temperatures/cities/<id>", methods=["GET"])
    def get_temperatures_by_city(id):
        try:
            id = api_utils.check_route_parameters(id=id)["id"]
        except api_utils.BadTypeArgumentError as e:
            error_message = api_utils.build_error_message(
                Operations.GET_TEMPERATURES_BY_CITY, collection.name, None, e
            )
            return api_utils.exception_handlers[type(e)](
                json.loads(dumps(error_message))
            )

        values = [
            map_fields(
                x,
                api_response_field_mappings[Operations.GET_TEMPERATURES],
                api_response_value_mappings[Operations.GET_TEMPERATURES],
            )
            for x in collection.find({"idOras": id})
            if api_utils.date_filter(
                x["timestamp"], request.args.get("from"), request.args.get("until")
            )
        ]
        return jsonify(values), 200

    @api_temperatures.route("/api/temperatures/countries/<id>", methods=["GET"])
    def get_temperatures_by_country(id):
        try:
            id = api_utils.check_route_parameters(id=id)["id"]
        except api_utils.BadTypeArgumentError as e:
            error_message = api_utils.build_error_message(
                Operations.GET_TEMPERATURES_BY_COUNTRY, collection.name, None, e
            )
            return api_utils.exception_handlers[type(e)](
                json.loads(dumps(error_message))
            )

        # Get all cities which are inside the given country
        cities = [
            x["_id"]
            for x in collection.database.get_collection("cities").find({"idTara": id})
        ]

        values = [
            map_fields(
                x,
                api_response_field_mappings[Operations.GET_TEMPERATURES],
                api_response_value_mappings[Operations.GET_TEMPERATURES],
            )
            for x in collection.find({"idOras": {"$in": cities}})
            if api_utils.date_filter(
                x["timestamp"], request.args.get("from"), request.args.get("until")
            )
        ]
        return jsonify(values), 200

    @api_temperatures.route("/api/temperatures/<id>", methods=["PUT"])
    def put_temperature(id):
        body = request.get_json(silent=False)

        try:
            id = api_utils.check_route_parameters(id=id)["id"]

            if not validators[Operations.PUT_TEMPERATURE](body):
                raise api_utils.ValidationError(
                    validation_error(Operations.PUT_TEMPERATURE)
                )
            if body["id"] != id:
                raise api_utils.ValidationError(
                    f"id={body['id']} does not match the id from the url id={id}"
                )

            body = map_fields(
                body, api_request_field_mappings[Operations.PUT_TEMPERATURE]
            )
            updated_temperature = db_utils.update(
                collection,
                {"_id": id},
                body,
                unique_fields[Operations.POST_TEMPERATURE],
                dependencies[Operations.POST_TEMPERATURE],
                timestamp=True,
            )

            if updated_temperature.modified_count == 0:
                if not collection.find_one({"_id": id}):
                    raise api_utils.ResourceNotFoundError(id, collection.name)

        except (
            api_utils.BadTypeArgumentError,
            api_utils.ValidationError,
            api_utils.ResourceNotFoundError,
            api_utils.DuplicateResourceError,
        ) as e:
            error_message = api_utils.build_error_message(
                Operations.PUT_TEMPERATURE, collection.name, body, e
            )
            return api_utils.exception_handlers[type(e)](
                json.loads(dumps(error_message))
            )
        return Response(status=200)

    @api_temperatures.route("/api/temperatures/<id>", methods=["DELETE"])
    def delete_temperature(id):
        try:
            id = api_utils.check_route_parameters(id=id)["id"]

            db_utils.chain_delete(collection, {"_id": id}, delete_chain)

        except (api_utils.BadTypeArgumentError, api_utils.ResourceNotFoundError) as e:
            error_message = api_utils.build_error_message(
                Operations.DELETE_TEMPERATURE, collection.name, None, e
            )
            return api_utils.exception_handlers[type(e)](
                json.loads(dumps(error_message))
            )
        return Response(status=200)
