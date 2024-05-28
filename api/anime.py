from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import jwt
from auth_middleware import token_required
from model.animes import Anime  # Import the Message class
from __init__ import app, db

anime_api = Blueprint("anime_api", __name__, url_prefix="/api/anime/")

api = Api(anime_api)


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



class AnimeAPI:
    class _CRUD(Resource):
        @token_required
        def post(self, current_user, Anime):
            body = request.get_json()  # get request

            # user rating and the title
            rating = int(body.get("rating"))
            title = body.get("title")

            # data checking
            if not body and not title:
                return {"rating": "Content is missing"}, 400

            userRating = Anime(uid=current_user.title, _rating=rating)

            try:
                newRating = userRating.create()
                return jsonify(newRating.read()), 201
            except Exception as e:
                return {"rating": f"Failed to create rating: {str(e)}"}, 500

        def get(self):  # Read Method
            messages = Anime.query.all()
            json_ready = [message.read() for message in messages]
            return jsonify(json_ready)

        def put(self, old_message, new_message, likes):
            Anime.update(old_message, new_message, likes)

    class _GetSorted(Resource):
        @token_required
        def post(self, current_user):
            body = request.get_json()
            criteria = body.get("criteria")
            is_reversed = body.get("isReversed", False)

            if criteria not in ["title", "release", "genre", "rating", "userRating"]:
                return jsonify({"message": "Invalid sorting criteria"}), 400

            # Retrieve all anime entries from the database
            animes = Anime.query.all()

            # Convert anime entries to dictionaries
            json_ready = [anime.read() for anime in animes]

            # Sort the anime entries based on the specified criteria
            sorted_animes = sorted(json_ready, key=lambda x: x[criteria])

            # Reverse the list if specified
            if is_reversed:
                sorted_animes.reverse()

            return jsonify(sorted_animes) 


api.add_resource(AnimeAPI._CRUD, "/")
api.add_resource(AnimeAPI._GetSorted, "/getsorted")
