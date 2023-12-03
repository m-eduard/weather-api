import json
import os
import urllib.parse

from flask import Flask, Response, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# Safe encode the special characters from both env variables
username = urllib.parse.quote_plus(os.environ.get("MONGO_INITDB_ROOT_USERNAME"))
password = urllib.parse.quote_plus(os.environ.get("MONGO_INITDB_ROOT_PASSWORD"))

client = MongoClient(
    f'mongodb://{username}:{password}@{os.environ.get("MONGO_HOST")}:{os.environ.get("MONGO_PORT")}/'
)
