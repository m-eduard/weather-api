import os

import api_utils
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
            return api_utils.exception_handlers[type(e)](error_message)

        return jsonify({"id": new_temperature.inserted_id}), 201
