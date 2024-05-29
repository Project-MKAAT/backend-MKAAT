from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import json, jwt
from auth_middleware import token_required
from model.trending import Trending  # Import the Message class
from __init__ import app, db
from model.trending import Trending, db

trending_api = Blueprint("trending_api", __name__, url_prefix="/api/trending/")

api = Api(trending_api)


# quicksort code
def partition(arr, criteria, low, high):
    pivot = arr[high][criteria]
    i = low - 1

    for j in range(low, high):
        if arr[j][criteria] <= pivot:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quickSort(arr, criteria, low, high):
    if low < high:
        pi = partition(arr, criteria, low, high)
        quickSort(arr, criteria, low, pi - 1)
        quickSort(arr, criteria, pi + 1, high)
    return arr


class TrendingAPI:
    class _CRUD(Resource):
        def get(self):  # Read Method
            animes = Trending.query.all()  # read/extract all animes from database
            json_ready = [anime.read() for anime in animes]  # prepare output in json
            return jsonify(json_ready)

    class _UserRating(Resource):
        @token_required
        def post(self, current_user):
            body = request.get_json()
            uid = body.get("uid")
            name = body.get("name")
            rating = body.get("rating")
            animes = Trending.query.all()
            for anime in animes:
                if anime.name == name:
                    anime.userRating = json.loads(anime.userRating)
                    for user_rating in anime.userRating:
                        if uid in user_rating:
                            return {"message": "You have already rated this show."}, 400
                    anime.userRating.append({uid: rating})
                    anime.userRating = json.dumps(anime.userRating)
                    db.session.commit()
                    return {"message": "Rating added successfully"}, 200
            return {"message": "Anime not found"}, 404

    class _GetSorted(Resource):
        def post(self):
            body = request.get_json()
            criteria = body.get("criteria")
            is_reversed = body.get("isReversed")

            if criteria not in ["title", "release", "genre", "rating", "userRating", "popularity"]:
                return jsonify({"message": "Invalid sorting criteria"}), 400

            # Retrieve all anime entries from the database
            animes = Trending.query.all()

            # Convert anime entries to dictionaries
            json_ready = [anime.read() for anime in animes]

            # Ensure that userRating is a float
            if criteria == "userRating":
                sorted_animes = sorted(json_ready, key=lambda x: float(x[criteria]))
            else:
                sorted_animes = sorted(json_ready, key=lambda x: x[criteria])

            # Reverse the list if specified
            if is_reversed is True:
                sorted_animes.reverse()

            return jsonify(sorted_animes)


api.add_resource(TrendingAPI._CRUD, "/")
api.add_resource(TrendingAPI._UserRating, "/userRating")
api.add_resource(TrendingAPI._GetSorted, "/getsorted")
