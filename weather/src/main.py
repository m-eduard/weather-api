import os
import urllib.parse

from flask import Flask

app = Flask(__name__)

# Safe encode the special characters from both env variables
username = urllib.parse.quote_plus(os.environ.get("MONGO_INITDB_ROOT_USERNAME"))
password = urllib.parse.quote_plus(os.environ.get("MONGO_INITDB_ROOT_PASSWORD"))

app.config[
    "mongo_uri"
] = f'mongodb://{username}:{password}@{os.environ.get("MONGO_HOST")}:{os.environ.get("MONGO_PORT")}/'


with app.app_context():
    from cities import api_cities
    from countries import api_countries

    app.register_blueprint(api_countries)
    app.register_blueprint(api_cities)
