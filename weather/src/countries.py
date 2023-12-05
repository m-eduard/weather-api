import os

import db_utils
from flask import Blueprint, Response, current_app, jsonify, request
from pymongo import MongoClient
from validators import Operations, unique_fields, validation_error, validators

with current_app.app_context():
    mongo_client = MongoClient(current_app.config["mongo_uri"])
    api_countries = Blueprint("api_countries", __name__)

    @api_countries.route("/api/countries/", methods=["POST"])
    def post_country():
        body = request.get_json(silent=False)
        if not validators[Operations.POST_COUNTRY](body):
            return Response(validation_error(Operations.POST_COUNTRY), status=400)

        db = mongo_client[os.environ.get("DB_NAME")]
        collection = db.get_collection("countries")

        try:
            new_country = db_utils.insert_if_unique(
                collection, body, unique_fields[Operations.POST_COUNTRY]
            )

            # Throw an error if a country with the same name already exists
            new_country.inserted_id
        except:
            return Response(f"Adding a new country, {body}, failed in DB", status=409)

        response = jsonify({"id": new_country.inserted_id})
        response.status_code = 201

        return response
