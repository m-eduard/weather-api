import json
from flask import Flask, Response, jsonify, request

app = Flask(__name__)


class Movie:
    order = 0

    def __init__(self, title, increment=True):
        if increment:
            Movie.order += 1
        self.id = Movie.order
        self.title = title

    def reset_order():
        Movie.order = 0

# movies = {}
# @app.route("/movies", methods=["GET"])
# def get_movies():
#     return jsonify([x.__dict__ for x in movies.values()]), 200


# @app.route("/movies", methods=["POST"])
# def post_movies():
#     payload = request.get_json(silent=True)
#     if not payload or not payload.get("nume", ""):
#         return Response(status=400)

#     movie = Movie(payload["nume"])
#     movies[movie.id] = movie
#     return Response(status=201)


# @app.route("/movie/<int:numar>", methods=["PUT"])
# def put_movie(numar):
#     payload = request.get_json(silent=True)
#     if not payload or not payload.get("nume", ""):
#         return Response(status=400)

#     if numar not in movies:
#         return Response(status=404)

#     movies[numar].title = payload.get("nume")
#     return Response(status=201)


# @app.route("/movie/<int:numar>", methods=["GET"])
# def get_movie(numar):
#     if numar not in movies:
#         return Response(status=404)

#     return jsonify(movies[numar].__dict__), 200


# @app.route("/movie/<int:numar>", methods=["DELETE"])
# def delete_movie(numar):
#     payload = request.get_json(silent=True)
#     if not payload or not payload.get("nume", ""):
#         return Response(status=400)

#     if numar not in movies:
#         return Response(status=404)

#     movies.pop(numar)
#     return Response(200)


# @app.route("/reset", methods=["DELETE"])
# def reset():
#     movies.clear()
#     Movie.reset_order()
#     return Response(200)

@app.route("/home", methods=["GET"])
def home():
    return jsonify({"message": "Hello World!"})

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
